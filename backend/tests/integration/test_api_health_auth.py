from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.composition.application_factory.factory import create_app
from app.domain.entities import Actor
from app.domain.exceptions import UnauthorizedError
from app.domain.value_objects import UserRole


def _actor(**overrides) -> Actor:
    data = {
        "id": "user-real-1",
        "email": "admin@cooperativa.org",
        "full_name": "Admin Real",
        "role": UserRole.ADMIN,
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
        "status": "active",
        "invitation_status": "active",
    }
    data.update(overrides)
    return Actor(**data)


def _client_with_gateway(gateway: MagicMock) -> TestClient:
    app = create_app()
    app.state.container.platform._db = gateway
    return TestClient(app)


def test_health_returns_ok() -> None:
    response = TestClient(create_app()).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_with_supabase_session_returns_user() -> None:
    gateway = MagicMock()
    gateway.sign_in.return_value = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real",
        "refresh_token": "refresh-real-token",
        "expires_in": 3600,
        "user": {"id": "user-real-1", "email": "admin@cooperativa.org"},
    }
    gateway.get.return_value = {
        "id": "user-real-1",
        "email": "admin@cooperativa.org",
        "full_name": "Admin Real",
        "role": "admin",
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
        "status": "active",
        "invitation_status": "active",
    }
    gateway.map_actor.return_value = _actor()

    client = _client_with_gateway(gateway)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@cooperativa.org", "password": "Secreta123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"].startswith("eyJ")
    assert "demo-" not in body["access_token"]
    assert body["user"]["organization_id"] == "e857fa80-1678-4b27-b80f-c38f471a8931"
    assert body["user"]["role"] == "admin"
    assert "manage_users" in body["user"]["permissions"]
    gateway.sign_in.assert_called_once()


def test_login_accepts_is_active_and_administrator_role() -> None:
    """Reproduce la incidencia de producción: Auth OK + is_active/administrator."""
    from app.adapters.outbound.supabase.client import SupabaseGateway

    gateway = MagicMock()
    gateway.sign_in.return_value = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real",
        "refresh_token": "refresh-real-token",
        "expires_in": 3600,
        "user": {
            "id": "user-cristhian",
            "email": "cristhian@gmail.com",
            "email_confirmed_at": "2026-11-01T00:00:00Z",
            "banned_until": None,
        },
    }
    gateway.get.return_value = {
        "id": "user-cristhian",
        "email": "cristhian@gmail.com",
        "full_name": "Cristhian",
        "role": "administrator",
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
        "is_active": True,
        "invitation_status": "active",
    }
    binder = SupabaseGateway.__new__(SupabaseGateway)
    gateway.map_actor.side_effect = lambda row, email="": SupabaseGateway.map_actor(binder, row, email)

    client = _client_with_gateway(gateway)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cristhian@gmail.com", "password": "Cristhian123"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user"]["role"] == "admin"
    assert body["user"]["status"] == "active"
    assert "demo-" not in body["access_token"]


def test_login_reconciles_inactive_status_for_confirmed_auth_user() -> None:
    from app.adapters.outbound.supabase.client import SupabaseGateway

    gateway = MagicMock()
    gateway.sign_in.return_value = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real",
        "refresh_token": "refresh-real-token",
        "expires_in": 3600,
        "user": {
            "id": "user-cristhian",
            "email": "cristhian@gmail.com",
            "email_confirmed_at": "2026-11-01T00:00:00Z",
            "banned_until": None,
        },
    }
    gateway.get.return_value = {
        "id": "user-cristhian",
        "email": "cristhian@gmail.com",
        "full_name": "Cristhian",
        "role": "admin",
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
        "status": "inactive",
        "invitation_status": "active",
    }
    binder = SupabaseGateway.__new__(SupabaseGateway)
    gateway.map_actor.side_effect = lambda row, email="": SupabaseGateway.map_actor(binder, row, email)

    client = _client_with_gateway(gateway)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cristhian@gmail.com", "password": "Cristhian123"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["user"]["status"] == "active"


def test_login_keeps_deactivated_invitation_blocked() -> None:
    gateway = MagicMock()
    gateway.sign_in.return_value = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real",
        "refresh_token": "refresh-real-token",
        "expires_in": 3600,
        "user": {
            "id": "user-x",
            "email": "x@y.com",
            "email_confirmed_at": "2026-11-01T00:00:00Z",
        },
    }
    gateway.get.return_value = {
        "id": "user-x",
        "role": "admin",
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
        "status": "inactive",
        "invitation_status": "inactive",
    }
    client = _client_with_gateway(gateway)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@y.com", "password": "Secreta123!"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "inactive_account"


def test_login_rejects_wrong_credentials() -> None:
    gateway = MagicMock()
    gateway.sign_in.side_effect = UnauthorizedError("El correo o la contraseña no son correctos.")
    client = _client_with_gateway(gateway)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@cooperativa.org", "password": "clave-incorrecta"},
    )
    assert response.status_code == 401


def test_demo_token_is_rejected() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer demo-local-cristhian"},
    )
    assert response.status_code == 401


def test_me_without_token_is_unauthorized() -> None:
    response = TestClient(create_app()).get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_valid_token_returns_profile() -> None:
    gateway = MagicMock()
    gateway.get_user.return_value = {"id": "user-real-1", "email": "admin@cooperativa.org"}
    gateway.get.return_value = {
        "id": "user-real-1",
        "email": "admin@cooperativa.org",
        "full_name": "Admin Real",
        "role": "admin",
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
        "status": "active",
        "invitation_status": "active",
    }
    gateway.map_actor.return_value = _actor()

    client = _client_with_gateway(gateway)
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@cooperativa.org"
    assert response.json()["organization_id"] != "demo-org"


def test_login_rejects_demo_organization() -> None:
    gateway = MagicMock()
    gateway.sign_in.return_value = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real",
        "refresh_token": "refresh-real-token",
        "expires_in": 3600,
        "user": {"id": "user-demo-org", "email": "x@y.com"},
    }
    gateway.get.return_value = {
        "id": "user-demo-org",
        "status": "active",
        "invitation_status": "active",
        "organization_id": "demo-org",
    }
    gateway.map_actor.return_value = _actor(
        id="user-demo-org",
        email="x@y.com",
        organization_id="demo-org",
    )

    client = _client_with_gateway(gateway)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@y.com", "password": "Secreta123!"},
    )
    assert response.status_code == 401


def test_refresh_rejects_demo_token() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "demo-local-cristhian"},
    )
    assert response.status_code == 401


def test_forbidden_when_missing_permission() -> None:
    gateway = MagicMock()
    gateway.get_user.return_value = {"id": "carrier-1", "email": "carrier@coop.org"}
    gateway.get.return_value = {
        "id": "carrier-1",
        "email": "carrier@coop.org",
        "full_name": "Transportista",
        "role": "carrier",
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
        "status": "active",
        "invitation_status": "active",
    }
    gateway.map_actor.return_value = _actor(
        id="carrier-1",
        email="carrier@coop.org",
        full_name="Transportista",
        role=UserRole.CARRIER,
    )
    gateway.select.return_value = ([], 0)

    client = _client_with_gateway(gateway)
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real"},
    )
    assert response.status_code == 403


def test_login_has_no_public_register_route() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/auth/register",
        json={"email": "nuevo@correo.com"},
    )
    assert response.status_code == 404
