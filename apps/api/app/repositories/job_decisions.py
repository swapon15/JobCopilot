from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import JobDecisionRecord
from app.domain import JobDecision, JobDecisionCreate


class JobDecisionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, job_id: UUID, decision: JobDecisionCreate) -> JobDecision:
        record = JobDecisionRecord(
            job_description_id=str(job_id),
            state=decision.state.value,
            notes=decision.notes,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return JobDecision.model_validate(record)
