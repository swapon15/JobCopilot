from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import CandidateEvidenceRecord, CandidateProfileRecord
from app.domain import CandidateProfile, CandidateProfileCreate


class CandidateProfileRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, profile: CandidateProfileCreate) -> CandidateProfile:
        record = CandidateProfileRecord(
            headline=profile.headline,
            summary=profile.summary,
            target_roles=profile.target_roles,
            preferred_locations=profile.preferred_locations,
            work_preferences=profile.work_preferences,
            sponsorship_required=profile.sponsorship_required,
            evidence=[
                CandidateEvidenceRecord(
                    project_or_position=item.project_or_position,
                    description=item.description,
                    skills=item.skills,
                    responsibilities=item.responsibilities,
                    measurable_outcomes=item.measurable_outcomes,
                    experience_type=item.experience_type.value,
                )
                for item in profile.evidence
            ],
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return self.get(UUID(record.id))

    def get(self, profile_id: UUID) -> CandidateProfile:
        statement = (
            select(CandidateProfileRecord)
            .options(selectinload(CandidateProfileRecord.evidence))
            .where(CandidateProfileRecord.id == str(profile_id))
        )
        record = self.session.scalar(statement)
        if record is None:
            raise LookupError(f"Candidate profile {profile_id} was not found")
        return CandidateProfile.model_validate(record)

    def get_latest(self) -> CandidateProfile | None:
        statement = (
            select(CandidateProfileRecord)
            .options(selectinload(CandidateProfileRecord.evidence))
            .order_by(CandidateProfileRecord.created_at.desc())
            .limit(1)
        )
        record = self.session.scalar(statement)
        if record is None:
            return None
        return CandidateProfile.model_validate(record)
