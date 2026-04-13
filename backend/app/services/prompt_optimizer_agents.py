"""
Fixed UUIDs for the three Agent rows that back the Prompt Optimizer loop.

The Executor, Judge, and Refiner used to be hardcoded Python functions with
inline system prompts inside `app/services/prompt_optimizer.py`. They are now
real `Agent` rows — seeded by the `0002_seed_prompt_optimizer_agents` Alembic
migration — so their system prompts and parameters (e.g. judge temperature)
are editable from the same UI as any other agent.

These UUIDs are deterministic so:
  - the migration can insert them with known IDs,
  - the runtime loader can fetch them without a name lookup,
  - tests can seed them directly without running Alembic.

IMPORTANT: do not change these UUIDs. They are referenced by existing rows.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select

from app.models.agent import Agent

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

EXECUTOR_AGENT_ID = UUID("11111111-1111-4111-8111-111111111101")
JUDGE_AGENT_ID    = UUID("11111111-1111-4111-8111-111111111102")
REFINER_AGENT_ID  = UUID("11111111-1111-4111-8111-111111111103")

ROLE_AGENT_IDS = (EXECUTOR_AGENT_ID, JUDGE_AGENT_ID, REFINER_AGENT_ID)


# ── Seed content ─────────────────────────────────────────────────────────────
# These are the system prompts that used to be hardcoded in
# `app/services/prompt_optimizer.py`. The migration reads them from here so
# that a single constant definition drives both DB seed and any test seed.

EXECUTOR_SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Execute the user's prompt faithfully and return the result."
)

JUDGE_SYSTEM_PROMPT = (
    "You are an expert evaluator. "
    "Given an AI-generated output and a goal description, "
    "rate how well the output achieves the goal on a scale of 0 to 100. "
    "Respond with valid JSON only, no markdown fences:\n"
    '{"score": <integer 0-100>, '
    '"feedback": "<concise critique of what is missing or wrong>"}'
)

REFINER_SYSTEM_PROMPT = (
    "You are an expert prompt engineer. "
    "Rewrite the given prompt so that an AI assistant is more likely "
    "to produce output that satisfies the stated goal. "
    "Output only the improved prompt — no explanation, no preamble."
)


class PromptOptimizerAgentsMissingError(RuntimeError):
    """Raised when one or more of the seeded role agents is not in the DB."""


async def load_role_agents(db: AsyncSession) -> dict[UUID, Agent]:
    """
    Fetch the three role agents in a single query.

    Returns a dict keyed by their fixed UUID so callers can do:
        agents = await load_role_agents(db)
        executor = agents[EXECUTOR_AGENT_ID]

    Raises `PromptOptimizerAgentsMissingError` if any row is missing — which
    means the seed migration wasn't run, or the rows were manually deleted.
    """
    result = await db.execute(select(Agent).where(Agent.id.in_(ROLE_AGENT_IDS)))
    by_id = {a.id: a for a in result.scalars().all()}

    missing = [str(u) for u in ROLE_AGENT_IDS if u not in by_id]
    if missing:
        raise PromptOptimizerAgentsMissingError(
            "Prompt optimizer role agents missing from the DB: "
            f"{missing}. Run `alembic upgrade head` to seed them."
        )

    return by_id
