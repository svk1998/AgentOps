"""create prompt_optimization_runs and prompt_optimization_iterations tables

Revision ID: 0001
Revises:
Create Date: 2026-04-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = "0000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_optimization_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("base_prompt", sa.Text(), nullable=False),
        sa.Column("required_output", sa.Text(), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("max_iterations", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("score_threshold", sa.Integer(), nullable=False, server_default="80"),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "running", "completed", "failed", "stopped",
                name="optimizationstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("best_score", sa.Integer(), nullable=True),
        sa.Column("best_prompt", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_prompt_optimization_runs_status",
        "prompt_optimization_runs",
        ["status"],
    )

    op.create_table(
        "prompt_optimization_iterations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("prompt_optimization_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("output", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("is_goal_reached", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("usage", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_prompt_optimization_iterations_run_id",
        "prompt_optimization_iterations",
        ["run_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_prompt_optimization_iterations_run_id", "prompt_optimization_iterations")
    op.drop_table("prompt_optimization_iterations")
    op.drop_index("ix_prompt_optimization_runs_status", "prompt_optimization_runs")
    op.drop_table("prompt_optimization_runs")
    op.execute("DROP TYPE IF EXISTS optimizationstatus")
