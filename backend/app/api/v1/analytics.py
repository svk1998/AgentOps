from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.evaluation import EvalRun, EvalRunStatus
from app.models.user import User
from app.schemas.evaluation import (
    AccuracyTrendPoint,
    FieldAccuracyPoint,
    LatencySummary,
    RegressionPoint,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _pass_rate(run: EvalRun) -> float:
    if run.total_items <= 0:
        return 0.0
    return round((run.passed / run.total_items) * 100, 2)


@router.get("/agents/{agent_id}/accuracy-trend", response_model=list[AccuracyTrendPoint])
async def get_accuracy_trend(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EvalRun)
        .where(EvalRun.agent_id == agent_id, EvalRun.status == EvalRunStatus.COMPLETED)
        .order_by(EvalRun.created_at.asc())
    )
    return [
        AccuracyTrendPoint(
            run_id=run.id,
            run_date=run.created_at,
            agent_version=run.agent_version,
            total_items=run.total_items,
            passed=run.passed,
            failed=run.failed,
            errored=run.errored,
            pass_rate_pct=_pass_rate(run),
            avg_latency_ms=run.avg_latency_ms,
            p95_latency_ms=run.p95_latency_ms,
            total_cost_usd=run.total_cost_usd,
        )
        for run in result.scalars().all()
    ]


@router.get("/agents/{agent_id}/field-accuracy", response_model=list[FieldAccuracyPoint])
async def get_field_accuracy(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EvalRun)
        .options(selectinload(EvalRun.results))
        .where(EvalRun.agent_id == agent_id, EvalRun.status == EvalRunStatus.COMPLETED)
        .order_by(EvalRun.created_at.desc())
    )

    points: list[FieldAccuracyPoint] = []
    for run in result.scalars().all():
        aggregate: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "matched": 0})
        for row in run.results:
            field_results = (row.matcher_details or {}).get("field_results", {})
            for field, value in field_results.items():
                aggregate[field]["total"] += 1
                if value.get("match") is True or value.get("matched") is True:
                    aggregate[field]["matched"] += 1

        for field, values in aggregate.items():
            total = values["total"]
            matched = values["matched"]
            points.append(
                FieldAccuracyPoint(
                    run_id=run.id,
                    agent_version=run.agent_version,
                    field=field,
                    total=total,
                    matched=matched,
                    accuracy_pct=round((matched / total) * 100, 2) if total else 0.0,
                )
            )
    return points


@router.get("/agents/{agent_id}/latency", response_model=list[LatencySummary])
async def get_latency_distribution(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EvalRun)
        .where(EvalRun.agent_id == agent_id, EvalRun.status == EvalRunStatus.COMPLETED)
        .order_by(EvalRun.created_at.desc())
    )
    return [
        LatencySummary(
            run_id=run.id,
            p50_latency_ms=run.p50_latency_ms,
            p95_latency_ms=run.p95_latency_ms,
            p99_latency_ms=run.p99_latency_ms,
            avg_latency_ms=run.avg_latency_ms,
        )
        for run in result.scalars().all()
    ]


@router.get("/agents/{agent_id}/regressions", response_model=list[RegressionPoint])
async def get_regressions(
    agent_id: UUID,
    threshold_pct: float = Query(5.0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EvalRun)
        .where(EvalRun.agent_id == agent_id, EvalRun.status == EvalRunStatus.COMPLETED)
        .order_by(EvalRun.created_at.desc())
        .limit(10)
    )
    runs = result.scalars().all()
    points: list[RegressionPoint] = []
    for index, current in enumerate(runs[:-1]):
        previous = runs[index + 1]
        current_rate = _pass_rate(current)
        previous_rate = _pass_rate(previous)
        delta = round(current_rate - previous_rate, 2)
        points.append(
            RegressionPoint(
                current_run=current.id,
                current_version=current.agent_version,
                current_pass_rate=current_rate,
                previous_run=previous.id,
                previous_version=previous.agent_version,
                previous_pass_rate=previous_rate,
                pass_rate_delta=delta,
                is_regression=delta < -threshold_pct,
            )
        )
    return points


@router.get("/compare")
async def compare_agents(
    agent_ids: list[UUID] = Query(default_factory=list),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(EvalRun).where(EvalRun.status == EvalRunStatus.COMPLETED)
    if agent_ids:
        query = query.where(EvalRun.agent_id.in_(agent_ids))
    result = await db.execute(query.order_by(EvalRun.created_at.desc()))

    comparison = []
    for run in result.scalars().all():
        comparison.append(
            {
                "agent_id": run.agent_id,
                "run_id": run.id,
                "agent_version": run.agent_version,
                "pass_rate_pct": _pass_rate(run),
                "avg_latency_ms": run.avg_latency_ms,
                "total_cost_usd": run.total_cost_usd,
                "created_at": run.created_at,
            }
        )
    return {"items": comparison, "total": len(comparison)}
