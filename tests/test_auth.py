from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """
    Test user registration endpoint.

    Args:
        client: Test HTTP client
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 201
    assert "access_token" in response.json()


def test_login_user(client: TestClient):
    """
    Test user login endpoint.

    Args:
        client: Test HTTP client
    """
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "TestPass123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "loginuser",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_health_check(client: TestClient):
    """
    Test health check endpoint.

    Args:
        client: Test HTTP client
    """
    response = client.get("/api/v1/health/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
