"""
Tests for routes service
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
app.dependency_overrides[verify_auth_token] = lambda: {"sub": 1, "role": "repartidor"}

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


def test_create_repartidor():
    """Test creating a repartidor"""
    response = client.post(
        "/api/rutas/repartidores",
        json={
            "phone": "1234567890",
            "vehicle_type": "motorcycle",
            "license_plate": "ABC123",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 201


def test_create_ruta():
    """Test creating a route"""
    create_repartidor_response = client.post(
        "/api/rutas/repartidores",
        json={
            "phone": "1234567890",
            "vehicle_type": "motorcycle",
            "license_plate": "ABC123",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert create_repartidor_response.status_code == 201

    response = client.post(
        "/api/rutas/rutas",
        json={
            "repartidor_id": 1,
            "delivery_id": 1,
            "origin_latitude": 10.5,
            "origin_longitude": -20.5,
            "destination_latitude": 10.6,
            "destination_longitude": -20.6,
            "notes": "Test delivery",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 201


def test_list_rutas():
    """Test listing routes"""
    response = client.get(
        "/api/rutas/rutas",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 200


def test_user_can_create_route_without_repartidor():
    """Test user role can create a route without assigning a repartidor"""
    original_override = app.dependency_overrides.get(verify_auth_token)
    app.dependency_overrides[verify_auth_token] = lambda: {"sub": 2, "role": "user"}
    try:
        response = client.post(
            "/api/rutas/rutas",
            json={
                "delivery_id": 99,
                "origin_latitude": 1.1,
                "origin_longitude": -1.1,
                "destination_latitude": 1.2,
                "destination_longitude": -1.2,
                "notes": "Ruta creada por el usuario",
            },
            headers={"Authorization": MOCK_TOKEN},
        )
        assert response.status_code == 201
        assert response.json()["created_by_user_id"] == 2
        assert response.json()["repartidor_id"] is None

        list_response = client.get(
            "/api/rutas/rutas",
            headers={"Authorization": MOCK_TOKEN},
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["created_by_user_id"] == 2
    finally:
        if original_override is not None:
            app.dependency_overrides[verify_auth_token] = original_override
        else:
            app.dependency_overrides.pop(verify_auth_token, None)


def test_create_repartidor_profile():
    """Test creating repartidor profile from authenticated role"""
    response = client.post(
        "/api/rutas/repartidores",
        json={
            "phone": "1234567890",
            "vehicle_type": "motorcycle",
            "license_plate": "ABC123",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 201
    assert response.json()["user_id"] == 1
    assert response.json()["vehicle_type"] == "motorcycle"


def test_get_my_repartidor_profile():
    """Test fetching authenticated repartidor profile"""
    client.post(
        "/api/rutas/repartidores",
        json={
            "phone": "1234567890",
            "vehicle_type": "motorcycle",
            "license_plate": "ABC123",
        },
        headers={"Authorization": MOCK_TOKEN},
    )

    response = client.get(
        "/api/rutas/repartidores/me",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == 1
    assert response.json()["vehicle_type"] == "motorcycle"


def test_get_repartidor_stats():
    """Test getting repartidor statistics"""
    response = client.get(
        "/api/rutas/stats/repartidor/1",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response.status_code == 200


def test_route_status_history():
    """Test route status changes and status history persistence"""
    create_repartidor_response = client.post(
        "/api/rutas/repartidores",
        json={
            "phone": "1234567890",
            "vehicle_type": "motorcycle",
            "license_plate": "ABC123",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert create_repartidor_response.status_code == 201

    create_ruta_response = client.post(
        "/api/rutas/rutas",
        json={
            "repartidor_id": 1,
            "delivery_id": 1,
            "origin_latitude": 10.5,
            "origin_longitude": -20.5,
            "destination_latitude": 10.6,
            "destination_longitude": -20.6,
            "notes": "Test delivery",
        },
        headers={"Authorization": MOCK_TOKEN},
    )
    assert create_ruta_response.status_code == 201

    response_in_transit = client.put(
        "/api/rutas/rutas/1",
        json={"status": "in_transit"},
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response_in_transit.status_code == 200
    assert response_in_transit.json()["status"] == "in_transit"

    response_delivered = client.put(
        "/api/rutas/rutas/1",
        json={"status": "delivered"},
        headers={"Authorization": MOCK_TOKEN},
    )
    assert response_delivered.status_code == 200
    assert response_delivered.json()["status"] == "delivered"

    history_response = client.get(
        "/api/rutas/rutas/1/status-history",
        headers={"Authorization": MOCK_TOKEN},
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 2
    assert history[0]["new_status"] == "delivered"
    assert history[1]["new_status"] == "in_transit"
