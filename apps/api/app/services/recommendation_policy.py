from app.domain import MatchResult, RecommendationAction


def apply_recommendation_policy(match_result: MatchResult) -> MatchResult:
    score = _overall_score(match_result)
    material_mandatory_gaps = bool(match_result.mandatory_gaps)

    if material_mandatory_gaps:
        recommendation = RecommendationAction.skip
        reason = "SKIP because one or more mandatory requirements are missing."
    elif score >= 80:
        recommendation = RecommendationAction.apply
        reason = "APPLY because the overall score is at least 80 with no mandatory gaps."
    elif score >= 65:
        recommendation = RecommendationAction.consider
        reason = "CONSIDER because the overall score is between 65 and 79."
    else:
        recommendation = RecommendationAction.skip
        reason = "SKIP because the overall score is below 65."

    return match_result.model_copy(
        update={
            "recommendation": recommendation,
            "recommendation_score": score,
            "recommendation_reason": reason,
        }
    )


def _overall_score(match_result: MatchResult) -> int:
    scores = match_result.scores
    return round(
        (
            scores.technical
            + scores.direct_experience
            + scores.level
            + scores.leadership
            + scores.preference
        )
        / 5
    )
