"""Puertos inbound del servicio ML."""

from __future__ import annotations

from typing import Any, Protocol


class EstimateExpectedQuantityPort(Protocol):
    def execute(self, features: dict[str, Any]) -> dict[str, Any]: ...
