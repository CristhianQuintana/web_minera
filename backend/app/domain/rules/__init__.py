from app.domain.exceptions import InvalidCustodyTransfer, InvalidLotState, InvalidQuantity
from app.domain.value_objects import LotStatus, MassBalanceStatus


class LotRegistrationRules:
    @staticmethod
    def validate(code: str, mineral: str, quantity: float, unit: str) -> None:
        if not code or len(code.strip()) < 3:
            raise InvalidLotState("El código del lote es obligatorio.")
        if not mineral:
            raise InvalidLotState("El mineral es obligatorio.")
        if quantity <= 0:
            raise InvalidQuantity("La cantidad debe ser mayor que cero.")
        if not unit:
            raise InvalidQuantity("La unidad de medida es obligatoria.")


class CustodyTransferRules:
    @staticmethod
    def validate(origin: str, destination: str, quantity: float, lot_status: str) -> None:
        if not origin or not destination:
            raise InvalidCustodyTransfer("Origen y destino son obligatorios.")
        if origin.strip().lower() == destination.strip().lower():
            raise InvalidCustodyTransfer("El origen y el destino no pueden ser iguales.")
        if quantity <= 0:
            raise InvalidQuantity("La cantidad transferida debe ser mayor que cero.")
        if lot_status == LotStatus.CLOSED.value:
            raise InvalidCustodyTransfer("No se puede transferir un lote cerrado.")


class ReceptionRules:
    @staticmethod
    def validate(declared: float, received: float) -> None:
        if declared <= 0 or received <= 0:
            raise InvalidQuantity("Las cantidades de recepción deben ser mayores que cero.")


class MassBalanceRules:
    @staticmethod
    def evaluate(
        origin_quantity: float,
        received_quantity: float | None,
        tolerance_percent: float,
    ) -> tuple[MassBalanceStatus, float | None, float | None]:
        if received_quantity is None:
            return MassBalanceStatus.INSUFFICIENT_DATA, None, None
        difference = received_quantity - origin_quantity
        percent = (difference / origin_quantity) * 100 if origin_quantity else 0
        if abs(percent) <= tolerance_percent:
            return MassBalanceStatus.WITHIN_TOLERANCE, difference, percent
        return MassBalanceStatus.REVIEW_REQUIRED, difference, percent


class AuditRules:
    @staticmethod
    def required_fields(action: str, entity: str) -> None:
        if not action or not entity:
            raise ValueError("La auditoría requiere acción y entidad.")
