import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.run import Run, RunStatus
from app.models.user import User
from app.schemas.run import RunCreate, RunList, RunLogOut, RunOut
from app.workers.tasks import enqueue_run

router = APIRouter(prefix="/runs", tags=["runs"])

RUN_LOG_CHANNEL = "run:{run_id}:logs"


def _run_to_out(run: Run) -> RunOut:
    agent_name = run.agent.name if run.agent else None
    return RunOut(
        id=run.id,
        agent_id=run.agent_id,
        triggered_by=run.triggered_by,
        status=run.status,
        input=run.input,
        output=run.output,
        usage=run.usage,
        error=run.error,
        created_at=run.created_at,
        finished_at=run.finished_at,
        agent_name=agent_name,
    )


@router.get("", response_model=RunList)
async def list_runs(
    agent_id: UUID | None = None,
    run_status: RunStatus | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func

    query = (
        select(Run)
        .options(selectinload(Run.agent))
        .order_by(Run.created_at.desc())
    )
    if agent_id:
        query = query.where(Run.agent_id == agent_id)
    if run_status:
        query = query.where(Run.status == run_status)

    total_q = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_q)
    total = total_result.scalar() or 0

    result = await db.execute(query.limit(limit).offset(offset))
    runs = result.scalars().all()

    return RunList(items=[_run_to_out(r) for r in runs], total=total)


@router.post("", response_model=RunOut, status_code=status.HTTP_201_CREATED)
async def trigger_run(
    payload: RunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = Run(
        agent_id=payload.agent_id,
        triggered_by=current_user.id,
        input=payload.input,
        status=RunStatus.PENDING,
    )
    db.add(run)
    await db.flush()
    await enqueue_run(str(run.id))

    result = await db.execute(
        select(Run).options(selectinload(Run.agent)).where(Run.id == run.id)
    )
    return _run_to_out(result.scalar_one())


@router.get("/{run_id}", response_model=RunOut)
async def get_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Run).options(selectinload(Run.agent)).where(Run.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_out(run)


@router.get("/{run_id}/logs", response_model=list[RunLogOut])
async def get_run_logs(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Run).options(selectinload(Run.logs)).where(Run.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.logs


@router.get("/{run_id}/stream")
async def stream_run_logs(
    run_id: UUID,
    request: Request,
    token: str = Query(...),
):
    """SSE endpoint — token passed as query param since EventSource cannot send headers."""
    from app.core.security import decode_access_token
    from app.core.database import AsyncSessionLocal
    from app.models.user import User as UserModel
    from sqlalchemy import select as sa_select

    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    redis = await get_redis()
    channel = RUN_LOG_CHANNEL.format(run_id=run_id)

    async def event_generator():
        async with redis.pubsub() as pubsub:
            await pubsub.subscribe(channel)
            try:
                while True:
                    if await request.is_disconnected():
                        break
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message:
                        yield f"data: {message['data']}\n\n"
                    else:
                        yield ": ping\n\n"
                    await asyncio.sleep(0.1)
            finally:
                await pubsub.unsubscribe(channel)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/{run_id}/cancel", response_model=RunOut)
async def cancel_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Run).options(selectinload(Run.agent)).where(Run.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status not in (RunStatus.PENDING, RunStatus.RUNNING):
        raise HTTPException(status_code=400, detail="Run is not cancellable")

    run.status = RunStatus.CANCELLED
    await db.commit()
    return _run_to_out(run)
