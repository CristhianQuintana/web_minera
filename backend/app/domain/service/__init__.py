"""Alias de presentación académica: `domain/service` ≡ services + rules.

Implementación canónica en `domain/services` y `domain/rules`.
"""

from app.domain.rules import (
    AuditRules,
    CustodyTransferRules,
    LotRegistrationRules,
    MassBalanceRules,
    ReceptionRules,
)
from app.domain.services import (
    CustodyIntegrityService,
    DeviationCalculator,
    MassBalanceCalculator,
)

__all__ = [
    "AuditRules",
    "CustodyTransferRules",
    "LotRegistrationRules",
    "MassBalanceRules",
    "ReceptionRules",
    "CustodyIntegrityService",
    "DeviationCalculator",
    "MassBalanceCalculator",
]
