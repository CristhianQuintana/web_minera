from app.domain.exceptions import InactiveAccountError
from app.domain.services.profile_status import normalize_profile_row, normalize_role, profile_is_active
from app.application.profile_access import assert_profile_can_login


def test_normalize_role_accepts_administrator_alias() -> None:
    assert normalize_role("administrator") == "admin"
    assert normalize_role("Administrador") == "admin"
    assert normalize_role("ADMIN") == "admin"


def test_profile_active_with_is_active_when_status_missing() -> None:
    assert profile_is_active({"is_active": True}) is True
    assert profile_is_active({"is_active": False}) is False


def test_profile_active_status_case_insensitive() -> None:
    assert profile_is_active({"status": "Active"}) is True
    assert profile_is_active({"status": "ACTIVE"}) is True
    assert profile_is_active({"status": "inactive"}) is False


def test_invitation_inactive_blocks_even_if_status_active() -> None:
    assert profile_is_active({"status": "active", "invitation_status": "inactive"}) is False
    assert profile_is_active({"status": "active", "invitation_status": "expired"}) is False


def test_assert_profile_can_login_matches_production_symptom() -> None:
    # Caso reportado: Auth OK + is_active/administrator sin status textual "active".
    profile = {
        "id": "u1",
        "role": "administrator",
        "is_active": True,
        "invitation_status": "active",
        "organization_id": "e857fa80-1678-4b27-b80f-c38f471a8931",
    }
    assert_profile_can_login(profile)
    normalized = normalize_profile_row(profile, "cristhian@gmail.com")
    assert normalized["role"] == "admin"
    assert normalized["status"] == "active"


def test_is_active_true_overrides_textual_inactive_status() -> None:
    # Incidencia Render: operador ve is_active=true aunque status textual difiera.
    assert profile_is_active({"status": "inactive", "is_active": True}) is True
    assert_profile_can_login({"status": "inactive", "is_active": True, "invitation_status": "active"})


def test_is_active_false_blocks_even_if_status_active() -> None:
    assert profile_is_active({"status": "active", "is_active": False}) is False
    try:
        assert_profile_can_login({"status": "active", "is_active": False})
        raised = False
    except InactiveAccountError:
        raised = True
    assert raised


def test_status_inactive_blocks_when_is_active_absent() -> None:
    assert profile_is_active({"status": "inactive"}) is False
