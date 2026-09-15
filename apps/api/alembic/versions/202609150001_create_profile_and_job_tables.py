"""create profile and job tables

Revision ID: 202609150001
Revises:
Create Date: 2026-09-15 00:01:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202609150001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candidate_profiles",
        sa.Column("headline", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("target_roles", sa.JSON(), nullable=False),
        sa.Column("preferred_locations", sa.JSON(), nullable=False),
        sa.Column("work_preferences", sa.JSON(), nullable=False),
        sa.Column("sponsorship_required", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_descriptions",
        sa.Column("raw_description", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("company", sa.String(length=200), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("compensation", sa.String(length=200), nullable=True),
        sa.Column("work_mode", sa.String(length=100), nullable=True),
        sa.Column("normalized_requirements", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "candidate_evidence",
        sa.Column("candidate_profile_id", sa.String(length=36), nullable=False),
        sa.Column("project_or_position", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("responsibilities", sa.JSON(), nullable=False),
        sa.Column("measurable_outcomes", sa.JSON(), nullable=False),
        sa.Column("experience_type", sa.String(length=40), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_candidate_evidence_candidate_profile_id"),
        "candidate_evidence",
        ["candidate_profile_id"],
        unique=False,
    )
    op.create_table(
        "job_decisions",
        sa.Column("job_description_id", sa.String(length=36), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["job_description_id"], ["job_descriptions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_job_decisions_job_description_id"),
        "job_decisions",
        ["job_description_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_job_decisions_job_description_id"), table_name="job_decisions")
    op.drop_table("job_decisions")
    op.drop_index(
        op.f("ix_candidate_evidence_candidate_profile_id"), table_name="candidate_evidence"
    )
    op.drop_table("candidate_evidence")
    op.drop_table("job_descriptions")
    op.drop_table("candidate_profiles")
