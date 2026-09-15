from fastapi.testclient import TestClient


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
