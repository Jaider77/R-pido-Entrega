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


def test_reply_to_notification():
    """Test replying to a notification and preserving thread relationships"""
    create_response = client.post(
        "/api/notificaciones/",
        json={
            "user_id": 2,
            "title": "Original mensaje",
            "message": "Mensaje inicial",
            "recipient": "2",
            "notification_type": "in_app",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert create_response.status_code == 201
    original = create_response.json()

    reply_response = client.post(
        "/api/notificaciones/",
        json={
            "user_id": 1,
            "recipient": "1",
            "parent_id": original["id"],
            "title": "Re: Original mensaje",
            "message": "Respuesta al mensaje",
            "notification_type": "in_app",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert reply_response.status_code == 201
    reply = reply_response.json()
    assert reply["parent_id"] == original["id"]
    assert reply["thread_id"] == original["thread_id"] or reply["thread_id"] == original["id"]

    thread_response = client.get(
        f"/api/notificaciones/threads/{reply['thread_id']}",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert thread_response.status_code == 200
    thread_messages = thread_response.json()
    assert len(thread_messages) == 2
    assert thread_messages[0]["id"] == original["id"]
    assert thread_messages[1]["parent_id"] == original["id"]


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
