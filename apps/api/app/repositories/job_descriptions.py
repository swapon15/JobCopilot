from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import JobDescriptionRecord
from app.domain import JobDescription, JobDescriptionCreate
from app.services.job_normalizer import extract_requirements, normalize_job_description


class JobDescriptionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, job: JobDescriptionCreate) -> JobDescription:
        normalized_job = normalize_job_description(job)
        normalized_requirements = extract_requirements(normalized_job.raw_description)
        record = JobDescriptionRecord(
            raw_description=normalized_job.raw_description,
            source_url=str(normalized_job.source_url) if normalized_job.source_url else None,
            title=normalized_job.title,
            company=normalized_job.company,
            location=normalized_job.location,
            compensation=normalized_job.compensation,
            work_mode=normalized_job.work_mode,
            normalized_requirements=[
                requirement.model_dump(mode="json") for requirement in normalized_requirements
            ],
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return JobDescription.model_validate(record)

    def get(self, job_id: UUID) -> JobDescription:
        record = self.session.get(JobDescriptionRecord, str(job_id))
        if record is None:
            raise LookupError(f"Job description {job_id} was not found")
        return JobDescription.model_validate(record)

    def list(self) -> list[JobDescription]:
        records = self.session.scalars(
            select(JobDescriptionRecord).order_by(JobDescriptionRecord.created_at.desc())
        ).all()
        return [JobDescription.model_validate(record) for record in records]
