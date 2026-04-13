from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AgentCreate(BaseModel):
    name: str
    description: str | None = None
    model: str
    system_prompt: str | None = None
    tool_ids: list[UUID] = []
    parameters: dict = {}


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    tool_ids: list[UUID] | None = None
    parameters: dict | None = None


class AgentOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    model: str
    system_prompt: str | None
    tool_ids: list[UUID]
    parameters: dict
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentWithStats(AgentOut):
    run_count: int = 0
    last_run_at: datetime | None = None
    last_run_status: str | None = None
