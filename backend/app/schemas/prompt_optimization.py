from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.models.prompt_optimization import OptimizationStatus

# ── Shared camelCase config for all output schemas ──────────────────────────

class _CamelModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )


# ── Input schemas (accept camelCase from the frontend) ──────────────────────

class PromptOptimizationRunCreate(_CamelModel):
    base_prompt: str
    required_output: str
    model: str = "claude-sonnet-4-6"
    max_iterations: int = 5
    score_threshold: int = 80


# ── Output schemas ───────────────────────────────────────────────────────────

class IterationOut(_CamelModel):
    id: UUID
    run_id: UUID
    number: int
    prompt: str
    output: str
    score: int
    feedback: str | None
    is_goal_reached: bool
    created_at: datetime


class PromptOptimizationRunOut(_CamelModel):
    id: UUID
    base_prompt: str
    required_output: str
    model: str
    max_iterations: int
    score_threshold: int
    status: OptimizationStatus
    best_score: int | None
    best_prompt: str | None
    created_by: UUID
    created_at: datetime
    finished_at: datetime | None
    iterations: list[IterationOut] = []


class PromptOptimizationRunList(_CamelModel):
    items: list[PromptOptimizationRunOut]
    total: int
