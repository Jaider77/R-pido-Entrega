"""
Tests for notifications service
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


def test_create_notification():
    """Test creating a notification"""
    response = client.post(
        "/api/notificaciones/",
        json={
            "user_id": 1,
            "title": "Test notification",
            "message": "This is a test",
            "recipient": "test@example.com",
            "notification_type": "email",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 201


def test_create_notification_template():
    """Test creating notification template"""
    response = client.post(
        "/api/notificaciones/templates/",
        json={
            "name": "delivery_completed",
            "title_template": "Entrega completada",
            "message_template": "Tu paquete ha sido entregado",
            "notification_type": "email",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 201


def test_get_user_notifications():
    """Test getting user notifications"""
    response = client.get(
        "/api/notificaciones/user/1",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 200


def test_get_user_stats():
    """Test getting user notification stats"""
    response = client.get(
        "/api/notificaciones/stats/user/1",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 200
