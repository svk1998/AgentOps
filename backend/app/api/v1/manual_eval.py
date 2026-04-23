from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.agent import Agent
from app.models.evaluation import (
    EvalRun,
    EvalRunResult,
    ManualEvalItem,
    ManualEvalSession,
    ManualSessionStatus,
)
from app.models.user import User
from app.schemas.evaluation import (
    ManualEvalItemOut,
    ManualEvalSessionCreate,
    ManualEvalSessionDetail,
    ManualReviewSubmit,
)

router = APIRouter(prefix="/manual-eval", tags=["manual-eval"])


async def _get_session(db: AsyncSession, session_id: UUID, with_items: bool = False):
    query = select(ManualEvalSession).where(ManualEvalSession.id == session_id)
    if with_items:
        query = query.options(selectinload(ManualEvalSession.items))
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Manual eval session not found")
    return session


@router.post(
    "/sessions",
    response_model=ManualEvalSessionDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_manual_eval_session(
    payload: ManualEvalSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent_result = await db.execute(select(Agent).where(Agent.id == payload.agent_id))
    if not agent_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent not found")

    seed_items = payload.items
    if payload.eval_run_id and not seed_items:
        run_result = await db.execute(select(EvalRun).where(EvalRun.id == payload.eval_run_id))
        run = run_result.scalar_one_or_none()
        if not run:
            raise HTTPException(status_code=404, detail="Eval run not found")
        if run.agent_id != payload.agent_id:
            raise HTTPException(status_code=400, detail="Eval run belongs to a different agent")
        failed_results = await db.execute(
            select(EvalRunResult)
            .where(
                EvalRunResult.run_id == run.id,
                (EvalRunResult.passed.is_(False) | EvalRunResult.error.isnot(None)),
            )
            .order_by(EvalRunResult.item_index)
        )
        seed_items = [
            {
                "eval_result_id": result.id,
                "item_index": result.item_index,
                "agent_input": result.agent_input,
                "agent_output": result.agent_output or {},
            }
            for result in failed_results.scalars().all()
        ]

    session = ManualEvalSession(
        agent_id=payload.agent_id,
        eval_run_id=payload.eval_run_id,
        name=payload.name,
        description=payload.description,
        assignment_config=payload.assignment_config,
        total_items=len(seed_items),
        created_by=current_user.id,
    )
    db.add(session)
    await db.flush()

    items = []
    for raw_item in seed_items:
        item_payload = raw_item if isinstance(raw_item, dict) else raw_item.model_dump()
        items.append(
            ManualEvalItem(
                session_id=session.id,
                eval_result_id=item_payload.get("eval_result_id"),
                item_index=item_payload["item_index"],
                agent_input=item_payload["agent_input"],
                agent_output=item_payload["agent_output"],
                assigned_to=item_payload.get("assigned_to"),
            )
        )
    db.add_all(items)
    await db.flush()
    return await _get_session(db, session.id, with_items=True)


@router.get("/sessions/{session_id}", response_model=ManualEvalSessionDetail)
async def get_manual_eval_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_session(db, session_id, with_items=True)


@router.get("/queue/{session_id}", response_model=ManualEvalItemOut | None)
async def get_next_manual_eval_item(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_session(db, session_id)
    result = await db.execute(
        select(ManualEvalItem)
        .where(
            ManualEvalItem.session_id == session_id,
            ManualEvalItem.is_reviewed.is_(False),
        )
        .order_by(ManualEvalItem.item_index)
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.post(
    "/sessions/{session_id}/items/{item_id}/review",
    response_model=ManualEvalItemOut,
)
async def submit_manual_review(
    session_id: UUID,
    item_id: UUID,
    payload: ManualReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = await _get_session(db, session_id)
    result = await db.execute(
        select(ManualEvalItem).where(
            ManualEvalItem.session_id == session_id,
            ManualEvalItem.id == item_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Manual eval item not found")

    if payload.lock_version is not None and payload.lock_version != item.lock_version:
        raise HTTPException(status_code=409, detail="Manual eval item was updated")

    was_reviewed = item.is_reviewed
    item.verdict = payload.verdict
    item.field_verdicts = payload.field_verdicts
    item.severity = payload.severity
    item.reviewer_notes = payload.reviewer_notes
    item.corrected_output = payload.corrected_output
    item.review_duration_ms = payload.review_duration_ms
    item.reviewer_id = current_user.id
    item.is_reviewed = True
    item.reviewed_at = datetime.now(timezone.utc)
    item.lock_version += 1

    if not was_reviewed:
        session.reviewed_count += 1
    if session.total_items and session.reviewed_count >= session.total_items:
        session.status = ManualSessionStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)

    return item
