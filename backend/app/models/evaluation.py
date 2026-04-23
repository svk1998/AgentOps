from datetime import datetime
import enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.dataset import EvalDataset, RagEvalDataset


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


class EvalRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ManualVerdict(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"


class SeverityLevel(str, enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class ManualSessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class EvalRun(UUIDBase):
    __tablename__ = "eval_runs"
    __table_args__ = (
        CheckConstraint(
            "(dataset_id IS NOT NULL AND rag_dataset_id IS NULL) OR "
            "(dataset_id IS NULL AND rag_dataset_id IS NOT NULL)",
            name="chk_eval_runs_one_dataset_type",
        ),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_datasets.id"),
        nullable=True,
        index=True,
    )
    rag_dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_eval_datasets.id"),
        nullable=True,
        index=True,
    )
    status: Mapped[EvalRunStatus] = mapped_column(
        Enum(EvalRunStatus, name="eval_run_status", values_callable=_enum_values),
        default=EvalRunStatus.PENDING,
        nullable=False,
        index=True,
    )
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errored: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    p50_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    p95_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    p99_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    agent_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="eval_runs")
    dataset: Mapped["EvalDataset | None"] = relationship("EvalDataset", back_populates="eval_runs")
    rag_dataset: Mapped["RagEvalDataset | None"] = relationship(
        "RagEvalDataset",
        back_populates="eval_runs",
    )
    results: Mapped[list["EvalRunResult"]] = relationship(
        "EvalRunResult",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="EvalRunResult.item_index",
    )
    manual_sessions: Mapped[list["ManualEvalSession"]] = relationship(
        "ManualEvalSession",
        back_populates="eval_run",
    )


class EvalRunResult(UUIDBase):
    __tablename__ = "eval_run_results"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dataset_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    item_index: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_input: Mapped[dict] = mapped_column(JSONB, nullable=False)
    agent_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    expected_output: Mapped[dict] = mapped_column(JSONB, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    matcher_details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    run: Mapped[EvalRun] = relationship("EvalRun", back_populates="results")
    rag_details: Mapped["RagEvalResultDetail | None"] = relationship(
        "RagEvalResultDetail",
        back_populates="eval_result",
        cascade="all, delete-orphan",
        uselist=False,
    )
    manual_items: Mapped[list["ManualEvalItem"]] = relationship(
        "ManualEvalItem",
        back_populates="eval_result",
    )


class RagEvalResultDetail(UUIDBase):
    __tablename__ = "rag_eval_result_details"

    eval_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_run_results.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    retrieved_chunks: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    retrieval_precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    retrieval_recall: Mapped[float | None] = mapped_column(Float, nullable=True)
    faithfulness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    answer_relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    chunk_attribution: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    eval_result: Mapped[EvalRunResult] = relationship(
        "EvalRunResult",
        back_populates="rag_details",
    )


class ManualEvalSession(UUIDBase):
    __tablename__ = "manual_eval_sessions"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    eval_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_runs.id"),
        nullable=True,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ManualSessionStatus] = mapped_column(
        Enum(ManualSessionStatus, name="manual_session_status", values_callable=_enum_values),
        default=ManualSessionStatus.IN_PROGRESS,
        nullable=False,
        index=True,
    )
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reviewed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assignment_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="manual_sessions")
    eval_run: Mapped[EvalRun | None] = relationship("EvalRun", back_populates="manual_sessions")
    items: Mapped[list["ManualEvalItem"]] = relationship(
        "ManualEvalItem",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ManualEvalItem.item_index",
    )


class ManualEvalItem(UUIDBase):
    __tablename__ = "manual_eval_items"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("manual_eval_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    eval_result_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_run_results.id"),
        nullable=True,
        index=True,
    )
    item_index: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_input: Mapped[dict] = mapped_column(JSONB, nullable=False)
    agent_output: Mapped[dict] = mapped_column(JSONB, nullable=False)
    verdict: Mapped[ManualVerdict | None] = mapped_column(
        Enum(ManualVerdict, name="manual_verdict", values_callable=_enum_values),
        nullable=True,
        index=True,
    )
    field_verdicts: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    severity: Mapped[SeverityLevel | None] = mapped_column(
        Enum(SeverityLevel, name="severity_level", values_callable=_enum_values),
        nullable=True,
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lock_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped[ManualEvalSession] = relationship("ManualEvalSession", back_populates="items")
    eval_result: Mapped[EvalRunResult | None] = relationship(
        "EvalRunResult",
        back_populates="manual_items",
    )


class AuditLog(UUIDBase):
    __tablename__ = "audit_log"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    changes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
