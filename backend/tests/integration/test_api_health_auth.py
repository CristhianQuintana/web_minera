from fastapi.testclient import TestClient

from app.composition.application_factory.factory import create_app

client = TestClient(create_app())


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_login_returns_admin_session() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cristhian@gmail.com", "password": "Cristhian123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "demo-local-cristhian"
    assert body["user"]["role"] == "admin"
    assert body["user"]["email"] == "cristhian@gmail.com"
    assert "manage_users" in body["user"]["permissions"]


def test_demo_login_rejects_wrong_password() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cristhian@gmail.com", "password": "clave-incorrecta"},
    )
    assert response.status_code in {401, 500}


def test_me_with_demo_token() -> None:
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer demo-local-cristhian"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Cristhian"


def test_me_without_token_is_unauthorized() -> None:
    fresh = TestClient(create_app())
    response = fresh.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_login_has_no_public_register_route() -> None:
    response = client.post("/api/v1/auth/register", json={"email": "nuevo@correo.com"})
    assert response.status_code == 404
