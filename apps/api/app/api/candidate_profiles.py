from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.domain import CandidateProfile, CandidateProfileCreate
from app.repositories import CandidateProfileRepository

router = APIRouter(prefix="/candidate-profile", tags=["candidate profile"])


def get_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> CandidateProfileRepository:
    return CandidateProfileRepository(session)


@router.post("", response_model=CandidateProfile, status_code=status.HTTP_201_CREATED)
def create_candidate_profile(
    profile: CandidateProfileCreate,
    repository: Annotated[CandidateProfileRepository, Depends(get_repository)],
) -> CandidateProfile:
    return repository.create(profile)


@router.get("", response_model=CandidateProfile | None)
def get_latest_candidate_profile(
    repository: Annotated[CandidateProfileRepository, Depends(get_repository)],
) -> CandidateProfile | None:
    return repository.get_latest()


@router.get("/{profile_id}", response_model=CandidateProfile)
def get_candidate_profile(
    profile_id: UUID,
    repository: Annotated[CandidateProfileRepository, Depends(get_repository)],
) -> CandidateProfile:
    try:
        return repository.get(profile_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
