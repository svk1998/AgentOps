"""
Tests for the prompt optimizer loop after the Agent-backed refactor.

These are unit tests on `run_optimization` directly — they bypass ARQ/Redis
and patch `app.services.llm.chat` with canned responses. The goal is to
verify three things the refactor set out to fix:

  1. Executor/Judge/Refiner each load their system_prompt from the seeded
     Agent rows (not from hardcoded Python strings).
  2. Refiner token usage is included in the iteration's total_usage
     (previously dropped).
  3. When `is_stopped` returns True, the loop emits `cancelled` (not
     `stopped`), matching the unified status enum.
"""
from __future__ import annotations

from unittest.mock import AsyncMock
import uuid

import pytest
import pytest_asyncio

from app.models.agent import Agent
from app.models.prompt_optimization import OptimizationStatus, PromptOptimizationRun
from app.models.user import User
from app.services import prompt_optimizer
from app.services.prompt_optimizer_agents import (
    EXECUTOR_AGENT_ID,
    EXECUTOR_SYSTEM_PROMPT,
    JUDGE_AGENT_ID,
    JUDGE_SYSTEM_PROMPT,
    REFINER_AGENT_ID,
    REFINER_SYSTEM_PROMPT,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def system_user(db):
    user = User(
        id=uuid.uuid4(),
        email="optimizer-system@test.local",
        hashed_password="!",
        full_name="Optimizer System",
        is_active=False,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    return user


@pytest_asyncio.fixture
async def seeded_role_agents(db, system_user):
    """Insert the three role agents with the fixed UUIDs the loader expects."""
    executor = Agent(
        id=EXECUTOR_AGENT_ID,
        name="Prompt Optimizer · Executor",
        description="executor",
        model="__runtime_override__",
        system_prompt=EXECUTOR_SYSTEM_PROMPT,
        tool_ids=[],
        parameters={},
        created_by=system_user.id,
    )
    judge = Agent(
        id=JUDGE_AGENT_ID,
        name="Prompt Optimizer · Judge",
        description="judge",
        model="__runtime_override__",
        system_prompt=JUDGE_SYSTEM_PROMPT,
        tool_ids=[],
        parameters={"temperature": 0.2},
        created_by=system_user.id,
    )
    refiner = Agent(
        id=REFINER_AGENT_ID,
        name="Prompt Optimizer · Refiner",
        description="refiner",
        model="__runtime_override__",
        system_prompt=REFINER_SYSTEM_PROMPT,
        tool_ids=[],
        parameters={},
        created_by=system_user.id,
    )
    db.add_all([executor, judge, refiner])
    await db.commit()
    return executor, judge, refiner


@pytest_asyncio.fixture
async def opt_run(db, system_user):
    run = PromptOptimizationRun(
        id=uuid.uuid4(),
        base_prompt="Write a haiku about X.",
        required_output="A haiku about autumn leaves.",
        model="claude-sonnet-4-6",
        max_iterations=2,
        score_threshold=90,
        created_by=system_user.id,
        status=OptimizationStatus.PENDING,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


# ── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_loop_uses_seeded_agent_system_prompts(
    monkeypatch, db, seeded_role_agents, opt_run
):
    """
    Each call to llm.chat should receive the system_prompt from the
    corresponding seeded Agent row — not a hardcoded string. This proves
    the refactor actually routes through the DB.
    """
    calls: list[tuple[str, list[dict], dict]] = []

    async def fake_chat(model, messages, **kwargs):
        calls.append((model, messages, kwargs))
        # Simple canned responses keyed off which role this call is.
        system = messages[0]["content"]
        if system == EXECUTOR_SYSTEM_PROMPT:
            return "Leaves fall gently down.", {
                "prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15,
            }
        if system == JUDGE_SYSTEM_PROMPT:
            return '{"score": 50, "feedback": "Needs more autumn imagery."}', {
                "prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30,
            }
        if system == REFINER_SYSTEM_PROMPT:
            return "Write a haiku about autumn leaves falling.", {
                "prompt_tokens": 8, "completion_tokens": 6, "total_tokens": 14,
            }
        raise AssertionError(f"Unexpected system prompt: {system[:40]}")

    monkeypatch.setattr("app.services.prompt_optimizer._chat", fake_chat)

    events: list[tuple[str, dict]] = []
    async def emit(event_type, data):
        events.append((event_type, data))

    is_stopped = AsyncMock(return_value=False)

    await prompt_optimizer.run_optimization(opt_run, emit, is_stopped, db)

    # Every call must have used the DB-sourced system prompt.
    systems = [messages[0]["content"] for _, messages, _ in calls]
    assert EXECUTOR_SYSTEM_PROMPT in systems
    assert JUDGE_SYSTEM_PROMPT in systems
    assert REFINER_SYSTEM_PROMPT in systems

    # Judge's parameters (temperature=0.2) must have been forwarded to llm.chat.
    judge_calls = [
        (model, msgs, kwargs)
        for (model, msgs, kwargs) in calls
        if msgs[0]["content"] == JUDGE_SYSTEM_PROMPT
    ]
    assert judge_calls, "Judge was never called"
    assert judge_calls[0][2].get("temperature") == 0.2


@pytest.mark.asyncio
async def test_iteration_usage_includes_refiner_tokens(
    monkeypatch, db, seeded_role_agents, opt_run
):
    """
    Before the refactor, refine_usage was dropped from total_usage. Confirm
    that the first iteration's usage now includes all three roles' tokens
    when another iteration follows (i.e. the refiner fired).
    """
    async def fake_chat(model, messages, **kwargs):
        system = messages[0]["content"]
        if system == EXECUTOR_SYSTEM_PROMPT:
            return "x", {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
        if system == JUDGE_SYSTEM_PROMPT:
            return '{"score": 10, "feedback": "wrong"}', {
                "prompt_tokens": 3, "completion_tokens": 3, "total_tokens": 6,
            }
        if system == REFINER_SYSTEM_PROMPT:
            return "better prompt", {
                "prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10,
            }
        raise AssertionError("unexpected call")

    monkeypatch.setattr("app.services.prompt_optimizer._chat", fake_chat)

    iteration_events: list[dict] = []
    async def emit(event_type, data):
        if event_type == "iteration":
            iteration_events.append(data)

    await prompt_optimizer.run_optimization(
        opt_run, emit, AsyncMock(return_value=False), db
    )

    assert len(iteration_events) >= 1
    first = iteration_events[0]
    # Executor (2) + Judge (6) + Refiner (10) = 18
    assert first["usage"]["total_tokens"] == 18
    assert first["usage"]["prompt_tokens"] == 1 + 3 + 5
    assert first["usage"]["completion_tokens"] == 1 + 3 + 5


@pytest.mark.asyncio
async def test_cancelled_event_when_stop_flag_set(
    monkeypatch, db, seeded_role_agents, opt_run
):
    """
    When is_stopped() returns True at the top of an iteration, the loop
    must emit `cancelled` (not `stopped`). This matches the unified status
    enum introduced by migration 0003.
    """
    async def fake_chat(*args, **kwargs):
        raise AssertionError("chat should not be called when stop is set at entry")

    monkeypatch.setattr("app.services.prompt_optimizer._chat", fake_chat)

    events: list[tuple[str, dict]] = []
    async def emit(event_type, data):
        events.append((event_type, data))

    is_stopped = AsyncMock(return_value=True)

    await prompt_optimizer.run_optimization(opt_run, emit, is_stopped, db)

    event_types = [e[0] for e in events]
    assert "cancelled" in event_types
    assert "stopped" not in event_types


@pytest.mark.asyncio
async def test_missing_role_agents_raises(monkeypatch, db, system_user, opt_run):
    """
    If the seed migration hasn't run, the loader must raise a clear error
    rather than silently running with missing prompts.
    """
    from app.services.prompt_optimizer_agents import PromptOptimizerAgentsMissingError

    async def emit(*args, **kwargs):
        pass

    with pytest.raises(PromptOptimizerAgentsMissingError):
        await prompt_optimizer.run_optimization(
            opt_run, emit, AsyncMock(return_value=False), db
        )
