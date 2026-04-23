"""add users.last_login_at

Revision ID: 0001
Revises: 0000
Create Date: 2026-04-24
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = "0000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "last_login_at")
