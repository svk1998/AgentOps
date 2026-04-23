import enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.agent import AgentType
from app.models.base import UUIDBase

if TYPE_CHECKING:
    from app.models.evaluation import EvalRun


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


class DatasetItemStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    FLAGGED = "flagged"


class EvalDataset(UUIDBase):
    __tablename__ = "eval_datasets"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_type: Mapped[AgentType | None] = mapped_column(
        Enum(AgentType, name="agent_type", values_callable=_enum_values),
        nullable=True,
        index=True,
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    items: Mapped[list["EvalDatasetItem"]] = relationship(
        "EvalDatasetItem",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="EvalDatasetItem.sort_order",
    )
    versions: Mapped[list["DatasetVersion"]] = relationship(
        "DatasetVersion",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="DatasetVersion.version_number.desc()",
    )
    eval_runs: Mapped[list["EvalRun"]] = relationship("EvalRun", back_populates="dataset")


class EvalDatasetItem(UUIDBase):
    __tablename__ = "eval_dataset_items"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input: Mapped[dict] = mapped_column(JSONB, nullable=False)
    expected_output: Mapped[dict] = mapped_column(JSONB, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    status: Mapped[DatasetItemStatus] = mapped_column(
        Enum(DatasetItemStatus, name="dataset_item_status", values_callable=_enum_values),
        default=DatasetItemStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    dataset: Mapped[EvalDataset] = relationship("EvalDataset", back_populates="items")


class DatasetVersion(UUIDBase):
    __tablename__ = "dataset_versions"
    __table_args__ = (
        UniqueConstraint("dataset_id", "version_number", name="uq_dataset_versions_version"),
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_data: Mapped[list] = mapped_column(JSONB, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    dataset: Mapped[EvalDataset] = relationship("EvalDataset", back_populates="versions")


class RagEvalDataset(UUIDBase):
    __tablename__ = "rag_eval_datasets"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_base_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    items: Mapped[list["RagEvalItem"]] = relationship(
        "RagEvalItem",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="RagEvalItem.created_at",
    )
    eval_runs: Mapped[list["EvalRun"]] = relationship("EvalRun", back_populates="rag_dataset")


class RagEvalItem(UUIDBase):
    __tablename__ = "rag_eval_items"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_eval_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[str] = mapped_column(Text, nullable=False)
    relevant_chunk_ids: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False,
    )
    relevant_passages: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        nullable=False,
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    dataset: Mapped[RagEvalDataset] = relationship("RagEvalDataset", back_populates="items")
