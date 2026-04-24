from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import TokenOut, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        display_name=payload.display_name or payload.full_name,
    )
    db.add(user)
    await db.flush()
    return user


@router.post("/login", response_model=TokenOut)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    # Track last successful login — powers the "last seen" column in admin UI.
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    return TokenOut(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=TokenOut)
async def refresh(current_user: User = Depends(get_current_user)):
    """Exchange a valid token for a fresh one.

    The frontend calls this before the current token expires so sessions
    can outlive a single JWT lifetime without forcing re-login. Requires
    the current token to still be valid — expired tokens 401 in
    get_current_user and never reach here.
    """
    return TokenOut(access_token=create_access_token(str(current_user.id)))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(_: User = Depends(get_current_user)):
    """Client-side logout for stateless JWT.

    The token is discarded by the browser; this endpoint exists as a hook
    so future session-tracking / token-blacklist logic can plug in without
    touching frontend code. Requires a valid token so unauthenticated
    requests can't spam the endpoint.
    """
    return None
