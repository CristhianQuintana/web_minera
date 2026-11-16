from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.application.auth_context import AuthContext
from app.application.dto import ActivateCommand, InviteCommand, PageQuery
from app.application.services.platform import PlatformService
from app.domain.entities import Actor
from app.domain.exceptions import DomainError, ForbiddenError, InvitationInvalidError
from app.domain.value_objects import UserRole


ORG = "org-1"
OTHER_ORG = "org-2"


def _actor(user_id: str = "admin-1", org: str = ORG, role: UserRole = UserRole.ADMIN) -> Actor:
    return Actor(
        id=user_id,
        email=f"{user_id}@example.org",
        full_name="Admin User",
        role=role,
        organization_id=org,
        status="active",
        invitation_status="active",
    )


class FakeGateway:
    def __init__(self) -> None:
        self.rows: dict[str, list[dict]] = {"profiles": [], "invitations": []}
        self.audits: list[dict] = []
        self.next_user_id = "new-user"
        self.create_error: Exception | None = None

    def select(self, table, filters=None, search=None, order="created_at.desc", limit=20,
               offset=0, select="*", access_token=None, admin=False):
        rows = list(self.rows.get(table, []))
        for key, value in (filters or {}).items():
            if key.endswith("__ilike"):
                column = key.removesuffix("__ilike")
                rows = [row for row in rows if str(row.get(column, "")).lower() == str(value).lower()]
            else:
                rows = [row for row in rows if str(row.get(key)) == str(value)]
        if search and search[1]:
            needle = search[1].lower()
            rows = [row for row in rows if any(needle in str(row.get(col, "")).lower() for col in search[0])]
        return rows[offset : offset + limit], len(rows)

    def get(self, table, record_id, **kwargs):
        return next((row.copy() for row in self.rows.get(table, []) if row.get("id") == record_id), None)

    def insert(self, table, payload, **kwargs):
        row = {"id": f"{table}-{len(self.rows.setdefault(table, [])) + 1}", **payload}
        self.rows[table].append(row)
        if table == "audit_log":
            self.audits.append(row)
        return row.copy()

    def update(self, table, record_id, payload, **kwargs):
        for row in self.rows.get(table, []):
            if row.get("id") == record_id:
                row.update(payload)
                return row.copy()
        return {}

    def upsert(self, table, payload, on_conflict, **kwargs):
        existing = next((row for row in self.rows.setdefault(table, []) if row.get("id") == payload.get("id")), None)
        if existing:
            existing.update(payload)
            return existing.copy()
        return self.insert(table, payload)

    def auth_email_exists(self, email):
        return any(str(row.get("email", "")).lower() == email.lower() for row in self.rows["profiles"])

    def claim_invitation(self, token_hash):
        for row in self.rows["invitations"]:
            if row.get("token_hash") == token_hash and row.get("status") == "pending":
                expiry = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
                if expiry > datetime.now(timezone.utc):
                    row["status"] = "accepting"
                    return row.copy()
                row["status"] = "expired"
        return None

    def create_user(self, email, password, full_name):
        if self.create_error:
            raise self.create_error
        return {"id": self.next_user_id, "email": email}


class FakeEmail:
    def __init__(self, error=None):
        self.error = error
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to, subject, body):
        if self.error:
            raise self.error
        self.sent.append((to, subject, body))


@pytest.fixture
def setup():
    gateway = FakeGateway()
    email = FakeEmail()
    service = PlatformService(
        gateway,
        SimpleNamespace(has_service_role=True, invite_expiry_hours=72,
                        invite_base_url="https://example.org/activate"),
        email,
        MagicMock(),
    )
    return service, gateway, email, AuthContext(_actor(), "session")


def _command(email="new@example.org", role="producer"):
    return InviteCommand(full_name="New Employee", email=email, role=role)


def test_invite_sends_activation_link_and_lists_no_token_hash(setup):
    service, gateway, email, ctx = setup
    result = service.invite_user(ctx, _command())
    assert result["status"] == "pending"
    assert email.sent[0][0] == "new@example.org"
    assert "?token=" in email.sent[0][2]
    listed = service.list_users(ctx, PageQuery())
    assert listed["items"][0]["id"] == result["id"]
    assert listed["items"][0]["invitation_status"] == "pending"
    assert "token_hash" not in listed["items"][0]


def test_get_invitation_does_not_expose_token_hash(setup):
    service, gateway, _, ctx = setup
    gateway.rows["invitations"].append({
        "id": "invite-1",
        "email": "new@example.org",
        "full_name": "New Employee",
        "role": "producer",
        "organization_id": ORG,
        "status": "pending",
        "token_hash": "secret-hash",
    })

    invitation = service.get_user(ctx, "invite-1")

    assert invitation["invitation_status"] == "pending"
    assert "token_hash" not in invitation


def test_existing_account_email_is_rejected(setup):
    service, gateway, _, ctx = setup
    gateway.rows["profiles"].append({"id": "existing", "email": "new@example.org", "organization_id": OTHER_ORG})
    with pytest.raises(DomainError, match="Ya existe una cuenta"):
        service.invite_user(ctx, _command())


def test_duplicate_pending_invitation_is_rejected(setup):
    service, gateway, _, ctx = setup
    gateway.rows["invitations"].append({
        "id": "pending", "email": "new@example.org", "organization_id": ORG,
        "status": "pending", "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
    })
    with pytest.raises(DomainError, match="invitación pendiente"):
        service.invite_user(ctx, _command())


