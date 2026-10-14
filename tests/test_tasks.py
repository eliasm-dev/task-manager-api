
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_and_retrieve_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Learn pytest",
            "description": "Test my API",
            "completed": False,
        },
    )

    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Learn pytest"

    task_id = task["id"]
    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_missing_task_returns_404():
    response = client.get("/tasks/999999")
    assert response.status_code == 404


def test_invalid_task_returns_422():
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422
