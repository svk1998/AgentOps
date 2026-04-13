from uuid import UUID

from pydantic import BaseModel


class ToolCreate(BaseModel):
    name: str
    description: str | None = None
    input_schema: dict = {}
    handler: str
    config: dict = {}


class ToolUpdate(BaseModel):
    description: str | None = None
    input_schema: dict | None = None
    is_active: bool | None = None
    config: dict | None = None


class ToolOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    input_schema: dict
    handler: str
    is_active: bool

    model_config = {"from_attributes": True}
