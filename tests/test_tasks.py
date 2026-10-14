
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import (
    app,
    get_db,
    password_hash,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)
from app.models import User


TEST_USER_ID = 1

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


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

#helper function to help fixture
@pytest.fixture
def authenticated_client(client):
    db = TestingSessionLocal()

    try:
        user = User(
            id=TEST_USER_ID,
            email="test@example.com",
            hashed_password=password_hash.hash("TestPassword123!"),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    token = jwt.encode(
        {
            "sub": str(TEST_USER_ID),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    client.headers["Authorization"] = f"Bearer {token}"
    return client


def create_test_user(user_id: int, email: str):
    db = TestingSessionLocal()

    try:
        user = User(
            id=user_id,
            email=email,
            hashed_password=password_hash.hash("TestPassword123!"),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return f"Bearer {token}"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_and_retrieve_task(authenticated_client):
    response = authenticated_client.post(
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
    response = authenticated_client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_missing_task_returns_404(authenticated_client):
    response = authenticated_client.get("/tasks/999999")
    assert response.status_code == 404


def test_invalid_task_returns_422(authenticated_client):
    response = authenticated_client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_update_task(authenticated_client):
    create_response = authenticated_client.post(
        "/tasks",
        json={
            "title": "Original title",
            "description": "Test",
            "completed": False,
        },
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = authenticated_client.put(
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


def test_delete_task(authenticated_client):
    create_response = authenticated_client.post(
        "/tasks",
        json={
            "title": "Task to delete",
            "description": "",
            "completed": False,
        },
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = authenticated_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    response = authenticated_client.get(f"/tasks/{task_id}")
    assert response.status_code == 404


def test_title_cannot_exceed_100_characters(authenticated_client):
    response = authenticated_client.post(
        "/tasks",
        json={
            "title": "T" * 101,
            "description": "Test",
            "completed": False,
        },
    )
    assert response.status_code == 422


def test_description_cannot_exceed_500_characters(authenticated_client):
    response = authenticated_client.post(
        "/tasks",
        json={
            "title": "Valid title",
            "description": "D" * 501,
            "completed": False,
        },
    )
    assert response.status_code == 422


def test_empty_title_is_rejected(authenticated_client):
    response = authenticated_client.post(
        "/tasks",
        json={
            "title": "",
            "description": "Test",
            "completed": False,
        },
    )
    assert response.status_code == 422


def test_deleting_missing_task_returns_404(authenticated_client):
    response = authenticated_client.delete("/tasks/999999")
    assert response.status_code == 404


def test_list_tasks_respects_limit(authenticated_client):
    for i in range(3):
        response = authenticated_client.post(
            "/tasks",
            json={
                "title": f"Task {i}",
                "description": "Pagination test",
                "completed": False,
            },
        )
        assert response.status_code == 201

    response = authenticated_client.get("/tasks?skip=0&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tasks_respects_skip(authenticated_client):
    for i in range(3):
        response = authenticated_client.post(
            "/tasks",
            json={
                "title": f"Task {i}",
                "description": "Pagination test",
                "completed": False,
            },
        )
        assert response.status_code == 201

    response = authenticated_client.get("/tasks?skip=2&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_tasks_rejects_invalid_pagination(authenticated_client):
    assert authenticated_client.get("/tasks?skip=-1").status_code == 422
    assert authenticated_client.get("/tasks?limit=101").status_code == 422


def test_patch_task_updates_only_provided_fields(authenticated_client):
    create_response = authenticated_client.post(
        "/tasks",
        json={
            "title": "Original title",
            "description": "Original description",
            "completed": False,
        },
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "Original title"
    assert response.json()["description"] == "Original description"


def test_patch_missing_task_returns_404(authenticated_client):
    response = authenticated_client.patch(
        "/tasks/999999",
        json={"completed": True},
    )
    assert response.status_code == 404


def test_patch_empty_body_returns_422(authenticated_client):
    create_response = authenticated_client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Testing empty patch",
            "completed": False,
        },
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/tasks/{task_id}",
        json={},
    )
    assert response.status_code == 422



def test_users_cannot_access_each_others_tasks(authenticated_client):
    # User A creates a task
    create_response = authenticated_client.post(
        "/tasks",
        json={
            "title": "User A private task",
            "description": "This task belongs to User A",
            "completed": False,
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Create User B and switch to User B's token

    # Create User B
    user_b_token = create_test_user(2, "userb@example.com")

    # Use a separate client authenticated as User B
    with TestClient(
        app,
        headers={"Authorization": user_b_token},
    ) as user_b_client:

        # User B should not see User A's tasks
        list_response = user_b_client.get("/tasks")
        assert list_response.status_code == 200
        assert list_response.json() == []

        # User B cannot view User A's task
        assert user_b_client.get(
            f"/tasks/{task_id}"
        ).status_code == 404

        # User B cannot update User A's task
        assert user_b_client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Changed by User B",
                "description": "Unauthorized change",
                "completed": True,
            },
        ).status_code == 404

        # User B cannot partially update User A's task
        assert user_b_client.patch(
            f"/tasks/{task_id}",
            json={"completed": True},
        ).status_code == 404

        # User B cannot delete User A's task
        assert user_b_client.delete(
            f"/tasks/{task_id}"
        ).status_code == 404


def test_list_tasks_requires_authentication(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_list_tasks_rejects_invalid_token(client):
    client.headers["Authorization"] = "Bearer invalid-token"

    response = client.get("/tasks")

    assert response.status_code == 401



def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["message"] == "User registered successfully"
    assert "id" in data


def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
    }

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_user(client):
    client.post(
        "/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "TestPassword123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert "access_token" in data


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "TestPassword123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_token_can_create_task(client):
    # Register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "tokenuser@example.com",
            "password": "TestPassword123!",
        },
    )
    assert register_response.status_code == 201

    # Log in and obtain a token
    login_response = client.post(
        "/auth/login",
        json={
            "email": "tokenuser@example.com",
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Use the token to create a task
    response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "My authenticated task",
            "description": "Created using a real login token",
            "completed": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "My authenticated task"
