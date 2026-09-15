from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import JobDescriptionRecord
from app.domain import JobDescription, JobDescriptionCreate


class JobDescriptionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, job: JobDescriptionCreate) -> JobDescription:
        record = JobDescriptionRecord(
            raw_description=job.raw_description,
            source_url=str(job.source_url) if job.source_url else None,
            title=job.title,
            company=job.company,
            location=job.location,
            compensation=job.compensation,
            work_mode=job.work_mode,
            normalized_requirements=[],
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
