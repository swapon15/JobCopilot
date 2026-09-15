"""add work preference conflicts

Revision ID: 202609150004
Revises: 202609150003
Create Date: 2026-09-15 00:04:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202609150004"
down_revision: str | None = "202609150003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "match_results",
        sa.Column("work_preference_conflicts", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.alter_column("match_results", "work_preference_conflicts", server_default=None)


def downgrade() -> None:
    op.drop_column("match_results", "work_preference_conflicts")
