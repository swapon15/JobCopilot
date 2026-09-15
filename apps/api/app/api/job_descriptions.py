from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.domain import (
    JobDecision,
    JobDecisionCreate,
    JobDescription,
    JobDescriptionCreate,
    MatchResult,
)
from app.repositories import (
    CandidateProfileRepository,
    JobDecisionRepository,
    JobDescriptionRepository,
    MatchResultRepository,
)
from app.services import JobMatcher, apply_recommendation_policy, get_matcher

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> JobDescriptionRepository:
    return JobDescriptionRepository(session)


def get_candidate_profile_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> CandidateProfileRepository:
    return CandidateProfileRepository(session)


def get_match_result_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> MatchResultRepository:
    return MatchResultRepository(session)


def get_job_decision_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> JobDecisionRepository:
    return JobDecisionRepository(session)


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


@router.post("/{job_id}/match", response_model=MatchResult, status_code=status.HTTP_201_CREATED)
def create_match_preview(
    job_id: UUID,
    job_repository: Annotated[JobDescriptionRepository, Depends(get_repository)],
    candidate_repository: Annotated[
        CandidateProfileRepository, Depends(get_candidate_profile_repository)
    ],
    match_repository: Annotated[MatchResultRepository, Depends(get_match_result_repository)],
    matcher: Annotated[JobMatcher, Depends(get_matcher)],
) -> MatchResult:
    try:
        job = job_repository.get(job_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    candidate_profile = candidate_repository.get_latest()
    if candidate_profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Create a candidate profile before generating a match preview.",
        )

    match_result = apply_recommendation_policy(matcher.match(candidate_profile, job))
    return match_repository.create(match_result)


@router.post(
    "/{job_id}/decision",
    response_model=JobDecision,
    status_code=status.HTTP_201_CREATED,
)
def create_job_decision(
    job_id: UUID,
    decision: JobDecisionCreate,
    job_repository: Annotated[JobDescriptionRepository, Depends(get_repository)],
    decision_repository: Annotated[JobDecisionRepository, Depends(get_job_decision_repository)],
) -> JobDecision:
    try:
        job_repository.get(job_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return decision_repository.create(job_id, decision)