def test_smtp_failure_is_reported_and_invitation_revoked(setup):
    service, gateway, email, ctx = setup
    email.error = OSError("smtp offline")
    with pytest.raises(DomainError, match="No se pudo enviar"):
        service.invite_user(ctx, _command())
    assert gateway.rows["invitations"][0]["status"] == "revoked"


@pytest.mark.parametrize("role", ["superadmin", "root"])
def test_unrecognized_roles_are_rejected(setup, role):
    service, _, _, ctx = setup
    with pytest.raises(ForbiddenError):
        service.invite_user(ctx, _command(role=role))


def test_frontend_roles_match_backend_roles():
    source = Path(__file__).resolve().parents[3] / "frontend" / "src" / "app" / "(app)" / "users" / "page.tsx"
    frontend_roles = set(re.findall(r'\{ value: "([a-z_]+)", label:', source.read_text(encoding="utf-8")))
    assert frontend_roles == {role.value for role in UserRole}


def test_admin_cannot_change_own_role_or_deactivate_self(setup):
    service, gateway, _, ctx = setup
    gateway.rows["profiles"].append({"id": ctx.actor.id, "organization_id": ORG, "email": ctx.actor.email})
    with pytest.raises(ForbiddenError, match="propio rol"):
        service.update_user_role(ctx, ctx.actor.id, "producer")
    with pytest.raises(ForbiddenError, match="propia cuenta"):
        service.set_user_status(ctx, ctx.actor.id, False)


def test_admin_cannot_modify_user_in_other_organization(setup):
    service, gateway, _, ctx = setup
    gateway.rows["profiles"].append({"id": "foreign", "organization_id": OTHER_ORG, "email": "x@example.org"})
    with pytest.raises(ForbiddenError):
        service.update_user_role(ctx, "foreign", "producer")
    with pytest.raises(ForbiddenError):
        service.set_user_status(ctx, "foreign", False)
    assert gateway.rows["profiles"][0].get("status") is None


def test_activate_invitation_and_reject_reuse(setup):
    service, gateway, _, ctx = setup
    service.invite_user(ctx, _command())
    invitation = gateway.rows["invitations"][0]
    token = "unused"
    import hashlib
    invitation["token_hash"] = hashlib.sha256(token.encode()).hexdigest()
    service.activate_account(ActivateCommand(token=token, full_name="New Employee", password="StrongPass123"))
    assert gateway.rows["profiles"][0]["organization_id"] == ORG
    assert invitation["status"] == "accepted"
    with pytest.raises(InvitationInvalidError):
        service.activate_account(ActivateCommand(token=token, full_name="New Employee", password="StrongPass123"))


def test_auth_provider_failure_does_not_consume_invitation(setup):
    service, gateway, _, ctx = setup
    service.invite_user(ctx, _command())
    gateway.create_error = RuntimeError("provider down")
    invitation = gateway.rows["invitations"][0]
    import hashlib
    token = "activation-token"
    invitation["token_hash"] = hashlib.sha256(token.encode()).hexdigest()
    with pytest.raises(DomainError, match="No pudimos activar"):
        service.activate_account(ActivateCommand(token=token, full_name="New Employee", password="StrongPass123"))
    assert invitation["status"] == "pending"


def test_activate_and_deactivate_other_account(setup):
    service, gateway, _, ctx = setup
    gateway.rows["profiles"].append({"id": "employee", "organization_id": ORG, "status": "inactive"})
    service.set_user_status(ctx, "employee", True)
    assert gateway.rows["profiles"][0]["status"] == "active"
    service.set_user_status(ctx, "employee", False)
    assert gateway.rows["profiles"][0]["status"] == "inactive"


def test_admin_can_assign_any_existing_role_to_another_org_member(setup):
    service, gateway, _, ctx = setup
    gateway.rows["profiles"].append({"id": "employee", "organization_id": ORG})
    result = service.update_user_role(ctx, "employee", "transporter")
    assert result["role"] == "transporter"
    assert gateway.audits[-1]["action"] == "update_user_role"


def test_expired_invitation_token_is_rejected(setup):
    import hashlib

    service, gateway, _, ctx = setup
    service.invite_user(ctx, _command())
    token = "expired-token"
    invitation = gateway.rows["invitations"][0]
    invitation["token_hash"] = hashlib.sha256(token.encode()).hexdigest()
    invitation["expires_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    with pytest.raises(InvitationInvalidError):
        service.validate_invitation(token)
    assert invitation["status"] == "expired"


def test_resend_pending_invitation_reissues_link(setup):
    service, gateway, email, ctx = setup
    result = service.invite_user(ctx, _command())
    first_token_hash = gateway.rows["invitations"][0]["token_hash"]
    service.resend_invite(ctx, result["id"])
    assert len(email.sent) == 2
    assert gateway.rows["invitations"][0]["status"] == "revoked"
    assert gateway.rows["invitations"][1]["status"] == "pending"
    assert gateway.rows["invitations"][1]["token_hash"] != first_token_hash


def test_failed_resend_preserves_previous_pending_invitation(setup):
    service, gateway, email, ctx = setup
    result = service.invite_user(ctx, _command())
    email.error = OSError("smtp offline")
    with pytest.raises(DomainError):
        service.resend_invite(ctx, result["id"])
    assert gateway.rows["invitations"][0]["status"] == "pending"
    assert gateway.rows["invitations"][1]["status"] == "revoked"
