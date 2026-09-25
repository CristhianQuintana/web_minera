from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    PRODUCER = "producer"
    CARRIER = "carrier"
    RECEIVER = "receiver"
    TRANSPORTER = "transporter"
    PLANT_MANAGER = "plant_manager"
    CONTROL_CENTER = "control_center"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    AUDITOR = "auditor"

    @property
    def canonical(self) -> "UserRole":
        mapping = {
            UserRole.TRANSPORTER: UserRole.CARRIER,
            UserRole.PLANT_MANAGER: UserRole.RECEIVER,
            UserRole.CONTROL_CENTER: UserRole.SUPERVISOR,
        }
        return mapping.get(self, self)

    @property
    def label(self) -> str:
        return {
            UserRole.PRODUCER: "Productor",
            UserRole.CARRIER: "Transportista",
            UserRole.RECEIVER: "Receptor",
            UserRole.TRANSPORTER: "Transportista",
            UserRole.PLANT_MANAGER: "Receptor",
            UserRole.CONTROL_CENTER: "Supervisor",
            UserRole.SUPERVISOR: "Supervisor",
            UserRole.ADMIN: "Administrador",
            UserRole.AUDITOR: "Auditor",
        }[self]


class LotStatus(str, Enum):
    REGISTERED = "registered"
    IN_TRANSIT = "inTransit"
    TRANSFERRED = "transferred"
    RECEIVED = "received"
    CLOSED = "closed"


class AlertStatus(str, Enum):
    NEW = "new"
    IN_REVIEW = "in_review"
    ATTENDED = "attended"
    CLOSED = "closed"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MassBalanceStatus(str, Enum):
    WITHIN_TOLERANCE = "within_tolerance"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_DATA = "insufficient_data"


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class Permission(str, Enum):
    VIEW_LOTS = "view_lots"
    REGISTER_LOT = "register_lot"
    VIEW_CUSTODY = "view_custody"
    TRANSFER_CUSTODY = "transfer_custody"
    VIEW_TRANSPORT = "view_transport"
    REGISTER_TRANSPORT = "register_transport"
    VIEW_RECEPTIONS = "view_receptions"
    REGISTER_RECEPTION = "register_reception"
    REGISTER_WEIGHING = "register_weighing"
    VIEW_BALANCE = "view_balance"
    VIEW_ALERTS = "view_alerts"
    REVIEW_ALERT = "review_alert"
    VIEW_AUDIT = "view_audit"
    VIEW_ML = "view_ml"
    ESTIMATE_ML = "estimate_ml"
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    EXPORT = "export"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.ADMIN: set(Permission),
    UserRole.AUDITOR: {
        Permission.VIEW_LOTS,
        Permission.VIEW_CUSTODY,
        Permission.VIEW_TRANSPORT,
        Permission.VIEW_RECEPTIONS,
        Permission.VIEW_BALANCE,
        Permission.VIEW_ALERTS,
        Permission.REVIEW_ALERT,
        Permission.VIEW_AUDIT,
        Permission.VIEW_ML,
        Permission.ESTIMATE_ML,
        Permission.EXPORT,
    },
    UserRole.SUPERVISOR: {
        Permission.VIEW_LOTS,
        Permission.VIEW_CUSTODY,
        Permission.VIEW_TRANSPORT,
        Permission.VIEW_RECEPTIONS,
        Permission.VIEW_BALANCE,
        Permission.VIEW_ALERTS,
        Permission.VIEW_AUDIT,
        Permission.VIEW_ML,
        Permission.EXPORT,
    },
    UserRole.PRODUCER: {
        Permission.VIEW_LOTS,
        Permission.REGISTER_LOT,
        Permission.VIEW_CUSTODY,
        Permission.TRANSFER_CUSTODY,
        Permission.VIEW_TRANSPORT,
        Permission.VIEW_BALANCE,
        Permission.VIEW_ALERTS,
    },
    UserRole.CARRIER: {
        Permission.VIEW_LOTS,
        Permission.VIEW_CUSTODY,
        Permission.VIEW_TRANSPORT,
        Permission.REGISTER_TRANSPORT,
        Permission.VIEW_ALERTS,
    },
    UserRole.RECEIVER: {
        Permission.VIEW_LOTS,
        Permission.VIEW_TRANSPORT,
        Permission.VIEW_RECEPTIONS,
        Permission.REGISTER_RECEPTION,
        Permission.REGISTER_WEIGHING,
        Permission.VIEW_BALANCE,
        Permission.VIEW_ALERTS,
    },
}


def permissions_for(role: UserRole) -> set[Permission]:
    return ROLE_PERMISSIONS.get(role.canonical, set())


def allows(role: UserRole, permission: Permission) -> bool:
    return permission in permissions_for(role)


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        if not self.unit:
            raise ValueError("La unidad es obligatoria")


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float
    accuracy: float | None = None
