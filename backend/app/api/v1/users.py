from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_current_user
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


async def _get_user(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=list[UserOut])
async def list_users(
    search: str | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    query = select(User)
    if search:
        like = f"%{search}%"
        query = query.where(or_(User.email.ilike(like), User.display_name.ilike(like)))
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    query = query.order_by(User.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        display_name=payload.display_name or payload.full_name,
        role=payload.role or UserRole.VIEWER,
    )
    db.add(user)
    await db.flush()
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Allow self-read for any user; admin-read for everyone
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await _get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Allow self-update for display_name + password; admin can update everything
    target = await _get_user(db, user_id)
    is_self = user_id == current_user.id

    if not is_self and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    if is_self and not current_user.is_superuser:
        # Non-admin self-updates: restrict to safe fields
        if payload.role is not None or payload.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change role or active state",
            )

    data = payload.model_dump(exclude_unset=True)

    if "password" in data:
        password = data.pop("password")
        if password:
            target.hashed_password = hash_password(password)

    if "email" in data and data["email"] and data["email"] != target.email:
        existing = await db.execute(select(User).where(User.email == data["email"]))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

    for field, value in data.items():
        setattr(target, field, value)

    await db.flush()
    return target


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    target = await _get_user(db, user_id)
    # Soft delete — deactivate instead of hard-remove so historical audit links survive
    target.is_active = False
    await db.flush()


@router.post("/{user_id}/reactivate", response_model=UserOut)
async def reactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    target = await _get_user(db, user_id)
    target.is_active = True
    await db.flush()
    return target
