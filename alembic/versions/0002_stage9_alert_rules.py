"""Add configurable alert rules for Stage 9.

Revision ID: 0002_stage9_alert_rules
Revises: 0001_initial_stage7
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002_stage9_alert_rules"
down_revision = "0001_initial_stage7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the configurable alert rules table."""

    op.create_table(
        "alert_rules",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("metric", sa.String(64), nullable=False),
        sa.Column("operator", sa.String(8), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("device_id", sa.String(128), nullable=True),
        sa.Column("channel", sa.String(128), nullable=True),
        sa.Column(
            "severity",
            sa.String(32),
            nullable=False,
            server_default="WARNING",
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_alert_rules_metric",
        "alert_rules",
        ["metric"],
    )
    op.create_index(
        "ix_alert_rules_device_id",
        "alert_rules",
        ["device_id"],
    )


def downgrade() -> None:
    """Remove only the table introduced by this revision."""

    op.drop_index("ix_alert_rules_device_id", table_name="alert_rules")
    op.drop_index("ix_alert_rules_metric", table_name="alert_rules")
    op.drop_table("alert_rules")
