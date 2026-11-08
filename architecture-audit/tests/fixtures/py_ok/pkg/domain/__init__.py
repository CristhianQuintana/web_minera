"""Dominio de fixture: solo stdlib."""

from typing import Any


def pure_rule(x: float) -> dict[str, Any]:
    return {"value": x * 0.98}
