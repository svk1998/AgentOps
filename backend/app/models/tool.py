from sqlalchemy import JSON, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDBase


class Tool(UUIDBase):
    __tablename__ = "tools"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # JSON Schema for the tool's input parameters
    input_schema: Mapped[dict] = mapped_column(JSON, default=dict)

    # Python dotted path to the tool's handler function
    handler: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Optional config (API keys, endpoints, etc.) — store refs, not secrets
    config: Mapped[dict] = mapped_column(JSON, default=dict)
