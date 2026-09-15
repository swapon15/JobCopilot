from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ExperienceType(str, Enum):
    direct = "direct"
    transferable = "transferable"
    knowledge_only = "knowledge_only"
    missing = "missing"


class MatchCategory(str, Enum):
    direct = "direct"
    transferable = "transferable"
    knowledge_only = "knowledge_only"
    missing = "missing"


class JobDecisionState(str, Enum):
    applied = "applied"
    saved = "saved"
    skipped = "skipped"


class CandidateEvidenceBase(BaseModel):
    project_or_position: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    measurable_outcomes: list[str] = Field(default_factory=list)
    experience_type: ExperienceType


class CandidateEvidence(CandidateEvidenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_profile_id: UUID


class CandidateProfileCreate(BaseModel):
    headline: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1)
    target_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    work_preferences: list[str] = Field(default_factory=list)
    sponsorship_required: bool = False
    evidence: list[CandidateEvidenceBase] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    headline: str
    summary: str
    target_roles: list[str]
    preferred_locations: list[str]
    work_preferences: list[str]
    sponsorship_required: bool
    created_at: datetime
    updated_at: datetime
    evidence: list[CandidateEvidence]


class NormalizedRequirement(BaseModel):
    text: str = Field(min_length=1)
    mandatory: bool = True
    match_category: MatchCategory | None = None
    evidence_ids: list[UUID] = Field(default_factory=list)


class JobDescriptionCreate(BaseModel):
    raw_description: str = Field(min_length=1)
    source_url: HttpUrl | None = None
    title: str | None = Field(default=None, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    compensation: str | None = Field(default=None, max_length=200)
    work_mode: str | None = Field(default=None, max_length=100)


class JobDescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    raw_description: str
    source_url: str | None
    title: str | None
    company: str | None
    location: str | None
    compensation: str | None
    work_mode: str | None
    normalized_requirements: list[NormalizedRequirement]
    created_at: datetime
    updated_at: datetime


class JobDecision(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_description_id: UUID
    state: JobDecisionState
    notes: str | None
    created_at: datetime
