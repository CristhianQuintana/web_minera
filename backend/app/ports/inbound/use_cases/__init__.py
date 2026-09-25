"""Puertos inbound: contratos que los adaptadores HTTP invocan."""

from typing import Any, Protocol


class UseCase(Protocol):
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        ...
