"""
Tests for service3
"""

import pytest
from app.database import get_db
from app.main import app
from app.models import Base
from app.routes import verify_auth_token
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override get_db for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_auth_token] = lambda: {"sub": 1}

client = TestClient(app)

# Mock token for testing
MOCK_TOKEN = (
    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjo5OTk5OTk5OTk5fQ.test"
)


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up database before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_item():
    """Test creating an item"""
    response = client.post(
        "/api/service3/items",
        json={
            "name": "Test Item",
            "description": "This is a test item",
            "status": "active",
            "owner_id": 1,
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 201


def test_list_items():
    """Test listing items"""
    response = client.get(
        "/api/service3/items",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 200


def test_get_owner_stats():
    """Test getting owner statistics"""
    response = client.get(
        "/api/service3/stats/owner/1",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 200
