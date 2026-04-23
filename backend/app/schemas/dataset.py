from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.agent import AgentType
from app.models.dataset import DatasetItemStatus


class EvalDatasetItemBase(BaseModel):
    input: dict[str, Any]
    expected_output: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: DatasetItemStatus = DatasetItemStatus.ACTIVE
    sort_order: int = 0


class EvalDatasetItemCreate(EvalDatasetItemBase):
    pass


class EvalDatasetItemUpdate(BaseModel):
    input: dict[str, Any] | None = None
    expected_output: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    status: DatasetItemStatus | None = None
    sort_order: int | None = None


class EvalDatasetItemOut(BaseModel):
    id: UUID
    dataset_id: UUID
    input: dict[str, Any]
    expected_output: dict[str, Any]
    metadata: dict[str, Any] = Field(validation_alias="metadata_")
    status: DatasetItemStatus
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class EvalDatasetBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    agent_type: AgentType | None = None
    tags: list[str] = Field(default_factory=list)


class EvalDatasetCreate(EvalDatasetBase):
    items: list[EvalDatasetItemCreate] = Field(default_factory=list)


class EvalDatasetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    agent_type: AgentType | None = None
    tags: list[str] | None = None


class EvalDatasetOut(EvalDatasetBase):
    id: UUID
    item_count: int
    current_version: int
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvalDatasetDetail(EvalDatasetOut):
    items: list[EvalDatasetItemOut] = Field(default_factory=list)


class DatasetVersionOut(BaseModel):
    id: UUID
    dataset_id: UUID
    version_number: int
    item_count: int
    snapshot_data: list[Any]
    notes: str | None
    created_by: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetSnapshotCreate(BaseModel):
    notes: str | None = None


class BulkDatasetItemsCreate(BaseModel):
    items: list[EvalDatasetItemCreate]


class RagEvalItemBase(BaseModel):
    query: str = Field(min_length=1)
    expected_answer: str = Field(min_length=1)
    relevant_chunk_ids: list[str] = Field(default_factory=list)
    relevant_passages: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagEvalItemCreate(RagEvalItemBase):
    pass


class RagEvalItemOut(BaseModel):
    id: UUID
    dataset_id: UUID
    query: str
    expected_answer: str
    relevant_chunk_ids: list[str]
    relevant_passages: list[str]
    metadata: dict[str, Any] = Field(validation_alias="metadata_")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RagEvalDatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    knowledge_base_ref: str | None = Field(default=None, max_length=512)
    tags: list[str] = Field(default_factory=list)
    items: list[RagEvalItemCreate] = Field(default_factory=list)


class RagEvalDatasetOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    knowledge_base_ref: str | None
    tags: list[str]
    item_count: int
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RagEvalDatasetDetail(RagEvalDatasetOut):
    items: list[RagEvalItemOut] = Field(default_factory=list)


class RagKnowledgeBaseSync(BaseModel):
    knowledge_base_ref: str | None = Field(default=None, max_length=512)
    items: list[RagEvalItemCreate] = Field(default_factory=list)
