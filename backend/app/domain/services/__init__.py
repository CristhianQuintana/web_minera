from app.domain.rules import MassBalanceRules
from app.domain.value_objects import MassBalanceStatus


class MassBalanceCalculator:
    def calculate(
        self,
        origin_quantity: float,
        received_quantity: float | None,
        tolerance_percent: float,
    ) -> tuple[MassBalanceStatus, float | None, float | None]:
        return MassBalanceRules.evaluate(origin_quantity, received_quantity, tolerance_percent)


class DeviationCalculator:
    def percent(self, expected: float, observed: float | None) -> float | None:
        if observed is None or expected == 0:
            return None
        return ((observed - expected) / expected) * 100


class CustodyIntegrityService:
    def is_complete(self, has_origin: bool, has_destination: bool, has_quantity: bool) -> bool:
        return has_origin and has_destination and has_quantity
