"""Alias de presentación académica: `domain/model` ≡ entidades + value objects.

La implementación canónica vive en `domain/entities` y `domain/value_objects`
(conforme al Informe de arquitectura del proyecto). Este módulo reexporta
ese contenido real; no introduce clases ficticias.
"""

from app.domain.entities import (
    Actor,
    Alert,
    AuditRecord,
    CustodyTransfer,
    Evidence,
    Invitation,
    Lot,
    MassBalance,
    Reception,
    ToleranceRule,
    Transport,
    Weighing,
)
from app.domain.value_objects import (
    AlertSeverity,
    AlertStatus,
    Coordinates,
    InvitationStatus,
    LotStatus,
    MassBalanceStatus,
    Permission,
    Quantity,
    UserRole,
    allows,
    permissions_for,
)

__all__ = [
    "Actor",
    "Alert",
    "AuditRecord",
    "CustodyTransfer",
    "Evidence",
    "Invitation",
    "Lot",
    "MassBalance",
    "Reception",
    "ToleranceRule",
    "Transport",
    "Weighing",
    "AlertSeverity",
    "AlertStatus",
    "Coordinates",
    "InvitationStatus",
    "LotStatus",
    "MassBalanceStatus",
    "Permission",
    "Quantity",
    "UserRole",
    "allows",
    "permissions_for",
]
