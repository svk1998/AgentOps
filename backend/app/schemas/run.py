from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.run import LogLevel, RunStatus


class RunCreate(BaseModel):
    agent_id: UUID
    input: dict = {}


class RunOut(BaseModel):
    id: UUID
    agent_id: UUID
    triggered_by: UUID
    status: RunStatus
    input: dict
    output: dict | None
    usage: dict | None
    error: str | None
    created_at: datetime
    finished_at: datetime | None
    agent_name: str | None = None

    model_config = {"from_attributes": True}


class RunList(BaseModel):
    items: list[RunOut]
    total: int


class RunLogOut(BaseModel):
    id: UUID
    run_id: UUID
    level: LogLevel
    message: str
    sequence: int
    data: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
