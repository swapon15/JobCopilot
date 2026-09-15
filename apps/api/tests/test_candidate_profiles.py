from fastapi.testclient import TestClient


def test_create_and_get_candidate_profile(client: TestClient) -> None:
    payload = {
        "headline": "Principal Software/Data Engineer",
        "summary": "Builds C++, Python, data, and ML platform systems.",
        "target_roles": ["Principal Software Engineer", "AI Platform Engineer"],
        "preferred_locations": ["Remote"],
        "work_preferences": ["Remote", "Strong work-life balance"],
        "sponsorship_required": False,
        "evidence": [
            {
                "project_or_position": "Licensing-data ingestion infrastructure",
                "description": "Built automated ingestion and data-quality workflows.",
                "skills": ["Python", "SQL", "Snowflake"],
                "responsibilities": ["Pipeline design", "Data validation"],
                "measurable_outcomes": ["Reduced processing time from hours to minutes"],
                "experience_type": "direct",
            }
        ],
    }

    create_response = client.post("/candidate-profile", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["headline"] == payload["headline"]
    assert created["evidence"][0]["experience_type"] == "direct"

    get_response = client.get(f"/candidate-profile/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]


def test_get_latest_candidate_profile_returns_none_when_empty(client: TestClient) -> None:
    response = client.get("/candidate-profile")

    assert response.status_code == 200
    assert response.json() is None


def test_update_candidate_profile_replaces_profile_and_evidence(client: TestClient) -> None:
    create_response = client.post(
        "/candidate-profile",
        json={
            "headline": "Principal Engineer",
            "summary": "Original summary",
            "evidence": [
                {
                    "project_or_position": "Original project",
                    "description": "Original evidence",
                    "experience_type": "direct",
                }
            ],
        },
    )
    profile_id = create_response.json()["id"]

    update_response = client.put(
        f"/candidate-profile/{profile_id}",
        json={
            "headline": "Principal Software/Data Engineer",
            "summary": "Updated profile summary",
            "target_roles": ["Staff Software Engineer"],
            "preferred_locations": ["Remote"],
            "work_preferences": ["Remote"],
            "sponsorship_required": False,
            "evidence": [
                {
                    "project_or_position": "Updated project",
                    "description": "Updated evidence",
                    "skills": ["Python"],
                    "responsibilities": ["Automation"],
                    "measurable_outcomes": ["Reduced processing time"],
                    "experience_type": "direct",
                }
            ],
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["headline"] == "Principal Software/Data Engineer"
    assert updated["evidence"][0]["project_or_position"] == "Updated project"
    assert len(updated["evidence"]) == 1
