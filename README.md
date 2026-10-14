# TaskFlow API

A RESTful task management API built with Python, FastAPI, SQLAlchemy, and SQLite.

## Features

- Create a task
- Retrieve all tasks
- Retrieve a task by ID
- Update a task
- Delete a task
- Validate incoming data
- Handle missing tasks with HTTP 404 errors
- Store tasks in an SQLite database
- Automated tests using pytest

## Technologies

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn
- Pytest

## Requirements

- Python 3.13 or compatible version
- pip

## Installation

Clone the repository and enter the project directory.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the API

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Open the interactive API documentation:

http://127.0.0.1:8001/docs

## Run Tests

```powershell
python -m pytest -v
```

## Project Structure

```text
task-manager-api/
├── app/
│   ├── main.py
│   ├── database.py
│   └── models.py
├── tests/
│   └── test_tasks.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Purpose

This project demonstrates foundational backend development skills, including REST API design, database integration, input validation, error handling, and automated testing.

## Status

Completed foundational CRUD functionality and initial automated tests.
