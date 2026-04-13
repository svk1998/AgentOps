import enum
import uuid

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase


class OptimizationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PromptOptimizationRun(UUIDBase):
    __tablename__ = "prompt_optimization_runs"

    base_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    required_output: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    score_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=80)

    status: Mapped[OptimizationStatus] = mapped_column(
        Enum(OptimizationStatus), default=OptimizationStatus.PENDING, nullable=False, index=True
    )

    best_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    best_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    finished_at: Mapped[None] = mapped_column(DateTime(timezone=True), nullable=True)

    iterations: Mapped[list["PromptOptimizationIteration"]] = relationship(
        "PromptOptimizationIteration",
        back_populates="run",
        order_by="PromptOptimizationIteration.number",
        cascade="all, delete-orphan",
    )


class PromptOptimizationIteration(UUIDBase):
    __tablename__ = "prompt_optimization_iterations"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_optimization_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    output: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_goal_reached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    usage: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    run: Mapped["PromptOptimizationRun"] = relationship(
        "PromptOptimizationRun", back_populates="iterations"
    )
