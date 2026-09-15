from fastapi.testclient import TestClient


def test_create_and_get_job_description(client: TestClient) -> None:
    payload = {
        "raw_description": "We need a Staff Software Engineer with Python, SQL, and platform work.",
        "title": "Staff Software Engineer",
        "company": "Example Co",
        "location": "Remote - US",
        "work_mode": "remote",
    }

    create_response = client.post("/jobs", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Staff Software Engineer"
    assert created["normalized_requirements"] == []

    get_response = client.get(f"/jobs/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["raw_description"] == payload["raw_description"]


def test_list_job_descriptions(client: TestClient) -> None:
    response = client.get("/jobs")

    assert response.status_code == 200
    assert response.json() == []
