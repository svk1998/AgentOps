from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.agent import AgentStatus, AgentType


class AgentBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    agent_type: AgentType
    endpoint_url: str = Field(min_length=1, max_length=2048)
    model_provider: str | None = Field(default=None, max_length=255)
    description: str | None = None
    input_schema: dict = Field(default_factory=dict)
    output_schema: dict = Field(default_factory=dict)
    version: str = Field(default="1.0.0", max_length=50)
    tags: list[str] = Field(default_factory=list)
    owner: str | None = Field(default=None, max_length=255)
    status: AgentStatus = AgentStatus.DRAFT
    auth_config: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)


class AgentCreate(AgentBase):
    change_summary: str | None = "Initial registration"


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    agent_type: AgentType | None = None
    endpoint_url: str | None = Field(default=None, min_length=1, max_length=2048)
    model_provider: str | None = Field(default=None, max_length=255)
    description: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    version: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = None
    owner: str | None = Field(default=None, max_length=255)
    status: AgentStatus | None = None
    auth_config: dict | None = None
    config: dict | None = None
    change_summary: str | None = None


class AgentOut(AgentBase):
    id: UUID
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentVersionOut(BaseModel):
    id: UUID
    agent_id: UUID
    version: str
    snapshot: dict
    change_summary: str | None
    created_by: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
