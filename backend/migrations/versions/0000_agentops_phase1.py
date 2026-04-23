"""create AgentOps Phase 1 backend schema

Revision ID: 0000
Revises:
Create Date: 2026-04-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0000"
down_revision = None
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def _uuid_pk() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


user_role = postgresql.ENUM("admin", "evaluator", "viewer", name="user_role")
agent_type = postgresql.ENUM(
    "llm",
    "rag",
    "vision",
    "multi_step_chain",
    "tool_use",
    "custom",
    name="agent_type",
)
agent_status = postgresql.ENUM("draft", "active", "deprecated", "archived", name="agent_status")
dataset_item_status = postgresql.ENUM(
    "active",
    "disabled",
    "flagged",
    name="dataset_item_status",
)
eval_run_status = postgresql.ENUM(
    "pending",
    "running",
    "completed",
    "failed",
    "cancelled",
    name="eval_run_status",
)
manual_verdict = postgresql.ENUM("pass", "fail", "partial", name="manual_verdict")
severity_level = postgresql.ENUM("critical", "major", "minor", name="severity_level")
manual_session_status = postgresql.ENUM(
    "in_progress",
    "completed",
    name="manual_session_status",
)


def upgrade() -> None:
    bind = op.get_bind()
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    for enum_type in (
        user_role,
        agent_type,
        agent_status,
        dataset_item_status,
        eval_run_status,
        manual_verdict,
        severity_level,
        manual_session_status,
    ):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "users",
        _uuid_pk(),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column(
            "role",
            postgresql.ENUM(name="user_role", create_type=False),
            server_default="viewer",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "agents",
        _uuid_pk(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("agent_type", postgresql.ENUM(name="agent_type", create_type=False), nullable=False),
        sa.Column("endpoint_url", sa.String(2048), nullable=False),
        sa.Column("model_provider", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("input_schema", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("output_schema", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("version", sa.String(50), server_default="1.0.0", nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="agent_status", create_type=False),
            server_default="draft",
            nullable=False,
        ),
        sa.Column("auth_config", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("config", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_agents_name", "agents", ["name"])
    op.create_index("ix_agents_agent_type", "agents", ["agent_type"])
    op.create_index("ix_agents_status", "agents", ["status"])
    op.create_index("idx_agents_tags", "agents", ["tags"], postgresql_using="gin")
    op.create_index(
        "idx_agents_name_trgm",
        "agents",
        ["name"],
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )

    op.create_table(
        "agent_versions",
        _uuid_pk(),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("agent_id", "version", name="uq_agent_versions_agent_version"),
    )
    op.create_index("ix_agent_versions_agent_id", "agent_versions", ["agent_id"])

    op.create_table(
        "eval_datasets",
        _uuid_pk(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("agent_type", postgresql.ENUM(name="agent_type", create_type=False), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("item_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("current_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_eval_datasets_name", "eval_datasets", ["name"])
    op.create_index("ix_eval_datasets_agent_type", "eval_datasets", ["agent_type"])
    op.create_index("idx_eval_datasets_tags", "eval_datasets", ["tags"], postgresql_using="gin")

    op.create_table(
        "eval_dataset_items",
        _uuid_pk(),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("eval_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("input", postgresql.JSONB(), nullable=False),
        sa.Column("expected_output", postgresql.JSONB(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(name="dataset_item_status", create_type=False),
            server_default="active",
            nullable=False,
        ),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_eval_dataset_items_dataset_id", "eval_dataset_items", ["dataset_id"])
    op.create_index("ix_eval_dataset_items_status", "eval_dataset_items", ["status"])
    op.create_index("idx_eval_dataset_items_metadata", "eval_dataset_items", ["metadata"], postgresql_using="gin")

    op.create_table(
        "dataset_versions",
        _uuid_pk(),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("eval_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("snapshot_data", postgresql.JSONB(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("dataset_id", "version_number", name="uq_dataset_versions_version"),
    )
    op.create_index("ix_dataset_versions_dataset_id", "dataset_versions", ["dataset_id"])

    op.create_table(
        "rag_eval_datasets",
        _uuid_pk(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("knowledge_base_ref", sa.String(512), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("item_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_rag_eval_datasets_name", "rag_eval_datasets", ["name"])
    op.create_index("idx_rag_eval_datasets_tags", "rag_eval_datasets", ["tags"], postgresql_using="gin")

    op.create_table(
        "rag_eval_items",
        _uuid_pk(),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rag_eval_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("expected_answer", sa.Text(), nullable=False),
        sa.Column("relevant_chunk_ids", postgresql.ARRAY(sa.String()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("relevant_passages", postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_rag_eval_items_dataset_id", "rag_eval_items", ["dataset_id"])
    op.create_index("idx_rag_eval_items_chunks", "rag_eval_items", ["relevant_chunk_ids"], postgresql_using="gin")

    op.create_table(
        "eval_runs",
        _uuid_pk(),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("eval_datasets.id"), nullable=True),
        sa.Column("rag_dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rag_eval_datasets.id"), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="eval_run_status", create_type=False),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("config", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("total_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column("passed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("errored", sa.Integer(), server_default="0", nullable=False),
        sa.Column("avg_latency_ms", sa.Float(), nullable=True),
        sa.Column("avg_score", sa.Float(), nullable=True),
        sa.Column("p50_latency_ms", sa.Float(), nullable=True),
        sa.Column("p95_latency_ms", sa.Float(), nullable=True),
        sa.Column("p99_latency_ms", sa.Float(), nullable=True),
        sa.Column("total_cost_usd", sa.Float(), nullable=True),
        sa.Column("agent_version", sa.String(50), nullable=True),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.CheckConstraint(
            "(dataset_id IS NOT NULL AND rag_dataset_id IS NULL) OR "
            "(dataset_id IS NULL AND rag_dataset_id IS NOT NULL)",
            name="chk_eval_runs_one_dataset_type",
        ),
    )
    op.create_index("ix_eval_runs_agent_id", "eval_runs", ["agent_id"])
    op.create_index("ix_eval_runs_dataset_id", "eval_runs", ["dataset_id"])
    op.create_index("ix_eval_runs_rag_dataset_id", "eval_runs", ["rag_dataset_id"])
    op.create_index("ix_eval_runs_status", "eval_runs", ["status"])

    op.create_table(
        "eval_run_results",
        _uuid_pk(),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("eval_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("dataset_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("item_index", sa.Integer(), nullable=False),
        sa.Column("agent_input", postgresql.JSONB(), nullable=False),
        sa.Column("agent_output", postgresql.JSONB(), nullable=True),
        sa.Column("expected_output", postgresql.JSONB(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("tokens_in", sa.Integer(), nullable=True),
        sa.Column("tokens_out", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=True),
        sa.Column("matcher_details", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("raw_response", postgresql.JSONB(), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_eval_run_results_run_id", "eval_run_results", ["run_id"])
    op.create_index("ix_eval_run_results_score", "eval_run_results", ["score"])
    op.create_index("ix_eval_run_results_passed", "eval_run_results", ["passed"])

    op.create_table(
        "rag_eval_result_details",
        _uuid_pk(),
        sa.Column(
            "eval_result_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("eval_run_results.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("retrieved_chunks", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("retrieval_precision", sa.Float(), nullable=True),
        sa.Column("retrieval_recall", sa.Float(), nullable=True),
        sa.Column("faithfulness_score", sa.Float(), nullable=True),
        sa.Column("answer_relevance_score", sa.Float(), nullable=True),
        sa.Column("chunk_attribution", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_rag_eval_result_details_eval_result_id", "rag_eval_result_details", ["eval_result_id"])

    op.create_table(
        "manual_eval_sessions",
        _uuid_pk(),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("eval_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("eval_runs.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(name="manual_session_status", create_type=False),
            server_default="in_progress",
            nullable=False,
        ),
        sa.Column("total_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reviewed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("assignment_config", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_manual_eval_sessions_agent_id", "manual_eval_sessions", ["agent_id"])
    op.create_index("ix_manual_eval_sessions_eval_run_id", "manual_eval_sessions", ["eval_run_id"])
    op.create_index("ix_manual_eval_sessions_status", "manual_eval_sessions", ["status"])

    op.create_table(
        "manual_eval_items",
        _uuid_pk(),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("manual_eval_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("eval_result_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("eval_run_results.id"), nullable=True),
        sa.Column("item_index", sa.Integer(), nullable=False),
        sa.Column("agent_input", postgresql.JSONB(), nullable=False),
        sa.Column("agent_output", postgresql.JSONB(), nullable=False),
        sa.Column("verdict", postgresql.ENUM(name="manual_verdict", create_type=False), nullable=True),
        sa.Column("field_verdicts", postgresql.JSONB(), nullable=True),
        sa.Column("severity", postgresql.ENUM(name="severity_level", create_type=False), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("corrected_output", postgresql.JSONB(), nullable=True),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_reviewed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_duration_ms", sa.Integer(), nullable=True),
        sa.Column("lock_version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("locked_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_manual_eval_items_session_id", "manual_eval_items", ["session_id"])
    op.create_index("ix_manual_eval_items_eval_result_id", "manual_eval_items", ["eval_result_id"])
    op.create_index("ix_manual_eval_items_reviewer_id", "manual_eval_items", ["reviewer_id"])
    op.create_index("ix_manual_eval_items_assigned_to", "manual_eval_items", ["assigned_to"])
    op.create_index("ix_manual_eval_items_is_reviewed", "manual_eval_items", ["is_reviewed"])
    op.create_index("ix_manual_eval_items_verdict", "manual_eval_items", ["verdict"])

    op.create_table(
        "audit_log",
        _uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("changes", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("idx_audit_log_entity", "audit_log", ["entity_type", "entity_id", "created_at"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("manual_eval_items")
    op.drop_table("manual_eval_sessions")
    op.drop_table("rag_eval_result_details")
    op.drop_table("eval_run_results")
    op.drop_table("eval_runs")
    op.drop_table("rag_eval_items")
    op.drop_table("rag_eval_datasets")
    op.drop_table("dataset_versions")
    op.drop_table("eval_dataset_items")
    op.drop_table("eval_datasets")
    op.drop_table("agent_versions")
    op.drop_table("agents")
    op.drop_table("users")

    bind = op.get_bind()
    for enum_type in (
        manual_session_status,
        severity_level,
        manual_verdict,
        eval_run_status,
        dataset_item_status,
        agent_status,
        agent_type,
        user_role,
    ):
        enum_type.drop(bind, checkfirst=True)
