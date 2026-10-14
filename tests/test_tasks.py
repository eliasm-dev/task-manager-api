
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app, get_db
from app.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


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


def test_update_task():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original title",
            "description": "Test",
            "completed": False,
        },
    )
    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "completed": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["completed"] is True


def test_delete_task():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Task to delete",
            "description": "",
            "completed": False,
        },
    )
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
