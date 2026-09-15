from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CandidateProfileRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candidate_profiles"

    headline: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    target_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    preferred_locations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    work_preferences: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    sponsorship_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    evidence: Mapped[list["CandidateEvidenceRecord"]] = relationship(
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        order_by="CandidateEvidenceRecord.created_at",
    )


class CandidateEvidenceRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candidate_evidence"

    candidate_profile_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_or_position: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    responsibilities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    measurable_outcomes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    experience_type: Mapped[str] = mapped_column(String(40), nullable=False)

    candidate_profile: Mapped[CandidateProfileRecord] = relationship(back_populates="evidence")


class JobDescriptionRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_descriptions"

    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    compensation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    work_mode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    normalized_requirements: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )

    decisions: Mapped[list["JobDecisionRecord"]] = relationship(
        back_populates="job_description", cascade="all, delete-orphan"
    )


class JobDecisionRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_decisions"

    job_description_id: Mapped[str] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    job_description: Mapped[JobDescriptionRecord] = relationship(back_populates="decisions")
