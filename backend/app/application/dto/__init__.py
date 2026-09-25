from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr, Field


class LoginCommand(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class ActivateCommand(BaseModel):
    token: str
    full_name: str = Field(min_length=2)
    password: str = Field(min_length=8)


class InviteCommand(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr
    role: str


class RegisterLotCommand(BaseModel):
    code: str
    mineral: str
    quantity: float = Field(gt=0)
    unit: str
    mining_operation_id: str | None = None
    observation: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    qr_payload: str | None = None
    client_operation_id: str | None = None


class CustodyCommand(BaseModel):
    lot_id: str
    origin: str
    destination: str
    quantity: float = Field(gt=0)
    notes: str | None = None
    client_operation_id: str | None = None


class TransportCommand(BaseModel):
    lot_id: str
    vehicle: str
    plate: str
    driver: str
    origin: str | None = None
    destination: str | None = None
    notes: str | None = None
    client_operation_id: str | None = None


class ReceptionCommand(BaseModel):
    lot_id: str
    declared_quantity: float = Field(gt=0)
    received_quantity: float = Field(gt=0)
    unit: str
    responsible: str
    notes: str | None = None
    client_operation_id: str | None = None


class WeighingCommand(BaseModel):
    lot_id: str
    weight: float = Field(gt=0)
    unit: str
    instrument: str
    responsible: str
    reception_id: str | None = None
    notes: str | None = None
    client_operation_id: str | None = None


class AlertReviewCommand(BaseModel):
    result: str = Field(min_length=2)
    observation: str | None = None


class ToleranceCommand(BaseModel):
    rule_key: str = "mass_balance_percent"
    name: str = "Tolerancia de balance de masas"
    value: float = Field(ge=0)
    unit: str = "percent"


class ProfileCommand(BaseModel):
    full_name: str | None = None


class SettingsCommand(BaseModel):
    general: dict[str, Any] | None = None
    security: dict[str, Any] | None = None
    notifications: dict[str, Any] | None = None
    integrations: dict[str, Any] | None = None


class PageQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    q: str | None = None
    sort: str = "created_at"
    order: str = "desc"
    status: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
