"""add match recommendation policy fields

Revision ID: 202609150003
Revises: 202609150002
Create Date: 2026-09-15 00:03:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202609150003"
down_revision: str | None = "202609150002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "match_results",
        sa.Column(
            "recommendation", sa.String(length=20), nullable=False, server_default="CONSIDER"
        ),
    )
    op.add_column(
        "match_results",
        sa.Column("recommendation_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "match_results",
        sa.Column(
            "recommendation_reason",
            sa.Text(),
            nullable=False,
            server_default="Recommendation policy was added after this match was created.",
        ),
    )
    op.alter_column("match_results", "recommendation", server_default=None)
    op.alter_column("match_results", "recommendation_score", server_default=None)
    op.alter_column("match_results", "recommendation_reason", server_default=None)


def downgrade() -> None:
    op.drop_column("match_results", "recommendation_reason")
    op.drop_column("match_results", "recommendation_score")
    op.drop_column("match_results", "recommendation")
