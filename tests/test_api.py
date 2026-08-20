from fastapi.testclient import TestClient

from src.api.main import app


def test_health_endpoint_reports_api_state() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}
    assert isinstance(response.json()["model_loaded"], bool)


def test_login_returns_bearer_token() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["expires_in"] > 0
