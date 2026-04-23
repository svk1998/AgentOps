import enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.evaluation import EvalRun, ManualEvalSession


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


class AgentType(str, enum.Enum):
    LLM = "llm"
    RAG = "rag"
    VISION = "vision"
    MULTI_STEP_CHAIN = "multi_step_chain"
    TOOL_USE = "tool_use"
    CUSTOM = "custom"


class AgentStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class Agent(UUIDBase):
    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    agent_type: Mapped[AgentType] = mapped_column(
        Enum(AgentType, name="agent_type", values_callable=_enum_values),
        nullable=False,
        index=True,
    )
    endpoint_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    model_provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_schema: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    output_schema: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus, name="agent_status", values_callable=_enum_values),
        default=AgentStatus.DRAFT,
        nullable=False,
        index=True,
    )
    auth_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    versions: Mapped[list["AgentVersion"]] = relationship(
        "AgentVersion",
        back_populates="agent",
        cascade="all, delete-orphan",
        order_by="AgentVersion.created_at.desc()",
    )
    eval_runs: Mapped[list["EvalRun"]] = relationship("EvalRun", back_populates="agent")
    manual_sessions: Mapped[list["ManualEvalSession"]] = relationship(
        "ManualEvalSession",
        back_populates="agent",
    )


class AgentVersion(UUIDBase):
    __tablename__ = "agent_versions"
    __table_args__ = (
        UniqueConstraint("agent_id", "version", name="uq_agent_versions_agent_version"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    agent: Mapped[Agent] = relationship("Agent", back_populates="versions")
