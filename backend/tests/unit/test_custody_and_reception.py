import pytest

from app.domain.exceptions import InvalidCustodyTransfer, InvalidQuantity
from app.domain.rules import AuditRules, CustodyTransferRules, ReceptionRules
from app.domain.services import CustodyIntegrityService, DeviationCalculator
from app.domain.value_objects import LotStatus


def test_custody_rejects_same_origin_and_destination() -> None:
    with pytest.raises(InvalidCustodyTransfer):
        CustodyTransferRules.validate("Mina El Alto", "mina el alto", 10, LotStatus.REGISTERED.value)


def test_custody_rejects_closed_lot() -> None:
    with pytest.raises(InvalidCustodyTransfer):
        CustodyTransferRules.validate("Origen", "Destino", 10, LotStatus.CLOSED.value)


def test_custody_rejects_invalid_quantity() -> None:
    with pytest.raises(InvalidQuantity):
        CustodyTransferRules.validate("Origen", "Destino", 0, LotStatus.REGISTERED.value)


def test_reception_requires_positive_quantities() -> None:
    with pytest.raises(InvalidQuantity):
        ReceptionRules.validate(0, 10)


def test_audit_requires_action_and_entity() -> None:
    with pytest.raises(ValueError):
        AuditRules.required_fields("", "lot")


def test_deviation_and_custody_integrity_services() -> None:
    assert DeviationCalculator().percent(100, 90) == -10
    assert DeviationCalculator().percent(0, 10) is None
    assert CustodyIntegrityService().is_complete(True, True, True) is True
    assert CustodyIntegrityService().is_complete(True, False, True) is False
