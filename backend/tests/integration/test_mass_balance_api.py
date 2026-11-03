from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.composition.application_factory.factory import create_app
from app.domain.entities import Actor
from app.domain.value_objects import UserRole

ORG = "e857fa80-1678-4b27-b80f-c38f471a8931"


def _client(gateway: MagicMock) -> TestClient:
    app = create_app()
    app.state.container.platform._db = gateway
    gateway.get_user.return_value = {"id": "admin-1", "email": "admin@coop.org"}
    gateway.map_actor.return_value = Actor(
        id="admin-1",
        email="admin@coop.org",
        full_name="Admin",
        role=UserRole.ADMIN,
        organization_id=ORG,
        status="active",
        invitation_status="active",
    )
    gateway.get.return_value = {
        "id": "admin-1",
        "email": "admin@coop.org",
        "full_name": "Admin",
        "role": "admin",
        "organization_id": ORG,
        "status": "active",
        "invitation_status": "active",
    }
    return TestClient(app)


def test_mass_balance_lists_computed_rows_without_mass_balances_table() -> None:
    gateway = MagicMock()
    def select_side_effect(table, filters=None, **kwargs):
        if table == "lots":
            return (
                [
                    {
                        "id": "lot-1",
                        "organization_id": ORG,
                        "code": "LOT-2026-001",
                        "mineral": "Oro",
                        "quantity": 100,
                    }
                ],
                1,
            )
        if table == "receptions":
            return ([{"lot_id": "lot-1", "received_quantity": 98}], 1)
        if table == "tolerance_rules":
            return ([], 0)
        return ([], 0)

    gateway.select.side_effect = select_side_effect

    client = _client(gateway)
    # Override get for profile only; lots detail not needed for list
    response = client.get(
        "/api/v1/mass-balance",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["lot_code"] == "LOT-2026-001"
    assert body["items"][0]["status"] in {"within_tolerance", "review_required", "insufficient_data"}
    # Must not touch mass_balances table
    assert all(call.args[0] != "mass_balances" for call in gateway.select.call_args_list)
