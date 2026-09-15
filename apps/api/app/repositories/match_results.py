from sqlalchemy.orm import Session

from app.db.models import MatchResultRecord
from app.domain import MatchResult


class MatchResultRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, match_result: MatchResult) -> MatchResult:
        record = MatchResultRecord(
            candidate_profile_id=str(match_result.candidate_profile_id),
            job_description_id=str(match_result.job_description_id),
            scores=match_result.scores.model_dump(mode="json"),
            recommendation=match_result.recommendation.value,
            recommendation_score=match_result.recommendation_score,
            recommendation_reason=match_result.recommendation_reason,
            mandatory_gaps=match_result.mandatory_gaps,
            preferred_gaps=match_result.preferred_gaps,
            evidence_matches=[
                evidence_match.model_dump(mode="json")
                for evidence_match in match_result.evidence_matches
            ],
            concise_rationale=match_result.concise_rationale,
            interview_risks=match_result.interview_risks,
            work_preference_conflicts=match_result.work_preference_conflicts,
            model_name=match_result.model_name,
            prompt_version=match_result.prompt_version,
            input_tokens=match_result.input_tokens,
            output_tokens=match_result.output_tokens,
            estimated_cost_usd=match_result.estimated_cost_usd,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return MatchResult.model_validate(record)
