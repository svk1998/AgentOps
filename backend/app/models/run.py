import enum
import uuid

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Run(UUIDBase):
    __tablename__ = "runs"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    triggered_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus), default=RunStatus.PENDING, nullable=False, index=True
    )

    # Input passed to the agent
    input: Mapped[dict] = mapped_column(JSON, default=dict)

    # Final output once completed
    output: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Token usage summary
    usage: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Error message if failed
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    finished_at: Mapped[None] = mapped_column(DateTime(timezone=True), nullable=True)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="runs")  # noqa: F821
    logs: Mapped[list["RunLog"]] = relationship(
        "RunLog", back_populates="run", order_by="RunLog.sequence"
    )


class RunLog(UUIDBase):
    __tablename__ = "run_logs"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), default=LogLevel.INFO, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    # Optional structured data (tool call inputs/outputs, token counts, etc.)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    run: Mapped["Run"] = relationship("Run", back_populates="logs")
