from fastapi.testclient import TestClient

from app.api.job_descriptions import get_matcher
from app.domain import MatchResult, RecommendationAction
from app.services.matcher import FakeJobMatcher


def test_create_and_get_job_description(client: TestClient) -> None:
    payload = {
        "raw_description": "\n".join(
            [
                "Staff Software Engineer",
                "Company: Example Co",
                "Location: Remote - US",
                "Compensation: $180,000 - $220,000",
                "Requirements:",
                "- 8+ years of Python, SQL, and platform engineering experience",
                "- Experience with distributed systems",
                "Preferred Qualifications:",
                "- Familiarity with ML platforms is preferred",
            ]
        ),
        "company": "Example Co",
    }

    create_response = client.post("/jobs", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Staff Software Engineer"
    assert created["location"] == "Remote - US"
    assert created["compensation"] == "$180,000 - $220,000"
    assert created["work_mode"] == "remote"
    assert created["normalized_requirements"][0] == {
        "text": "8+ years of Python, SQL, and platform engineering experience",
        "mandatory": True,
        "match_category": None,
        "evidence_ids": [],
    }
    assert created["normalized_requirements"][2]["mandatory"] is False

    get_response = client.get(f"/jobs/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["raw_description"] == payload["raw_description"]


def test_list_job_descriptions(client: TestClient) -> None:
    response = client.get("/jobs")

    assert response.status_code == 200
    assert response.json() == []


def test_create_job_description_respects_explicit_fields(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        json={
            "raw_description": "Backend role\nRequirements:\n- Must have Python experience",
            "title": "Senior Backend Engineer",
            "location": "Hybrid - New York",
            "work_mode": "hybrid",
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Senior Backend Engineer"
    assert created["location"] == "Hybrid - New York"
    assert created["work_mode"] == "hybrid"


def test_create_match_preview_requires_candidate_profile(client: TestClient) -> None:
    job_response = client.post(
        "/jobs",
        json={
            "raw_description": (
                "Staff Software Engineer\nRequirements:\n- Must have Python experience"
            ),
        },
    )
    job_id = job_response.json()["id"]

    response = client.post(f"/jobs/{job_id}/match")

    assert response.status_code == 409
    assert "Create a candidate profile" in response.json()["detail"]


def test_create_match_preview_with_fake_matcher(client: TestClient) -> None:
    client.post(
        "/candidate-profile",
        json={
            "headline": "Principal Software/Data Engineer",
            "summary": "Builds Python and data platforms.",
            "work_preferences": ["Remote"],
            "evidence": [
                {
                    "project_or_position": "Data platform",
                    "description": "Built Python automation and SQL data pipelines.",
                    "skills": ["Python", "SQL"],
                    "responsibilities": ["Pipeline design"],
                    "measurable_outcomes": ["Reduced processing time"],
                    "experience_type": "direct",
                }
            ],
        },
    )
    job_response = client.post(
        "/jobs",
        json={
            "raw_description": "\n".join(
                [
                    "Staff Software Engineer",
                    "Location: Remote - US",
                    "Requirements:",
                    "- Must have Python experience",
                    "- Experience with Kubernetes",
                ]
            )
        },
    )
    job_id = job_response.json()["id"]

    response = client.post(f"/jobs/{job_id}/match")

    assert response.status_code == 201
    match = response.json()
    assert match["model_name"] == "fake-local-matcher"
    assert match["prompt_version"] == "fake-match-v1"
    assert match["input_tokens"] is None
    assert match["output_tokens"] is None
    assert match["estimated_cost_usd"] is None
    assert match["recommendation"] == "SKIP"
    assert match["recommendation_score"] == 74
    assert (
        match["recommendation_reason"]
        == "SKIP because one or more mandatory requirements are missing."
    )
    assert match["work_preference_conflicts"] == []
    assert match["scores"]["technical"] >= 55
    assert match["evidence_matches"][0]["match_category"] == "direct"


def test_recommendation_policy_overrides_matcher_threshold_decision(
    client: TestClient,
) -> None:
    class OverconfidentMatcher(FakeJobMatcher):
        model_name = "overconfident-test-matcher"

        def match(self, profile, job) -> MatchResult:  # type: ignore[no-untyped-def]
            match_result = super().match(profile, job)
            return match_result.model_copy(
                update={
                    "recommendation": RecommendationAction.apply,
                    "recommendation_score": 100,
                    "recommendation_reason": "Matcher tried to force an APPLY decision.",
                    "mandatory_gaps": ["Must have production Kubernetes experience"],
                }
            )

    client.app.dependency_overrides[get_matcher] = OverconfidentMatcher
    client.post(
        "/candidate-profile",
        json={
            "headline": "Principal Software/Data Engineer",
            "summary": "Builds Python and data platforms.",
            "evidence": [
                {
                    "project_or_position": "Data platform",
                    "description": "Built Python automation and SQL data pipelines.",
                    "skills": ["Python", "SQL"],
                    "responsibilities": ["Pipeline design"],
                    "measurable_outcomes": ["Reduced processing time"],
                    "experience_type": "direct",
                }
            ],
        },
    )
    job_response = client.post(
        "/jobs",
        json={
            "raw_description": "\n".join(
                [
                    "Staff Software Engineer",
                    "Requirements:",
                    "- Must have production Kubernetes experience",
                ]
            )
        },
    )
    job_id = job_response.json()["id"]

    response = client.post(f"/jobs/{job_id}/match")

    assert response.status_code == 201
    match = response.json()
    assert match["model_name"] == "overconfident-test-matcher"
    assert match["recommendation"] == "SKIP"
    assert match["recommendation_score"] == 62
    assert match["recommendation_reason"] == (
        "SKIP because one or more mandatory requirements are missing."
    )
    assert match["mandatory_gaps"] == ["Must have production Kubernetes experience"]


def test_recommendation_policy_preserves_experience_classifications(client: TestClient) -> None:
    client.post(
        "/candidate-profile",
        json={
            "headline": "Platform Engineer",
            "summary": "Has several kinds of evidence.",
            "evidence": [
                {
                    "project_or_position": "Direct platform work",
                    "description": "Built Python services.",
                    "skills": ["Python"],
                    "responsibilities": [],
                    "measurable_outcomes": [],
                    "experience_type": "direct",
                },
                {
                    "project_or_position": "Transferable systems work",
                    "description": "Operated Kubernetes-adjacent deployment tooling.",
                    "skills": ["Kubernetes"],
                    "responsibilities": [],
                    "measurable_outcomes": [],
                    "experience_type": "transferable",
                },
                {
                    "project_or_position": "Security coursework",
                    "description": "Studied compliance controls.",
                    "skills": ["Compliance"],
                    "responsibilities": [],
                    "measurable_outcomes": [],
                    "experience_type": "knowledge_only",
                },
            ],
        },
    )
    job_response = client.post(
        "/jobs",
        json={
            "raw_description": "\n".join(
                [
                    "Platform Engineer",
                    "Requirements:",
                    "- Must have Python experience",
                    "- Must have Kubernetes experience",
                    "- Must have compliance experience",
                    "- Must have Rust experience",
                ]
            )
        },
    )

    response = client.post(f"/jobs/{job_response.json()['id']}/match")

    assert response.status_code == 201
    categories = [match["match_category"] for match in response.json()["evidence_matches"]]
    assert categories == ["direct", "transferable", "knowledge_only", "missing"]


def test_create_match_preview_includes_work_preference_conflicts(client: TestClient) -> None:
    client.post(
        "/candidate-profile",
        json={
            "headline": "Remote-first Engineer",
            "summary": "Prefers remote teams.",
            "work_preferences": ["Remote"],
            "evidence": [
                {
                    "project_or_position": "Platform work",
                    "description": "Built Python services.",
                    "skills": ["Python"],
                    "responsibilities": [],
                    "measurable_outcomes": [],
                    "experience_type": "direct",
                }
            ],
        },
    )
    job_response = client.post(
        "/jobs",
        json={
            "raw_description": "\n".join(
                [
                    "Platform Engineer",
                    "Work mode: onsite",
                    "Requirements:",
                    "- Must have Python experience",
                ]
            ),
            "work_mode": "onsite",
        },
    )

    response = client.post(f"/jobs/{job_response.json()['id']}/match")

    assert response.status_code == 201
    assert response.json()["work_preference_conflicts"] == [
        "Job is listed as onsite, but profile preferences are: Remote."
    ]


def test_create_job_decision(client: TestClient) -> None:
    job_response = client.post(
        "/jobs",
        json={"raw_description": "Staff Software Engineer\nRequirements:\n- Must have Python"},
    )
    job_id = job_response.json()["id"]

    response = client.post(
        f"/jobs/{job_id}/decision",
        json={"state": "saved", "notes": "Worth reviewing after matching."},
    )

    assert response.status_code == 201
    decision = response.json()
    assert decision["job_description_id"] == job_id
    assert decision["state"] == "saved"
    assert decision["notes"] == "Worth reviewing after matching."


def test_create_job_decision_requires_existing_job(client: TestClient) -> None:
    response = client.post(
        "/jobs/00000000-0000-0000-0000-000000000000/decision",
        json={"state": "skipped"},
    )

    assert response.status_code == 404
