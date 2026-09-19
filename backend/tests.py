import sqlite3

import pytest
from fastapi.testclient import TestClient
from app.config import settings
# Import the FastAPI app and the SQLite database helpers.
from main import app
from sql_data import init_db


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    database_path = tmp_path_factory.mktemp("data") / "test.db"
    original_database_path = settings.DB_FILE
    settings.DB_FILE = str(database_path)

    with sqlite3.connect(settings.DB_FILE) as connection:
        init_db(connection.cursor())

    with TestClient(app) as c:
        yield c

    settings.DB_FILE = original_database_path


# --- TEST SUITE ---

# User Auth Tests
def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword",
        },
    )
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "user_id" in data

def test_login_user(client):
    response = client.post(
        "/users/login",
        data={"username": "testuser", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_me(client):
    # Login to retrieve access token
    login_res = client.post(
        "/users/login",
        data={"username": "testuser", "password": "securepassword"}
    )
    token = login_res.json()["access_token"]
    
    # Fetch current user profile
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


# Threads & Chat Endpoints Tests
def test_create_thread(client):
    login_res = client.post("/users/login", data={"username": "testuser", "password": "securepassword"})
    token = login_res.json()["access_token"]
    
    response = client.post(
        "/create_threads",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert "thread_id" in response.json()

def test_list_threads(client):
    login_res = client.post("/users/login", data={"username": "testuser", "password": "securepassword"})
    token = login_res.json()["access_token"]

    response = client.get(
        "/threads",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_chat(client):
    login_res = client.post("/users/login", data={"username": "testuser", "password": "securepassword"})
    token = login_res.json()["access_token"]

    response = client.post(
        "/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"thread_id": "test-thread-123", "question": "Hello vector store"}
    )
    assert response.status_code == 200


# Document Upload Test
def test_upload_document(client):
    login_res = client.post(
        "/users/login",
        data={"username": "testuser", "password": "securepassword"},
    )
    token = login_res.json()["access_token"]
    file_payload = {
        "files": ("test.pdf", b"%PDF-1.4 dummy content", "application/pdf")
    }
    response = client.post(
        "/upload-document",
        headers={"Authorization": f"Bearer {token}"},
        files=file_payload,
    )
    assert response.status_code == 201