from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.agent import Agent, AgentStatus, AgentType, AgentVersion
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentOut, AgentUpdate, AgentVersionOut

router = APIRouter(prefix="/agents", tags=["agents"])


def _agent_snapshot(agent: Agent) -> dict:
    return {
        "id": str(agent.id),
        "name": agent.name,
        "agent_type": agent.agent_type.value,
        "endpoint_url": agent.endpoint_url,
        "model_provider": agent.model_provider,
        "description": agent.description,
        "input_schema": agent.input_schema,
        "output_schema": agent.output_schema,
        "version": agent.version,
        "tags": agent.tags,
        "owner": agent.owner,
        "status": agent.status.value,
        "auth_config": agent.auth_config,
        "config": agent.config,
        "created_by": str(agent.created_by) if agent.created_by else None,
    }


async def _create_version_snapshot(
    db: AsyncSession,
    agent: Agent,
    user_id: UUID | None,
    change_summary: str | None,
) -> None:
    existing = await db.execute(
        select(AgentVersion).where(
            AgentVersion.agent_id == agent.id,
            AgentVersion.version == agent.version,
        )
    )
    if existing.scalar_one_or_none():
        return

    db.add(
        AgentVersion(
            agent_id=agent.id,
            version=agent.version,
            snapshot=_agent_snapshot(agent),
            change_summary=change_summary,
            created_by=user_id,
        )
    )


@router.get("", response_model=list[AgentOut])
async def list_agents(
    search: str | None = None,
    agent_type: AgentType | None = None,
    agent_status: AgentStatus | None = Query(None, alias="status"),
    tag: str | None = None,
    include_archived: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Agent).order_by(Agent.created_at.desc())

    if search:
        pattern = f"%{search}%"
        query = query.where(Agent.name.ilike(pattern) | Agent.description.ilike(pattern))
    if agent_type:
        query = query.where(Agent.agent_type == agent_type)
    if agent_status:
        query = query.where(Agent.status == agent_status)
    elif not include_archived:
        query = query.where(Agent.status != AgentStatus.ARCHIVED)
    if tag:
        query = query.where(Agent.tags.contains([tag]))

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    values = payload.model_dump(exclude={"change_summary"})
    agent = Agent(**values, created_by=current_user.id)
    db.add(agent)
    await db.flush()
    await _create_version_snapshot(db, agent, current_user.id, payload.change_summary)
    return agent


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentOut)
@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: UUID,
    payload: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    values = payload.model_dump(exclude_none=True, exclude={"change_summary"})
    for field, value in values.items():
        setattr(agent, field, value)

    await db.flush()
    await _create_version_snapshot(db, agent, current_user.id, payload.change_summary)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.status = AgentStatus.ARCHIVED
    await db.flush()
    await _create_version_snapshot(db, agent, current_user.id, "Archived agent")


@router.get("/{agent_id}/versions", response_model=list[AgentVersionOut])
async def list_agent_versions(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Agent)
        .options(selectinload(Agent.versions))
        .where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.versions
