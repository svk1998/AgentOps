"""
Prompt Optimization loop — delegates each of its three roles (Executor,
Judge, Refiner) to real `Agent` rows seeded by migration 0002 instead of
hardcoded Python strings. The agents' system_prompt and parameters are
editable from the standard agents UI; the optimization run supplies the
`model` at runtime (agent.model is ignored).

Loop per iteration:
  1. Executor  — run the current prompt, get actual output
  2. Judge     — score output vs required_output (0-100) + critique
  3. Refiner   — rewrite the prompt based on the critique

Runs inside an ARQ background worker; logs stream via Redis pub/sub.
Cancelled via a Redis stop-flag set by the REST stop endpoint.
"""
from collections.abc import Callable
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.prompt_optimization import PromptOptimizationRun
from app.services.llm import chat as _chat
from app.services.prompt_optimizer_agents import (
    EXECUTOR_AGENT_ID,
    JUDGE_AGENT_ID,
    REFINER_AGENT_ID,
    load_role_agents,
)


async def _call_role_agent(
    agent: Agent,
    model: str,
    user_message: str,
    **overrides,
) -> tuple[str, dict]:
    """
    Run a single LLM turn using the seeded role agent's system prompt and
    parameters. `model` is supplied by the optimization run and overrides
    whatever is stored on the agent row (which is just a placeholder).
    """
    messages = [
        {"role": "system", "content": agent.system_prompt or ""},
        {"role": "user", "content": user_message},
    ]

    merged_kwargs = {**(agent.parameters or {}), **overrides}
    return await _chat(model, messages, **merged_kwargs)


def _parse_judge_response(raw: str) -> tuple[int, str]:
    """Parse the judge's JSON response, clamping score and falling back gracefully."""
    try:
        parsed = json.loads(raw)
        score = int(parsed.get("score", 0))
        score = max(0, min(100, score))
        feedback = str(parsed.get("feedback", ""))
    except (json.JSONDecodeError, ValueError, KeyError):
        score = 0
        feedback = f"Judge returned unparseable response: {raw[:200]}"
    return score, feedback


def _sum_usage(*usages: dict) -> dict:
    """Aggregate prompt/completion/total token counts across multiple llm calls."""
    return {
        "prompt_tokens":     sum(u.get("prompt_tokens",     0) for u in usages),
        "completion_tokens": sum(u.get("completion_tokens", 0) for u in usages),
        "total_tokens":      sum(u.get("total_tokens",      0) for u in usages),
    }


# ── Main optimization loop ───────────────────────────────────────────────────

async def run_optimization(
    run: PromptOptimizationRun,
    emit: Callable,
    is_stopped: Callable,
    db: AsyncSession,
) -> None:
    """
    Core agent loop. Called from the ARQ worker.

    Args:
        run:        ORM instance with relationships already loaded.
        emit:       async (type, data) — publishes to SSE channel.
        is_stopped: async () -> bool   — returns True when a stop was requested.
        db:         AsyncSession used to load the seeded role agents.
    """
    # Load Executor/Judge/Refiner once per run. Their system prompts and
    # per-call parameters now come from the DB instead of inline strings.
    role_agents = await load_role_agents(db)
    executor: Agent = role_agents[EXECUTOR_AGENT_ID]
    judge:    Agent = role_agents[JUDGE_AGENT_ID]
    refiner:  Agent = role_agents[REFINER_AGENT_ID]

    current_prompt = run.base_prompt
    model = run.model
    best_score = 0
    best_prompt = current_prompt

    for iteration_number in range(1, run.max_iterations + 1):

        if await is_stopped():
            await emit("cancelled", {"message": "Run cancelled by user."})
            return

        await emit("progress", {
            "message": f"Iteration {iteration_number}/{run.max_iterations} — executing prompt…"
        })

        # Step 1: Executor — run the candidate prompt.
        output, exec_usage = await _call_role_agent(executor, model, current_prompt)

        await emit("progress", {
            "message": f"Iteration {iteration_number} — judging output…"
        })

        # Step 2: Judge — score output against the required output.
        judge_input = f"Goal:\n{run.required_output}\n\nOutput:\n{output}"
        judge_raw, judge_usage = await _call_role_agent(judge, model, judge_input)
        score, feedback = _parse_judge_response(judge_raw)
        is_goal_reached = score >= run.score_threshold

        if score > best_score:
            best_score = score
            best_prompt = current_prompt

        # Step 3: Refiner — only runs if we're going around again.
        # Its token usage is attributed to the iteration that *spawned* it
        # (the one whose feedback it consumed), which is the current
        # iteration. This fixes a pre-refactor bug where refine_usage was
        # dropped from the reported total.
        refine_usage: dict = {}
        next_prompt = current_prompt
        if not is_goal_reached and iteration_number < run.max_iterations:
            await emit("progress", {
                "message": f"Iteration {iteration_number} — refining prompt…"
            })
            refine_input = (
                f"Current prompt:\n{current_prompt}\n\n"
                f"Goal:\n{run.required_output}\n\n"
                f"What was wrong / missing in the last output:\n{feedback}"
            )
            next_prompt, refine_usage = await _call_role_agent(
                refiner, model, refine_input
            )

        total_usage = _sum_usage(exec_usage, judge_usage, refine_usage)

        # Emit completed iteration to SSE listeners
        await emit("iteration", {
            "number": iteration_number,
            "prompt": current_prompt,
            "output": output,
            "score": score,
            "feedback": feedback if not is_goal_reached else None,
            "isGoalReached": is_goal_reached,
            "usage": total_usage,
        })

        if is_goal_reached:
            await emit("done", {
                "status": "completed",
                "bestScore": best_score,
                "bestPrompt": best_prompt,
            })
            return

        current_prompt = next_prompt

    # Exhausted all iterations without reaching the goal
    await emit("done", {
        "status": "failed",
        "bestScore": best_score,
        "bestPrompt": best_prompt,
    })


# Re-export UUIDs so existing imports `from app.services.prompt_optimizer import EXECUTOR_AGENT_ID`
# keep working if anyone picks them up. Purely a convenience.
__all__ = [
    "run_optimization",
    "EXECUTOR_AGENT_ID",
    "JUDGE_AGENT_ID",
    "REFINER_AGENT_ID",
]
