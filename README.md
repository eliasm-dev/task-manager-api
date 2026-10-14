# TaskFlow API
![TaskFlow API Tests](https://github.com/eliasm-dev/task-manager-api/actions/workflows/tests.yml/badge.svg)

A RESTful task management API built with **FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication**. This project demonstrates backend development fundamentals, secure user authentication, database migrations, and automated testing.

## Features

- **User registration and login** with password hashing
- **JWT authentication** for protected endpoints
- **Task CRUD operations** — create, read, update, and delete tasks
- **Task ownership** — users can access and manage only their own tasks
- **PostgreSQL database** for persistent storage
- **Alembic migrations** for database schema management
- **Request validation** using Pydantic
- **Automated tests** using pytest and an isolated SQLite test database
- **Interactive API documentation** with Swagger UI

## Technologies

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- PyJWT
- pwdlib
- Pydantic
- Uvicorn
- Pytest

## Requirements

- Python 3.13 or compatible
- PostgreSQL
- pip

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/eliasm-dev/task-manager-api.git
cd task-manager-api
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/taskflow
JWT_SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET
```

Replace the database username and password with your local PostgreSQL credentials. Generate a strong, private JWT secret before running the application.

**Never commit your `.env` file or expose your real credentials.**

### 5. Run database migrations

```powershell
python -m alembic upgrade head
```

### 6. Start the API

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

The API will be available at:

- API root: http://127.0.0.1:8001/
- Health check: http://127.0.0.1:8001/health
- Swagger UI: http://127.0.0.1:8001/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Log in and receive a JWT |
| GET | `/tasks` | List the authenticated user's tasks |
| POST | `/tasks` | Create a task |
| GET | `/tasks/{task_id}` | Retrieve an owned task |
| PUT | `/tasks/{task_id}` | Replace an owned task |
| PATCH | `/tasks/{task_id}` | Partially update an owned task |
| DELETE | `/tasks/{task_id}` | Delete an owned task |

Task endpoints require authentication. Users cannot access another user's tasks through the task endpoints.

## Running Tests

Run the automated test suite:

```powershell
python -m pytest -v
```

Tests use an isolated SQLite database, so they do not need your PostgreSQL database to run.

## Database Migrations

Check migration status:

```powershell
python -m alembic current
```

Check whether model changes require a migration:

```powershell
python -m alembic check
```

## Project Structure

```text
task-manager-api/
├── app/
│   ├── main.py
│   ├── database.py
│   └── models.py
├── migrations/
│   └── versions/
├── tests/
│   └── test_tasks.py
├── alembic.ini
├── requirements.txt
└── README.md
```

## Project Goals

This project is part of my backend development learning journey. It helps me practice REST API design, relational database integration, authentication, database migrations, and automated testing.

## Current Status

Core task management, user authentication, task ownership, database migrations, and automated tests are implemented. Further improvements may include pagination enhancements, deployment, and API rate limiting.