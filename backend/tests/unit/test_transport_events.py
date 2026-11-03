from types import SimpleNamespace
from unittest.mock import MagicMock

from app.application.auth_context import AuthContext
from app.application.dto import TransportEventCommand
from app.application.services.platform import PlatformService
from app.domain.entities import Actor
from app.domain.value_objects import UserRole

ORG = "org-a"


def _ctx() -> AuthContext:
    actor = Actor(
        id="user-1",
        email="a@example.com",
        full_name="User A",
        role=UserRole.ADMIN,
        organization_id=ORG,
        status="active",
        invitation_status="active",
    )
    return AuthContext(actor=actor, access_token="token")


def test_register_transport_event_persists_and_audits():
    gateway = MagicMock()
    gateway.get.side_effect = [
        {"id": "tr-1", "lot_id": "lot-1"},
        {"id": "lot-1", "organization_id": ORG, "status": "inTransit"},
    ]
    gateway.insert.side_effect = [
        {"id": "ev-1", "transport_id": "tr-1", "description": "Salida"},
        {"id": "le-1"},
        {"id": "audit-1"},
    ]
    platform = PlatformService(
        gateway,
        settings=SimpleNamespace(has_service_role=False),
        email=MagicMock(),
        ml=MagicMock(),
    )
    result = platform.register_transport_event(
        _ctx(),
        "tr-1",
        TransportEventCommand(description="Salida mina", event_type="departure"),
    )
    assert result["id"] == "ev-1"
    assert gateway.insert.call_count >= 2
