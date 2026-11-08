"""Dominio contaminado a propósito (fixture de violación)."""

import fastapi  # noqa: F401 — violación intencional para validar la regla


def contaminated() -> str:
    return fastapi.__name__
