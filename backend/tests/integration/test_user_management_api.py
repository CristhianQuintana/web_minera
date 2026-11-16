import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.composition.application_factory.factory import create_app
from app.domain.entities import Actor
from app.domain.value_objects import UserRole


def _client() -> tuple[TestClient, MagicMock]:
    app = create_app()
    gateway = MagicMock()
    gateway.get_user.return_value = {"id": "admin-1", "email": "admin@example.org"}
    gateway.get.return_value = {
        "id": "admin-1",
        "email": "admin@example.org",
        "full_name": "Admin User",
        "role": "admin",
        "organization_id": "org-1",
        "status": "active",
        "invitation_status": "active",
    }
    gateway.map_actor.return_value = Actor(
        id="admin-1", email="admin@example.org", full_name="Admin User", role=UserRole.ADMIN,
        organization_id="org-1", status="active", invitation_status="active",
    )
    gateway.select.return_value = ([], 0)
    gateway.auth_email_exists.return_value = False
    app.state.container.platform._db = gateway
    app.state.container.platform._email = MagicMock()
    return TestClient(app), gateway


def test_invite_rejects_invalid_email_before_persistence() -> None:
    client, gateway = _client()
    response = client.post(
        "/api/v1/users/invite",
        headers={"Authorization": "Bearer real-session-token"},
        json={"full_name": "Employee", "email": "not-an-email", "role": "producer"},
    )
    assert response.status_code == 422
    gateway.insert.assert_not_called()


def test_invite_rejects_role_not_in_domain_enum() -> None:
    client, gateway = _client()
    response = client.post(
        "/api/v1/users/invite",
        headers={"Authorization": "Bearer real-session-token"},
        json={"full_name": "Employee", "email": "employee@example.org", "role": "superadmin"},
    )
    assert response.status_code == 403
    gateway.insert.assert_not_called()


def test_invite_returns_failure_when_smtp_raises() -> None:
    client, gateway = _client()
    app_email = client.app.state.container.platform._email
    app_email.send.side_effect = OSError("private smtp detail")
    gateway.insert.side_effect = lambda table, payload, **kwargs: {"id": "invite-1", **payload}

    response = client.post(
        "/api/v1/users/invite",
        headers={"Authorization": "Bearer real-session-token"},
        json={"full_name": "Employee", "email": "employee@example.org", "role": "producer"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invitation_delivery_failed"
    assert "private smtp detail" not in response.text
    gateway.update.assert_called_once()


def test_concurrent_activation_claims_single_use_invitation() -> None:
    client, gateway = _client()
    token = "single-use-token"
    invitation = {
        "id": "invite-1",
        "email": "employee@example.org",
        "full_name": "Employee",
        "role": "producer",
        "organization_id": "org-1",
        "status": "pending",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
    }
    invitation["token_hash"] = hashlib.sha256(token.encode()).hexdigest()
    lock = threading.Lock()
    gateway.claim_invitation.side_effect = lambda token_hash: _claim_once(lock, invitation, token_hash)
    gateway.create_user.return_value = {"id": "employee-1", "email": invitation["email"]}
    gateway.upsert.return_value = {"id": "employee-1", "organization_id": "org-1"}
    gateway.update.return_value = {"id": "invite-1", "status": "accepted"}
    payload = {"token": token, "full_name": "Employee", "password": "StrongPass123"}

    def activate():
        return client.post("/api/v1/auth/activate", json=payload)

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: activate(), range(2)))
    assert sorted(response.status_code for response in responses) == [200, 400]
    assert gateway.claim_invitation.call_count == 2
    gateway.claim_invitation.assert_called_with(invitation["token_hash"])
    gateway.create_user.assert_called_once()
    gateway.upsert.assert_called_once()


def _claim_once(lock: threading.Lock, invitation: dict, token_hash: str):
    with lock:
        if token_hash != invitation["token_hash"] or invitation["status"] != "pending":
            return None
        invitation["status"] = "accepting"
        return invitation.copy()
