from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.agent import Agent, AgentType
from app.models.dataset import EvalDataset, RagEvalDataset
from app.models.evaluation import EvalRun, EvalRunResult, EvalRunStatus
from app.models.user import User
from app.schemas.evaluation import (
    EvalRunCreate,
    EvalRunOut,
    EvalRunResultCreate,
    EvalRunResultOut,
    EvalRunResultsPage,
)

router = APIRouter(prefix="/eval-runs", tags=["eval-runs"])


async def _get_run(db: AsyncSession, run_id: UUID) -> EvalRun:
    result = await db.execute(select(EvalRun).where(EvalRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Eval run not found")
    return run


async def _recalculate_summary(db: AsyncSession, run: EvalRun) -> None:
    rows = await db.execute(
        select(
            func.count(EvalRunResult.id),
            func.count(EvalRunResult.id).filter(EvalRunResult.passed.is_(True)),
            func.count(EvalRunResult.id).filter(EvalRunResult.passed.is_(False)),
            func.count(EvalRunResult.id).filter(EvalRunResult.error.isnot(None)),
            func.avg(EvalRunResult.latency_ms),
            func.avg(EvalRunResult.score),
        ).where(EvalRunResult.run_id == run.id)
    )
    total, passed, failed, errored, avg_latency, avg_score = rows.one()
    run.total_items = max(int(run.total_items or 0), int(total or 0))
    run.passed = int(passed or 0)
    run.failed = int(failed or 0)
    run.errored = int(errored or 0)
    run.avg_latency_ms = float(avg_latency) if avg_latency is not None else None
    run.avg_score = float(avg_score) if avg_score is not None else None


@router.post("", response_model=EvalRunOut, status_code=status.HTTP_201_CREATED)
async def create_eval_run(
    payload: EvalRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent_result = await db.execute(select(Agent).where(Agent.id == payload.agent_id))
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    total_items = 0
    if payload.dataset_id:
        dataset_result = await db.execute(
            select(EvalDataset).where(EvalDataset.id == payload.dataset_id)
        )
        dataset = dataset_result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        if dataset.agent_type and dataset.agent_type != agent.agent_type:
            raise HTTPException(
                status_code=400,
                detail="Dataset agent_type is incompatible with the selected agent",
            )
        total_items = dataset.item_count
    elif payload.rag_dataset_id:
        dataset_result = await db.execute(
            select(RagEvalDataset).where(RagEvalDataset.id == payload.rag_dataset_id)
        )
        dataset = dataset_result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(status_code=404, detail="RAG dataset not found")
        if agent.agent_type != AgentType.RAG:
            raise HTTPException(status_code=400, detail="RAG datasets require a RAG agent")
        total_items = dataset.item_count

    run = EvalRun(
        agent_id=payload.agent_id,
        dataset_id=payload.dataset_id,
        rag_dataset_id=payload.rag_dataset_id,
        status=EvalRunStatus.PENDING,
        config=payload.config,
        total_items=total_items,
        agent_version=agent.version,
        triggered_by=current_user.id,
    )
    db.add(run)
    await db.flush()
    return run


@router.get("", response_model=list[EvalRunOut])
async def list_eval_runs(
    agent_id: UUID | None = None,
    run_status: EvalRunStatus | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(EvalRun).order_by(EvalRun.created_at.desc())
    if agent_id:
        query = query.where(EvalRun.agent_id == agent_id)
    if run_status:
        query = query.where(EvalRun.status == run_status)
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()


@router.get("/{run_id}", response_model=EvalRunOut)
async def get_eval_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_run(db, run_id)


@router.get("/{run_id}/results", response_model=EvalRunResultsPage)
async def list_eval_run_results(
    run_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = await _get_run(db, run_id)

    total_result = await db.execute(
        select(func.count()).select_from(EvalRunResult).where(EvalRunResult.run_id == run.id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(EvalRunResult)
        .options(selectinload(EvalRunResult.rag_details))
        .where(EvalRunResult.run_id == run.id)
        .order_by(EvalRunResult.item_index)
        .limit(limit)
        .offset(offset)
    )
    return EvalRunResultsPage(items=result.scalars().all(), total=total)


@router.post("/{run_id}/results", response_model=EvalRunResultOut, status_code=201)
async def create_eval_run_result(
    run_id: UUID,
    payload: EvalRunResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = await _get_run(db, run_id)
    result = EvalRunResult(run_id=run.id, **payload.model_dump())
    db.add(result)
    await db.flush()
    await _recalculate_summary(db, run)
    return result


@router.post("/{run_id}/cancel", response_model=EvalRunOut)
async def cancel_eval_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = await _get_run(db, run_id)
    if run.status not in (EvalRunStatus.PENDING, EvalRunStatus.RUNNING):
        raise HTTPException(status_code=400, detail="Eval run is not cancellable")
    run.status = EvalRunStatus.CANCELLED
    run.completed_at = datetime.now(timezone.utc)
    return run
