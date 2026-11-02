from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.composition.application_factory.factory import create_app
from app.domain.entities import Actor
from app.domain.value_objects import UserRole


ORG = "e857fa80-1678-4b27-b80f-c38f471a8931"


def _actor() -> Actor:
    return Actor(
        id="admin-1",
        email="admin@cooperativa.org",
        full_name="Admin",
        role=UserRole.ADMIN,
        organization_id=ORG,
        status="active",
        invitation_status="active",
    )


def _authed_client(gateway: MagicMock) -> TestClient:
    app = create_app()
    platform = app.state.container.platform
    platform._db = gateway
    gateway.get_user.return_value = {"id": "admin-1", "email": "admin@cooperativa.org"}
    gateway.get.side_effect = lambda table, record_id, **kwargs: (
        {
            "id": "admin-1",
            "email": "admin@cooperativa.org",
            "full_name": "Admin",
            "role": "admin",
            "organization_id": ORG,
            "status": "active",
            "invitation_status": "active",
        }
        if table == "profiles"
        else {
            "id": record_id,
            "organization_id": ORG,
            "quantity": 100,
            "mineral": "Oro",
            "unit": "kg",
            "code": "DEMO-LOTE-001",
            "mining_operation_id": None,
        }
        if table == "lots"
        else None
    )
    gateway.map_actor.return_value = _actor()
    return TestClient(app)


def test_list_ml_inferences_filters_by_organization() -> None:
    gateway = MagicMock()
    gateway.select.return_value = (
        [
            {
                "id": "inf-1",
                "organization_id": ORG,
                "lot_id": "lot-1",
                "model_version": "1.0.0",
                "expected_quantity": 97.8,
                "signal": "none",
            }
        ],
        1,
    )
    client = _authed_client(gateway)
    response = client.get(
        "/api/v1/ml/inferences",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["model_version"] == "1.0.0"
    assert gateway.select.call_args.args[0] == "ml_inferences"
    assert gateway.select.call_args.args[1]["organization_id"] == ORG


def test_estimate_persists_inference_with_features() -> None:
    gateway = MagicMock()
    gateway.select.side_effect = [
        ([], 0),  # receptions
        ([{"id": "model-1", "version": "1.0.0", "status": "active"}], 1),  # models
    ]
    gateway.insert.return_value = {
        "id": "inf-new",
        "organization_id": ORG,
        "lot_id": "lot-1",
        "model_version": "1.0.0-fallback",
        "expected_quantity": 97.8,
        "signal": "none",
        "features": {"source": "fallback"},
    }
    client = _authed_client(gateway)
    # Force fallback path: empty ML URL already default in tests without env
    response = client.post(
        "/api/v1/ml/estimate/lot-1",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real"},
    )
    assert response.status_code == 200, response.text
    assert gateway.insert.called
    inserted_table = gateway.insert.call_args.args[0]
    payload = gateway.insert.call_args.args[1]
    assert inserted_table == "ml_inferences"
    assert payload["organization_id"] == ORG
    assert payload["lot_id"] == "lot-1"
    assert "expected_quantity" in payload
    assert payload["features"].get("source") in {"fallback", "ml_service"}
