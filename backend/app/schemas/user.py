from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None
    full_name: str | None = None


class UserOut(BaseModel):
    id: UUID
    email: str
    display_name: str | None
    full_name: str | None
    role: UserRole
    is_active: bool
    is_superuser: bool = Field(description="Compatibility flag derived from role == admin")

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
