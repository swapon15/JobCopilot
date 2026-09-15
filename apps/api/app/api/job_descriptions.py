from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.domain import JobDescription, JobDescriptionCreate
from app.repositories import JobDescriptionRepository

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> JobDescriptionRepository:
    return JobDescriptionRepository(session)


@router.post("", response_model=JobDescription, status_code=status.HTTP_201_CREATED)
def create_job_description(
    job: JobDescriptionCreate,
    repository: Annotated[JobDescriptionRepository, Depends(get_repository)],
) -> JobDescription:
    return repository.create(job)


@router.get("", response_model=list[JobDescription])
def list_job_descriptions(
    repository: Annotated[JobDescriptionRepository, Depends(get_repository)],
) -> list[JobDescription]:
    return repository.list()


@router.get("/{job_id}", response_model=JobDescription)
def get_job_description(
    job_id: UUID,
    repository: Annotated[JobDescriptionRepository, Depends(get_repository)],
) -> JobDescription:
    try:
        return repository.get(job_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
