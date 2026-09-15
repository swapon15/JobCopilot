from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from app.domain import (
    CandidateEvidence,
    CandidateProfile,
    JobDescription,
    MatchCategory,
    MatchEvidence,
    MatchResult,
    MatchScore,
)


class JobMatcher(Protocol):
    model_name: str
    prompt_version: str

    def match(self, profile: CandidateProfile, job: JobDescription) -> MatchResult:
        pass


class FakeJobMatcher:
    model_name = "fake-local-matcher"
    prompt_version = "fake-match-v1"

    def match(self, profile: CandidateProfile, job: JobDescription) -> MatchResult:
        evidence_matches = [
            self._match_requirement(requirement.text, profile.evidence)
            for requirement in job.normalized_requirements
        ]
        mandatory_gaps = [
            match.requirement_text
            for requirement, match in zip(
                job.normalized_requirements, evidence_matches, strict=False
            )
            if requirement.mandatory and match.match_category == MatchCategory.missing
        ]
        preferred_gaps = [
            match.requirement_text
            for requirement, match in zip(
                job.normalized_requirements, evidence_matches, strict=False
            )
            if not requirement.mandatory and match.match_category == MatchCategory.missing
        ]
        direct_matches = sum(
            1 for match in evidence_matches if match.match_category == MatchCategory.direct
        )
        total_requirements = max(len(evidence_matches), 1)
        technical_score = min(100, 55 + round((direct_matches / total_requirements) * 35))

        return MatchResult(
            id=_EMPTY_UUID,
            candidate_profile_id=profile.id,
            job_description_id=job.id,
            scores=MatchScore(
                technical=technical_score,
                direct_experience=70 if direct_matches else 45,
                level=75,
                leadership=70 if profile.evidence else 50,
                preference=80 if (job.work_mode or "").lower() == "remote" else 65,
            ),
            mandatory_gaps=mandatory_gaps,
            preferred_gaps=preferred_gaps,
            evidence_matches=evidence_matches,
            concise_rationale=(
                "Fake matcher preview based on keyword overlap between normalized requirements "
                "and candidate evidence. This is deterministic and not an LLM call."
            ),
            interview_risks=[
                "Fake matcher may overstate fit when keywords overlap without deep context.",
                "Direct versus transferable experience should be reviewed manually.",
            ],
            model_name=self.model_name,
            prompt_version=self.prompt_version,
            input_tokens=None,
            output_tokens=None,
            estimated_cost_usd=None,
            created_at=_EMPTY_DATETIME,
        )

    def _match_requirement(
        self, requirement_text: str, evidence: list[CandidateEvidence]
    ) -> MatchEvidence:
        requirement_terms = _terms(requirement_text)
        best_evidence = max(
            evidence,
            key=lambda item: len(
                requirement_terms & _terms(" ".join([item.description, *item.skills]))
            ),
            default=None,
        )
        if best_evidence is None:
            return MatchEvidence(
                requirement_text=requirement_text,
                match_category=MatchCategory.missing,
                evidence_ids=[],
                rationale="No candidate evidence is available yet.",
            )

        overlap = requirement_terms & _terms(
            " ".join([best_evidence.description, *best_evidence.skills])
        )
        if overlap:
            return MatchEvidence(
                requirement_text=requirement_text,
                match_category=MatchCategory(best_evidence.experience_type.value),
                evidence_ids=[best_evidence.id],
                rationale=f"Matched on: {', '.join(sorted(overlap)[:5])}.",
            )
        return MatchEvidence(
            requirement_text=requirement_text,
            match_category=MatchCategory.missing,
            evidence_ids=[],
            rationale="No meaningful keyword overlap found in available evidence.",
        )


def _terms(text: str) -> set[str]:
    return {
        term.lower() for term in text.replace("/", " ").replace(",", " ").split() if len(term) > 2
    }


_EMPTY_UUID = UUID("00000000-0000-0000-0000-000000000000")
_EMPTY_DATETIME = datetime.fromtimestamp(0, tz=timezone.utc)


def get_matcher() -> JobMatcher:
    return FakeJobMatcher()
