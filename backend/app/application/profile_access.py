"""Validación de acceso a partir del estado de perfil de dominio."""

from __future__ import annotations

from typing import Any

from app.domain.exceptions import InactiveAccountError
from app.domain.services.profile_status import (
    invitation_blocks_login,
    normalize_profile_row,
    normalize_role,
    profile_is_active,
)

__all__ = [
    "assert_profile_can_login",
    "normalize_profile_row",
    "normalize_role",
    "profile_is_active",
]


def assert_profile_can_login(profile: dict[str, Any]) -> None:
    blocked = invitation_blocks_login(profile)
    if blocked or not profile_is_active(profile):
        raise InactiveAccountError("Tu cuenta está inactiva. Contacta al administrador.")
