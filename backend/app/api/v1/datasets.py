from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.agent import AgentType
from app.models.dataset import DatasetVersion, EvalDataset, EvalDatasetItem
from app.models.user import User
from app.schemas.dataset import (
    BulkDatasetItemsCreate,
    DatasetSnapshotCreate,
    DatasetVersionOut,
    EvalDatasetCreate,
    EvalDatasetDetail,
    EvalDatasetItemCreate,
    EvalDatasetItemOut,
    EvalDatasetItemUpdate,
    EvalDatasetOut,
    EvalDatasetUpdate,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])


async def _get_dataset(db: AsyncSession, dataset_id: UUID, with_items: bool = False) -> EvalDataset:
    query = select(EvalDataset).where(EvalDataset.id == dataset_id)
    if with_items:
        query = query.options(selectinload(EvalDataset.items))
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


def _item_from_payload(dataset_id: UUID, payload: EvalDatasetItemCreate) -> EvalDatasetItem:
    return EvalDatasetItem(
        dataset_id=dataset_id,
        input=payload.input,
        expected_output=payload.expected_output,
        metadata_=payload.metadata,
        status=payload.status,
        sort_order=payload.sort_order,
    )


def _snapshot_item(item: EvalDatasetItem) -> dict[str, Any]:
    return {
        "id": str(item.id),
        "input": item.input,
        "expected_output": item.expected_output,
        "metadata": item.metadata_,
        "status": item.status.value,
        "sort_order": item.sort_order,
    }


@router.get("", response_model=list[EvalDatasetOut])
async def list_datasets(
    search: str | None = None,
    agent_type: AgentType | None = None,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(EvalDataset).order_by(EvalDataset.created_at.desc())
    if search:
        query = query.where(
            EvalDataset.name.ilike(f"%{search}%")
            | EvalDataset.description.ilike(f"%{search}%")
        )
    if agent_type:
        query = query.where(EvalDataset.agent_type == agent_type)
    if tag:
        query = query.where(EvalDataset.tags.contains([tag]))

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=EvalDatasetDetail, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    payload: EvalDatasetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = EvalDataset(
        name=payload.name,
        description=payload.description,
        agent_type=payload.agent_type,
        tags=payload.tags,
        created_by=current_user.id,
    )
    db.add(dataset)
    await db.flush()

    for index, item_payload in enumerate(payload.items):
        if item_payload.sort_order == 0:
            item_payload.sort_order = index
        db.add(_item_from_payload(dataset.id, item_payload))
    dataset.item_count = len(payload.items)
    await db.flush()
    return await _get_dataset(db, dataset.id, with_items=True)


@router.get("/{dataset_id}", response_model=EvalDatasetDetail)
async def get_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_dataset(db, dataset_id, with_items=True)


@router.put("/{dataset_id}", response_model=EvalDatasetOut)
@router.patch("/{dataset_id}", response_model=EvalDatasetOut)
async def update_dataset(
    dataset_id: UUID,
    payload: EvalDatasetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(dataset, field, value)
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)
    await db.delete(dataset)


@router.post("/{dataset_id}/items", response_model=list[EvalDatasetItemOut], status_code=201)
async def add_dataset_items(
    dataset_id: UUID,
    payload: EvalDatasetItemCreate | BulkDatasetItemsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)
    item_payloads = payload.items if isinstance(payload, BulkDatasetItemsCreate) else [payload]
    items = [_item_from_payload(dataset.id, item_payload) for item_payload in item_payloads]
    db.add_all(items)
    dataset.item_count += len(items)
    await db.flush()
    return items


@router.put("/{dataset_id}/items/{item_id}", response_model=EvalDatasetItemOut)
@router.patch("/{dataset_id}/items/{item_id}", response_model=EvalDatasetItemOut)
async def update_dataset_item(
    dataset_id: UUID,
    item_id: UUID,
    payload: EvalDatasetItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EvalDatasetItem).where(
            EvalDatasetItem.dataset_id == dataset_id,
            EvalDatasetItem.id == item_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Dataset item not found")

    values = payload.model_dump(exclude_none=True)
    if "metadata" in values:
        item.metadata_ = values.pop("metadata")
    for field, value in values.items():
        setattr(item, field, value)
    return item


@router.delete("/{dataset_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset_item(
    dataset_id: UUID,
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)
    result = await db.execute(
        select(EvalDatasetItem).where(
            EvalDatasetItem.dataset_id == dataset_id,
            EvalDatasetItem.id == item_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Dataset item not found")
    await db.delete(item)
    dataset.item_count = max(dataset.item_count - 1, 0)


@router.post("/{dataset_id}/import", response_model=list[EvalDatasetItemOut])
async def import_dataset_items(
    dataset_id: UUID,
    payload: BulkDatasetItemsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await add_dataset_items(dataset_id, payload, db, current_user)


@router.get("/{dataset_id}/export", response_model=EvalDatasetDetail)
async def export_dataset(
    dataset_id: UUID,
    export_format: str = Query("json", alias="format", pattern="^(json|jsonl|csv)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_dataset(db, dataset_id, with_items=True)


@router.post("/{dataset_id}/snapshot", response_model=DatasetVersionOut, status_code=201)
async def snapshot_dataset(
    dataset_id: UUID,
    payload: DatasetSnapshotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = await _get_dataset(db, dataset_id, with_items=True)
    version = DatasetVersion(
        dataset_id=dataset.id,
        version_number=dataset.current_version,
        item_count=dataset.item_count,
        snapshot_data=[_snapshot_item(item) for item in dataset.items],
        notes=payload.notes,
        created_by=current_user.id,
    )
    db.add(version)
    dataset.current_version += 1
    await db.flush()
    return version


@router.get("/{dataset_id}/versions", response_model=list[DatasetVersionOut])
async def list_dataset_versions(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)
    result = await db.execute(
        select(DatasetVersion)
        .where(DatasetVersion.dataset_id == dataset.id)
        .order_by(DatasetVersion.version_number.desc())
    )
    return result.scalars().all()
