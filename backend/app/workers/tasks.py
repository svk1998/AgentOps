"""
ARQ task definitions.

Each async function here is a background task.
The `enqueue_run` helper pushes a run job onto the Redis queue.
The `enqueue_optimization` helper pushes a prompt-optimizer job.
"""
from datetime import datetime, timezone
import json

import arq
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis
from app.models.prompt_optimization import (
    OptimizationStatus,
    PromptOptimizationIteration,
    PromptOptimizationRun,
)
from app.models.run import Run, RunLog, RunStatus

RUN_LOG_CHANNEL = "run:{run_id}:logs"
OPTIMIZER_CHANNEL = "optimizer:{run_id}"
OPTIMIZER_STOP_KEY = "optimizer:stop:{run_id}"


async def enqueue_run(run_id: str) -> None:
    redis = await get_redis()
    pool = arq.ArqRedis(redis.connection_pool)
    await pool.enqueue_job("execute_run", run_id)


async def enqueue_optimization(run_id: str) -> None:
    redis = await get_redis()
    pool = arq.ArqRedis(redis.connection_pool)
    await pool.enqueue_job("execute_optimization", run_id)


async def _publish_log(
    redis, run_id: str, level: str, message: str, sequence: int, data: dict | None = None
):
    payload = json.dumps({
        "level": level,
        "message": message,
        "sequence": sequence,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    await redis.publish(RUN_LOG_CHANNEL.format(run_id=run_id), payload)


async def execute_run(ctx: dict, run_id: str) -> None:
    """Main task: load the run, execute the agent, stream logs."""
    from app.services.execution import run_agent

    redis = ctx["redis"]

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Run).where(Run.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            return

        run.status = RunStatus.RUNNING
        await db.commit()

        try:
            sequence = 0
            logs_to_save = []

            async def emit(level: str, message: str, data: dict | None = None):
                nonlocal sequence
                await _publish_log(redis, run_id, level, message, sequence, data)
                logs_to_save.append(
                    RunLog(
                        run_id=run.id, level=level, message=message, sequence=sequence, data=data
                    )
                )
                sequence += 1

            output, usage = await run_agent(run, emit)

            run.status = RunStatus.COMPLETED
            run.output = output
            run.usage = usage
            run.finished_at = datetime.now(timezone.utc)

            db.add_all(logs_to_save)
            await db.commit()

            await _publish_log(redis, run_id, "info", "__done__", sequence)

        except Exception as exc:
            run.status = RunStatus.FAILED
            run.error = str(exc)
            run.finished_at = datetime.now(timezone.utc)
            await db.commit()
            await _publish_log(redis, run_id, "error", f"Run failed: {exc}", 0)
            raise


async def execute_optimization(ctx: dict, run_id: str) -> None:
    """Prompt optimization task: iterates Executor → Judge → Refiner until goal or max iterations."""  # noqa: E501
    from app.services.prompt_optimizer import run_optimization

    redis = ctx["redis"]
    channel = OPTIMIZER_CHANNEL.format(run_id=run_id)
    stop_key = OPTIMIZER_STOP_KEY.format(run_id=run_id)

    async def publish(event_type: str, data: dict) -> None:
        payload = json.dumps({"type": event_type, "data": data})
        await redis.publish(channel, payload)

    async def is_stopped() -> bool:
        return bool(await redis.exists(stop_key))

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PromptOptimizationRun)
            .options(selectinload(PromptOptimizationRun.iterations))
            .where(PromptOptimizationRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            return

        run.status = OptimizationStatus.RUNNING
        await db.commit()

        # Iteration objects to flush after the loop
        iterations_to_save: list[PromptOptimizationIteration] = []
        iteration_counter = 0

        # Wrap publish so the service emits "iteration" events and we persist them
        async def emit(event_type: str, data: dict) -> None:
            nonlocal iteration_counter

            if event_type == "iteration":
                iteration_counter += 1
                iteration = PromptOptimizationIteration(
                    run_id=run.id,
                    number=data["number"],
                    prompt=data["prompt"],
                    output=data["output"],
                    score=data["score"],
                    feedback=data.get("feedback"),
                    is_goal_reached=data["isGoalReached"],
                    usage=data.get("usage"),
                )
                iterations_to_save.append(iteration)
                # Include a temporary id placeholder so the frontend can render immediately
                await publish("iteration", {**data, "runId": run_id})

            elif event_type == "done":
                run.status = OptimizationStatus.COMPLETED
                run.best_score = data.get("bestScore")
                run.best_prompt = data.get("bestPrompt")
                run.finished_at = datetime.now(timezone.utc)
                await publish("done", data)

            elif event_type == "cancelled":
                run.status = OptimizationStatus.CANCELLED
                run.finished_at = datetime.now(timezone.utc)
                await publish("cancelled", data)

            else:
                # progress / debug messages
                await publish(event_type, data)

        try:
            await run_optimization(run, emit, is_stopped, db)
            db.add_all(iterations_to_save)
            await db.commit()

        except Exception as exc:
            run.status = OptimizationStatus.FAILED
            run.finished_at = datetime.now(timezone.utc)
            db.add_all(iterations_to_save)
            await db.commit()
            await publish("error", {"message": str(exc)})
            raise

        finally:
            # Clean up the stop flag if it was set
            await redis.delete(stop_key)


class WorkerSettings:
    functions = [execute_run, execute_optimization]
    redis_settings = arq.connections.RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
