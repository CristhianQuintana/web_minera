"""Reglas puras de estado de perfil y roles (sin I/O)."""

from __future__ import annotations

from typing import Any

from app.domain.value_objects import UserRole

_ROLE_ALIASES = {
    "administrator": UserRole.ADMIN.value,
    "admin": UserRole.ADMIN.value,
    "administrador": UserRole.ADMIN.value,
    "transportista": UserRole.CARRIER.value,
    "transporter": UserRole.TRANSPORTER.value,
    "productor": UserRole.PRODUCER.value,
    "receptor": UserRole.RECEIVER.value,
    "plant_manager": UserRole.PLANT_MANAGER.value,
    "control_center": UserRole.CONTROL_CENTER.value,
}


def normalize_role(raw: Any) -> str:
    value = str(raw or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not value:
        return UserRole.AUDITOR.value
    aliased = _ROLE_ALIASES.get(value, value)
    try:
        return UserRole(aliased).value
    except ValueError:
        return UserRole.AUDITOR.value


def _truthy(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "active", "activo"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "inactivo"}:
        return False
    return None


def invitation_blocks_login(profile: dict[str, Any]) -> str | None:
    invitation = str(profile.get("invitation_status") or "active").strip().lower()
    if invitation in {"inactive", "inactivo"}:
        return "inactive"
    if invitation in {"expired", "expirado"}:
        return "expired"
    return None


def profile_is_active(profile: dict[str, Any]) -> bool:
    """Determina si el perfil puede autenticarse.

    Compatibilidad: algunos perfiles/exportes usan ``is_active`` (bool) además o
    en lugar de ``status`` textual. Si ``is_active`` está presente, tiene
    prioridad sobre ``status`` para alinear con la señal que el operador ve en
    el panel de Auth / Table Editor.
    """
    if invitation_blocks_login(profile):
        return False

    is_active = _truthy(profile.get("is_active"))
    if is_active is not None:
        return is_active

    status_raw = profile.get("status")
    if status_raw is not None and str(status_raw).strip() != "":
        status_truth = _truthy(status_raw)
        if status_truth is not None:
            return status_truth
        return str(status_raw).strip().lower() == "active"

    return False


def normalize_profile_row(profile: dict[str, Any], email: str = "") -> dict[str, Any]:
    row = dict(profile)
    row["role"] = normalize_role(row.get("role"))
    row["status"] = "active" if profile_is_active(row) else "inactive"
    invitation = str(row.get("invitation_status") or "active").strip().lower()
    if invitation in {"pending", "active", "inactive", "expired"}:
        row["invitation_status"] = invitation
    else:
        row["invitation_status"] = "active"
    if email and not row.get("email"):
        row["email"] = email
    return row
