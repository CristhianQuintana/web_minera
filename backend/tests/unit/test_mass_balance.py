from app.domain.rules import LotRegistrationRules, MassBalanceRules
from app.domain.services import MassBalanceCalculator
from app.domain.value_objects import MassBalanceStatus, UserRole, allows, Permission


def test_mass_balance_within_tolerance() -> None:
    status, difference, percent = MassBalanceRules.evaluate(100, 98, 3)
    assert status == MassBalanceStatus.WITHIN_TOLERANCE
    assert difference == -2
    assert percent == -2


def test_mass_balance_review_required() -> None:
    calculator = MassBalanceCalculator()
    status, _, percent = calculator.calculate(100, 80, 3)
    assert status == MassBalanceStatus.REVIEW_REQUIRED
    assert percent == -20


def test_mass_balance_insufficient() -> None:
    status, difference, percent = MassBalanceRules.evaluate(100, None, 3)
    assert status == MassBalanceStatus.INSUFFICIENT_DATA
    assert difference is None
    assert percent is None


def test_lot_registration_rejects_empty_code() -> None:
    try:
        LotRegistrationRules.validate(" ", "Oro", 10, "kg")
        raise AssertionError("expected error")
    except Exception as exc:
        assert "código" in str(exc).lower()


def test_auditor_cannot_register_lot() -> None:
    assert not allows(UserRole.AUDITOR, Permission.REGISTER_LOT)
    assert allows(UserRole.ADMIN, Permission.MANAGE_USERS)
