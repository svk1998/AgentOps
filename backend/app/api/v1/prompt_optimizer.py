import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import decode_access_token
from app.models.prompt_optimization import OptimizationStatus, PromptOptimizationRun
from app.models.user import User
from app.schemas.prompt_optimization import (
    PromptOptimizationRunCreate,
    PromptOptimizationRunList,
    PromptOptimizationRunOut,
)
from app.workers.tasks import enqueue_optimization

router = APIRouter(prefix="/prompt-optimizer", tags=["prompt-optimizer"])

OPTIMIZER_CHANNEL = "optimizer:{run_id}"
OPTIMIZER_STOP_KEY = "optimizer:stop:{run_id}"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _run_with_iterations(query):
    return query.options(
        selectinload(PromptOptimizationRun.iterations)
    )


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/runs", response_model=PromptOptimizationRunList, response_model_by_alias=True)
async def list_runs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _run_with_iterations(
        select(PromptOptimizationRun)
        .where(PromptOptimizationRun.created_by == current_user.id)
        .order_by(PromptOptimizationRun.created_at.desc())
    )
    result = await db.execute(query)
    runs = result.scalars().all()
    return PromptOptimizationRunList(items=runs, total=len(runs))


@router.post(
    "/runs",
    response_model=PromptOptimizationRunOut,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_run(
    payload: PromptOptimizationRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = PromptOptimizationRun(
        base_prompt=payload.base_prompt,
        required_output=payload.required_output,
        model=payload.model,
        max_iterations=payload.max_iterations,
        score_threshold=payload.score_threshold,
        created_by=current_user.id,
        status=OptimizationStatus.PENDING,
    )
    db.add(run)
    await db.flush()
    await db.refresh(run)

    await enqueue_optimization(str(run.id))
    return run


@router.get("/runs/{run_id}", response_model=PromptOptimizationRunOut, response_model_by_alias=True)
async def get_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        _run_with_iterations(
            select(PromptOptimizationRun).where(PromptOptimizationRun.id == run_id)
        )
    )
    run = result.scalar_one_or_none()
    if not run or run.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post(
    "/runs/{run_id}/stop",
    response_model=PromptOptimizationRunOut,
    response_model_by_alias=True,
)
async def stop_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        _run_with_iterations(
            select(PromptOptimizationRun).where(PromptOptimizationRun.id == run_id)
        )
    )
    run = result.scalar_one_or_none()
    if not run or run.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status not in (OptimizationStatus.PENDING, OptimizationStatus.RUNNING):
        raise HTTPException(status_code=400, detail="Run is not stoppable")

    # Set the Redis stop flag — the worker checks this between iterations
    redis = await get_redis()
    await redis.set(OPTIMIZER_STOP_KEY.format(run_id=run_id), "1", ex=300)

    return run


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PromptOptimizationRun).where(PromptOptimizationRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run or run.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    await db.delete(run)


@router.get("/runs/{run_id}/stream")
async def stream_run(
    run_id: UUID,
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Server-Sent Events endpoint for live iteration updates.

    Auth is via `?token=<bearer>` because the browser EventSource API
    cannot send custom headers.
    """
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Verify the run belongs to this user
    result = await db.execute(
        select(PromptOptimizationRun).where(PromptOptimizationRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run or str(run.created_by) != user_id:
        raise HTTPException(status_code=404, detail="Run not found")

    redis = await get_redis()
    channel = OPTIMIZER_CHANNEL.format(run_id=run_id)

    async def event_generator():
        async with redis.pubsub() as pubsub:
            await pubsub.subscribe(channel)
            try:
                while True:
                    if await request.is_disconnected():
                        break
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=1.0
                    )
                    if message:
                        yield f"data: {message['data']}\n\n"
                        # Close the stream when the worker signals completion/stop
                        try:
                            payload = json.loads(message["data"])
                            if payload.get("type") in ("done", "cancelled"):
                                break
                        except (json.JSONDecodeError, KeyError):
                            pass
                    else:
                        yield ": ping\n\n"
                    await asyncio.sleep(0.05)
            finally:
                await pubsub.unsubscribe(channel)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
