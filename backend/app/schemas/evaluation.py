from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.evaluation import (
    EvalRunStatus,
    ManualSessionStatus,
    ManualVerdict,
    SeverityLevel,
)


class EvalRunCreate(BaseModel):
    agent_id: UUID
    dataset_id: UUID | None = None
    rag_dataset_id: UUID | None = None
    config: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_exactly_one_dataset(self):
        if bool(self.dataset_id) == bool(self.rag_dataset_id):
            raise ValueError("Provide exactly one of dataset_id or rag_dataset_id")
        return self


class EvalRunOut(BaseModel):
    id: UUID
    agent_id: UUID
    dataset_id: UUID | None
    rag_dataset_id: UUID | None
    status: EvalRunStatus
    config: dict[str, Any]
    total_items: int
    passed: int
    failed: int
    errored: int
    avg_latency_ms: float | None
    avg_score: float | None
    p50_latency_ms: float | None
    p95_latency_ms: float | None
    p99_latency_ms: float | None
    total_cost_usd: float | None
    agent_version: str | None
    triggered_by: UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvalRunResultCreate(BaseModel):
    dataset_item_id: UUID | None = None
    item_index: int
    agent_input: dict[str, Any]
    agent_output: dict[str, Any] | None = None
    expected_output: dict[str, Any]
    score: float | None = Field(default=None, ge=0, le=1)
    passed: bool | None = None
    latency_ms: int | None = None
    status_code: int | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    estimated_cost_usd: float | None = None
    matcher_details: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    raw_response: dict[str, Any] | None = None


class RagEvalResultDetailOut(BaseModel):
    id: UUID
    eval_result_id: UUID
    retrieved_chunks: list[Any]
    retrieval_precision: float | None
    retrieval_recall: float | None
    faithfulness_score: float | None
    answer_relevance_score: float | None
    chunk_attribution: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvalRunResultOut(BaseModel):
    id: UUID
    run_id: UUID
    dataset_item_id: UUID | None
    item_index: int
    agent_input: dict[str, Any]
    agent_output: dict[str, Any] | None
    expected_output: dict[str, Any]
    score: float | None
    passed: bool | None
    latency_ms: int | None
    status_code: int | None
    tokens_in: int | None
    tokens_out: int | None
    estimated_cost_usd: float | None
    matcher_details: dict[str, Any]
    error: str | None
    raw_response: dict[str, Any] | None
    created_at: datetime
    rag_details: RagEvalResultDetailOut | None = None

    model_config = ConfigDict(from_attributes=True)


class EvalRunResultsPage(BaseModel):
    items: list[EvalRunResultOut]
    total: int


class ManualEvalItemCreate(BaseModel):
    eval_result_id: UUID | None = None
    item_index: int
    agent_input: dict[str, Any]
    agent_output: dict[str, Any]
    assigned_to: UUID | None = None


class ManualEvalSessionCreate(BaseModel):
    agent_id: UUID
    eval_run_id: UUID | None = None
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    assignment_config: dict[str, Any] = Field(default_factory=dict)
    items: list[ManualEvalItemCreate] = Field(default_factory=list)


class ManualEvalItemOut(BaseModel):
    id: UUID
    session_id: UUID
    eval_result_id: UUID | None
    item_index: int
    agent_input: dict[str, Any]
    agent_output: dict[str, Any]
    verdict: ManualVerdict | None
    field_verdicts: dict[str, Any] | None
    severity: SeverityLevel | None
    reviewer_notes: str | None
    corrected_output: dict[str, Any] | None
    reviewer_id: UUID | None
    assigned_to: UUID | None
    is_reviewed: bool
    reviewed_at: datetime | None
    review_duration_ms: int | None
    lock_version: int
    locked_by: UUID | None
    locked_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManualEvalSessionOut(BaseModel):
    id: UUID
    agent_id: UUID
    eval_run_id: UUID | None
    name: str | None
    description: str | None
    status: ManualSessionStatus
    total_items: int
    reviewed_count: int
    assignment_config: dict[str, Any]
    created_by: UUID | None
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ManualEvalSessionDetail(ManualEvalSessionOut):
    items: list[ManualEvalItemOut] = Field(default_factory=list)


class ManualReviewSubmit(BaseModel):
    verdict: ManualVerdict
    field_verdicts: dict[str, Any] = Field(default_factory=dict)
    severity: SeverityLevel | None = None
    reviewer_notes: str | None = None
    corrected_output: dict[str, Any] | None = None
    review_duration_ms: int | None = None
    lock_version: int | None = None


class AccuracyTrendPoint(BaseModel):
    run_id: UUID
    run_date: datetime
    agent_version: str | None
    total_items: int
    passed: int
    failed: int
    errored: int
    pass_rate_pct: float
    avg_latency_ms: float | None
    p95_latency_ms: float | None
    total_cost_usd: float | None


class FieldAccuracyPoint(BaseModel):
    run_id: UUID
    agent_version: str | None
    field: str
    total: int
    matched: int
    accuracy_pct: float


class LatencySummary(BaseModel):
    run_id: UUID
    p50_latency_ms: float | None
    p95_latency_ms: float | None
    p99_latency_ms: float | None
    avg_latency_ms: float | None


class RegressionPoint(BaseModel):
    current_run: UUID
    current_version: str | None
    current_pass_rate: float
    previous_run: UUID | None
    previous_version: str | None
    previous_pass_rate: float | None
    pass_rate_delta: float | None
    is_regression: bool
