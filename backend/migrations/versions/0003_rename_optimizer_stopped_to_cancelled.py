"""rename optimizationstatus.stopped to cancelled

Unifies the prompt-optimizer status enum with `runstatus`, which already
uses `cancelled`. The endpoint `POST /prompt-optimizer/runs/{id}/stop` is
unchanged — only the resulting DB value (and the SSE event type emitted by
the worker) move from `stopped` to `cancelled`.

Postgres does not allow a newly-added enum value to be used inside the
same transaction as the ALTER TYPE ... ADD VALUE statement. So we cannot
simply `ADD VALUE 'cancelled'` and then `UPDATE ... SET status='cancelled'`
in the same migration. Instead we use the classic "swap types via TEXT"
pattern:

  1. Convert the column to TEXT (temporarily)
  2. UPDATE text values: 'stopped' → 'cancelled'
  3. Create a new enum type with the unified value set
  4. Convert the column back to the new enum type
  5. Drop the old enum type, rename the new one to the original name

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-11

"""
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Detach the column from the enum type by casting to text.
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status DROP DEFAULT"
    )
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status TYPE text USING status::text"
    )

    # 2. Rename the stopped rows to cancelled.
    op.execute(
        "UPDATE prompt_optimization_runs SET status = 'cancelled' "
        "WHERE status = 'stopped'"
    )

    # 3. Drop the old enum and create the new one with the unified set.
    op.execute("DROP TYPE optimizationstatus")
    op.execute(
        "CREATE TYPE optimizationstatus AS ENUM "
        "('pending', 'running', 'completed', 'failed', 'cancelled')"
    )

    # 4. Re-attach the column to the new enum type.
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status TYPE optimizationstatus "
        "USING status::optimizationstatus"
    )
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status SET DEFAULT 'pending'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status DROP DEFAULT"
    )
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status TYPE text USING status::text"
    )
    op.execute(
        "UPDATE prompt_optimization_runs SET status = 'stopped' "
        "WHERE status = 'cancelled'"
    )
    op.execute("DROP TYPE optimizationstatus")
    op.execute(
        "CREATE TYPE optimizationstatus AS ENUM "
        "('pending', 'running', 'completed', 'failed', 'stopped')"
    )
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status TYPE optimizationstatus "
        "USING status::optimizationstatus"
    )
    op.execute(
        "ALTER TABLE prompt_optimization_runs "
        "ALTER COLUMN status SET DEFAULT 'pending'"
    )
