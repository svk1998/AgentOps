"""seed agent rows backing the Prompt Optimizer loop

Creates a locked system user (if not already present) and three `agents`
rows — Executor, Judge, Refiner — whose system prompts and parameters used
to be hardcoded in `app/services/prompt_optimizer.py`. The optimizer loop
now loads these rows at runtime so the prompts are editable from the UI.

The three agent UUIDs are fixed and live in
`app/services/prompt_optimizer_agents.py` — do not change them.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-11

"""
from uuid import UUID

from alembic import op
import sqlalchemy as sa

from app.services.prompt_optimizer_agents import (
    EXECUTOR_AGENT_ID,
    EXECUTOR_SYSTEM_PROMPT,
    JUDGE_AGENT_ID,
    JUDGE_SYSTEM_PROMPT,
    REFINER_AGENT_ID,
    REFINER_SYSTEM_PROMPT,
)

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


# A fixed, locked system user that owns the three seeded agents. Kept
# inside the migration so the seed is self-contained and deterministic.
# `hashed_password = "!"` is a conventional locked-account sentinel — the
# passlib verify path will reject any login attempt against it.
SYSTEM_USER_ID = UUID("11111111-1111-4111-8111-111111111100")
SYSTEM_USER_EMAIL = "prompt-optimizer@system.agentops.local"


def upgrade() -> None:
    bind = op.get_bind()

    # ── Ensure a system user exists for the created_by FK ────────────────────
    existing = bind.execute(
        sa.text("SELECT id FROM users WHERE id = :id"),
        {"id": str(SYSTEM_USER_ID)},
    ).first()

    if existing is None:
        bind.execute(
            sa.text(
                """
                INSERT INTO users (id, email, hashed_password, full_name,
                                   is_active, is_superuser)
                VALUES (:id, :email, :pw, :name, false, false)
                """
            ),
            {
                "id": str(SYSTEM_USER_ID),
                "email": SYSTEM_USER_EMAIL,
                "pw": "!",  # locked — no valid bcrypt hash, login impossible
                "name": "Prompt Optimizer (system)",
            },
        )

    # ── Seed the three role agents ───────────────────────────────────────────
    agents = [
        {
            "id": str(EXECUTOR_AGENT_ID),
            "name": "Prompt Optimizer · Executor",
            "description": (
                "Runs the candidate prompt inside the Prompt Optimizer loop "
                "and returns the raw output. Edit this agent's system prompt "
                "to change how the Executor step behaves."
            ),
            "system_prompt": EXECUTOR_SYSTEM_PROMPT,
            "parameters": "{}",
        },
        {
            "id": str(JUDGE_AGENT_ID),
            "name": "Prompt Optimizer · Judge",
            "description": (
                "Scores executor output against the goal (0-100) and returns "
                "JSON critique. Used by the Prompt Optimizer loop. "
                "Temperature is kept low for consistent scoring."
            ),
            "system_prompt": JUDGE_SYSTEM_PROMPT,
            "parameters": '{"temperature": 0.2}',
        },
        {
            "id": str(REFINER_AGENT_ID),
            "name": "Prompt Optimizer · Refiner",
            "description": (
                "Rewrites the candidate prompt given judge feedback. "
                "Used by the Prompt Optimizer loop."
            ),
            "system_prompt": REFINER_SYSTEM_PROMPT,
            "parameters": "{}",
        },
    ]

    for a in agents:
        bind.execute(
            sa.text(
                """
                INSERT INTO agents (id, name, description, model,
                                    system_prompt, tool_ids, parameters,
                                    created_by)
                VALUES (:id, :name, :description, :model,
                        :system_prompt, :tool_ids, CAST(:parameters AS jsonb),
                        :created_by)
                """
            ),
            {
                **a,
                # model is NOT NULL — the optimization run supplies the real
                # model at runtime, so we stash a placeholder here. The
                # loader ignores agent.model.
                "model": "__runtime_override__",
                "tool_ids": "[]",
                "created_by": str(SYSTEM_USER_ID),
            },
        )


def downgrade() -> None:
    bind = op.get_bind()

    bind.execute(
        sa.text("DELETE FROM agents WHERE id IN (:a, :b, :c)"),
        {
            "a": str(EXECUTOR_AGENT_ID),
            "b": str(JUDGE_AGENT_ID),
            "c": str(REFINER_AGENT_ID),
        },
    )

    # Only remove the system user if we created it and nothing else
    # depends on it. Safe because the only FKs pointing at it are the
    # three agents we just deleted.
    bind.execute(
        sa.text("DELETE FROM users WHERE id = :id"),
        {"id": str(SYSTEM_USER_ID)},
    )
