from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.dataset import RagEvalDataset, RagEvalItem
from app.models.user import User
from app.schemas.dataset import (
    RagEvalDatasetCreate,
    RagEvalDatasetDetail,
    RagEvalDatasetOut,
    RagEvalItemCreate,
    RagKnowledgeBaseSync,
)

router = APIRouter(prefix="/rag-datasets", tags=["rag-datasets"])


async def _get_rag_dataset(
    db: AsyncSession,
    dataset_id: UUID,
    with_items: bool = False,
) -> RagEvalDataset:
    query = select(RagEvalDataset).where(RagEvalDataset.id == dataset_id)
    if with_items:
        query = query.options(selectinload(RagEvalDataset.items))
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="RAG dataset not found")
    return dataset


def _item_from_payload(dataset_id: UUID, payload: RagEvalItemCreate) -> RagEvalItem:
    return RagEvalItem(
        dataset_id=dataset_id,
        query=payload.query,
        expected_answer=payload.expected_answer,
        relevant_chunk_ids=payload.relevant_chunk_ids,
        relevant_passages=payload.relevant_passages,
        metadata_=payload.metadata,
    )


@router.get("", response_model=list[RagEvalDatasetOut])
async def list_rag_datasets(
    search: str | None = None,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(RagEvalDataset).order_by(RagEvalDataset.created_at.desc())
    if search:
        query = query.where(
            RagEvalDataset.name.ilike(f"%{search}%")
            | RagEvalDataset.description.ilike(f"%{search}%")
            | RagEvalDataset.knowledge_base_ref.ilike(f"%{search}%")
        )
    if tag:
        query = query.where(RagEvalDataset.tags.contains([tag]))

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=RagEvalDatasetDetail, status_code=status.HTTP_201_CREATED)
async def create_rag_dataset(
    payload: RagEvalDatasetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = RagEvalDataset(
        name=payload.name,
        description=payload.description,
        knowledge_base_ref=payload.knowledge_base_ref,
        tags=payload.tags,
        item_count=len(payload.items),
        created_by=current_user.id,
    )
    db.add(dataset)
    await db.flush()
    db.add_all([_item_from_payload(dataset.id, item) for item in payload.items])
    await db.flush()
    return await _get_rag_dataset(db, dataset.id, with_items=True)


@router.get("/{dataset_id}", response_model=RagEvalDatasetDetail)
async def get_rag_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_rag_dataset(db, dataset_id, with_items=True)


@router.post("/{dataset_id}/sync", response_model=RagEvalDatasetDetail)
async def sync_rag_dataset(
    dataset_id: UUID,
    payload: RagKnowledgeBaseSync,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = await _get_rag_dataset(db, dataset_id)
    if payload.knowledge_base_ref is not None:
        dataset.knowledge_base_ref = payload.knowledge_base_ref

    items = [_item_from_payload(dataset.id, item_payload) for item_payload in payload.items]
    db.add_all(items)
    dataset.item_count += len(items)
    await db.flush()
    return await _get_rag_dataset(db, dataset.id, with_items=True)
