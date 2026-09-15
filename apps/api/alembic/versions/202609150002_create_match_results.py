"""create match results

Revision ID: 202609150002
Revises: 202609150001
Create Date: 2026-09-15 00:02:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202609150002"
down_revision: str | None = "202609150001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "match_results",
        sa.Column("candidate_profile_id", sa.String(length=36), nullable=False),
        sa.Column("job_description_id", sa.String(length=36), nullable=False),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("mandatory_gaps", sa.JSON(), nullable=False),
        sa.Column("preferred_gaps", sa.JSON(), nullable=False),
        sa.Column("evidence_matches", sa.JSON(), nullable=False),
        sa.Column("concise_rationale", sa.Text(), nullable=False),
        sa.Column("interview_risks", sa.JSON(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=100), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["candidate_profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["job_description_id"], ["job_descriptions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_match_results_candidate_profile_id"),
        "match_results",
        ["candidate_profile_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_match_results_job_description_id"),
        "match_results",
        ["job_description_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_match_results_job_description_id"), table_name="match_results")
    op.drop_index(op.f("ix_match_results_candidate_profile_id"), table_name="match_results")
    op.drop_table("match_results")
