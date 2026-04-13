from uuid import UUID

from pydantic import BaseModel


class PipelineCreate(BaseModel):
    name: str
    description: str | None = None
    definition: dict = {}


class PipelineUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    definition: dict | None = None
    is_active: bool | None = None


class PipelineOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    definition: dict
    is_active: bool
    created_by: UUID

    model_config = {"from_attributes": True}
