from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.value_objects import AlertSeverity, AlertStatus, LotStatus, MassBalanceStatus, UserRole


@dataclass
class Actor:
    id: str
    email: str
    full_name: str
    role: UserRole
    organization_id: str
    status: str
    invitation_status: str
    last_activity_at: datetime | None = None


@dataclass
class Lot:
    id: str
    code: str
    mineral: str
    quantity: float
    unit: str
    status: LotStatus
    organization_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    mining_operation_id: str | None = None
    producer_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    qr_payload: str | None = None
    observation: str | None = None
    client_operation_id: str | None = None


@dataclass
class CustodyTransfer:
    id: str
    lot_id: str
    origin: str
    destination: str
    quantity: float
    occurred_at: datetime
    notes: str | None = None
    status: str = "completed"
    responsible: str | None = None
    lot_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class Transport:
    id: str
    lot_id: str
    vehicle: str
    plate: str
    driver: str
    status: str
    started_at: datetime
    ended_at: datetime | None = None
    code: str | None = None
    origin: str | None = None
    destination: str | None = None
    assigned_to: str | None = None
    lot_code: str | None = None
    notes: str | None = None


@dataclass
class Reception:
    id: str
    lot_id: str
    declared_quantity: float
    received_quantity: float
    unit: str
    occurred_at: datetime
    responsible: str
    status: str
    lot_code: str | None = None
    notes: str | None = None
    created_by: str | None = None


@dataclass
class Weighing:
    id: str
    lot_id: str
    weight: float
    unit: str
    occurred_at: datetime
    instrument: str
    responsible: str
    lot_code: str | None = None
    reception_id: str | None = None
    notes: str | None = None


@dataclass
class Evidence:
    id: str
    lot_id: str
    file_name: str
    mime_type: str
    size_bytes: int
    storage_path: str | None
    created_at: datetime
    created_by: str | None = None


@dataclass
class Alert:
    id: str
    organization_id: str
    severity: AlertSeverity
    alert_type: str
    title: str
    status: AlertStatus
    created_at: datetime
    lot_id: str | None = None
    lot_code: str | None = None
    summary: str | None = None
    reason: str | None = None
    assigned_to: str | None = None
    rule_applied: str | None = None
    ml_inference_id: str | None = None


@dataclass
class MassBalance:
    id: str
    lot_id: str
    organization_id: str
    origin_quantity: float
    status: MassBalanceStatus
    calculated_at: datetime
    received_quantity: float | None = None
    difference: float | None = None
    difference_percent: float | None = None
    tolerance_value: float | None = None
    tolerance_unit: str | None = None
    tolerance_version: int | None = None
    lot_code: str | None = None


@dataclass
class AuditRecord:
    id: str
    action: str
    entity: str
    created_at: datetime
    user_id: str | None = None
    actor_name: str | None = None
    entity_id: str | None = None
    lot_id: str | None = None
    result: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToleranceRule:
    id: str
    organization_id: str
    rule_key: str
    name: str
    value: float
    unit: str
    version: int
    is_active: bool
    effective_from: datetime
    created_by: str | None = None
    created_at: datetime | None = None


@dataclass
class Invitation:
    id: str
    email: str
    full_name: str
    role: str
    organization_id: str
    expires_at: datetime
    status: str
    created_at: datetime
    invited_by: str | None = None
