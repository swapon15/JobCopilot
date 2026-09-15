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
