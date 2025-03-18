# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.core import Base
from app.config import SQLALCHEMY_DATABASE_URI

# Create test database engine
engine = create_engine(SQLALCHEMY_DATABASE_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    # Create the test database and tables
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        # Clean up the test database
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

def test_create_project(client, test_db):
    # Test creating a new project
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"

def test_create_duplicate_project(client, test_db):
    # Test creating a project with duplicate name
    project_data = {"name": "Test Project", "description": "Test Description"}
    
    # Create first project
    response = client.post("/api/v1/projects/", json=project_data)
    assert response.status_code == 200
    
    # Try to create duplicate project
    response = client.post("/api/v1/projects/", json=project_data)
    assert response.status_code == 422
    assert "already exists" in response.json()["detail"][0]["msg"]

def test_get_project(client, test_db):
    # Create a project first
    create_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "Test Description"}
    )
    project_id = create_response.json()["id"]
    
    # Test getting the project
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"

def test_get_nonexistent_project(client, test_db):
    # Test getting a project that doesn't exist
    response = client.get("/api/v1/projects/999")
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"][0]["msg"]

def test_healthcheck(client):
    # Test the healthcheck endpoint
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}