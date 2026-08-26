from fastapi.testclient import TestClient

from src.api.main import app

CUSTOMER_PAYLOAD = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 89.10,
    "TotalCharges": 1047.65,
}


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
    assert "access_token=" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]


def test_prediction_requires_authentication() -> None:
    with TestClient(app) as client:
        response = client.post("/predict", json=CUSTOMER_PAYLOAD)

    assert response.status_code == 401


def test_authenticated_prediction_uses_versioned_model() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin"},
        )
        response = client.post("/predict", json=CUSTOMER_PAYLOAD)

    assert login_response.status_code == 200
    assert response.status_code == 200
    payload = response.json()
    assert payload["prediction"] in {"Yes", "No"}
    assert 0.0 <= payload["probability"] <= 1.0


def test_model_info_matches_documented_threshold() -> None:
    with TestClient(app) as client:
        response = client.get("/model/info")

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_type"] == "LogisticRegression"
    assert payload["threshold"] == 0.5
