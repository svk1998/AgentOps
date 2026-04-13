import uuid

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase


class Agent(UUIDBase):
    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=True)

    # Tool IDs this agent has access to
    tool_ids: Mapped[list] = mapped_column(JSON, default=list)

    # LLM parameters (temperature, max_tokens, etc.)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    runs: Mapped[list["Run"]] = relationship("Run", back_populates="agent", lazy="dynamic")  # noqa: F821
