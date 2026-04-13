"""
GET /v1/stats/summary  — aggregate dashboard metrics
GET /v1/stats/runs-timeline?days=7  — daily run counts by status
GET /v1/stats/token-timeline?days=7 — daily token usage
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import cast, case, func, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.agent import Agent
from app.models.run import Run, RunStatus
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["stats"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class RunStats(BaseModel):
    total: int
    pending: int
    running: int
    completed: int
    failed: int
    cancelled: int
    last_24h: int
    success_rate: float


class AgentStats(BaseModel):
    total: int
    active_last_24h: int


class TokenStats(BaseModel):
    total: int
    last_24h: int


class StatsSummary(BaseModel):
    agents: AgentStats
    runs: RunStats
    tokens: TokenStats


class DayBucket(BaseModel):
    date: str
    completed: int
    failed: int
    total: int


class TokenBucket(BaseModel):
    date: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now():
    return datetime.now(timezone.utc)


def _since_24h():
    return _now() - timedelta(hours=24)


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=StatsSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = _since_24h()

    # Run counts by status
    run_q = await db.execute(
        select(
            func.count().label("total"),
            func.sum(case((Run.status == RunStatus.PENDING,   1), else_=0)).label("pending"),
            func.sum(case((Run.status == RunStatus.RUNNING,   1), else_=0)).label("running"),
            func.sum(case((Run.status == RunStatus.COMPLETED, 1), else_=0)).label("completed"),
            func.sum(case((Run.status == RunStatus.FAILED,    1), else_=0)).label("failed"),
            func.sum(case((Run.status == RunStatus.CANCELLED, 1), else_=0)).label("cancelled"),
            func.sum(case((Run.created_at >= since,           1), else_=0)).label("last_24h"),
        )
    )
    run_row = run_q.one()

    total     = run_row.total     or 0
    completed = run_row.completed or 0
    failed    = run_row.failed    or 0
    success_rate = round(completed / (completed + failed), 4) if (completed + failed) > 0 else 0.0

    # Token totals (sum from usage JSONB column)
    tok_q = await db.execute(
        select(
            func.coalesce(
                func.sum(cast(Run.usage["total_tokens"].astext, type_=text("integer"))), 0
            ).label("total"),
            func.coalesce(
                func.sum(
                    case(
                        (Run.created_at >= since,
                         cast(Run.usage["total_tokens"].astext, type_=text("integer"))),
                        else_=0,
                    )
                ), 0
            ).label("last_24h"),
        ).where(Run.usage.isnot(None))
    )
    tok_row = tok_q.one()

    # Agent counts
    agent_total_q = await db.execute(select(func.count()).select_from(Agent))
    agent_total = agent_total_q.scalar() or 0

    active_q = await db.execute(
        select(func.count(Run.agent_id.distinct())).where(Run.created_at >= since)
    )
    active_agents = active_q.scalar() or 0

    return StatsSummary(
        agents=AgentStats(total=agent_total, active_last_24h=active_agents),
        runs=RunStats(
            total=total,
            pending=run_row.pending    or 0,
            running=run_row.running    or 0,
            completed=completed,
            failed=failed,
            cancelled=run_row.cancelled or 0,
            last_24h=run_row.last_24h  or 0,
            success_rate=success_rate,
        ),
        tokens=TokenStats(total=int(tok_row.total), last_24h=int(tok_row.last_24h)),
    )


@router.get("/runs-timeline", response_model=list[DayBucket])
async def get_runs_timeline(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = _now() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date_trunc("day", Run.created_at).label("day"),
            func.sum(case((Run.status == RunStatus.COMPLETED, 1), else_=0)).label("completed"),
            func.sum(case((Run.status == RunStatus.FAILED,    1), else_=0)).label("failed"),
            func.count().label("total"),
        )
        .where(Run.created_at >= since)
        .group_by(text("day"))
        .order_by(text("day"))
    )
    rows = result.all()

    return [
        DayBucket(
            date=row.day.strftime("%Y-%m-%d"),
            completed=row.completed or 0,
            failed=row.failed or 0,
            total=row.total or 0,
        )
        for row in rows
    ]


@router.get("/token-timeline", response_model=list[TokenBucket])
async def get_token_timeline(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = _now() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date_trunc("day", Run.created_at).label("day"),
            func.coalesce(
                func.sum(cast(Run.usage["prompt_tokens"].astext,     type_=text("integer"))), 0
            ).label("prompt_tokens"),
            func.coalesce(
                func.sum(cast(Run.usage["completion_tokens"].astext, type_=text("integer"))), 0
            ).label("completion_tokens"),
            func.coalesce(
                func.sum(cast(Run.usage["total_tokens"].astext,      type_=text("integer"))), 0
            ).label("total_tokens"),
        )
        .where(Run.created_at >= since, Run.usage.isnot(None))
        .group_by(text("day"))
        .order_by(text("day"))
    )
    rows = result.all()

    return [
        TokenBucket(
            date=row.day.strftime("%Y-%m-%d"),
            prompt_tokens=int(row.prompt_tokens),
            completion_tokens=int(row.completion_tokens),
            total_tokens=int(row.total_tokens),
        )
        for row in rows
    ]
