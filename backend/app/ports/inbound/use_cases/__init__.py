"""Puertos inbound: contratos que los adaptadores HTTP invocan.

No importan adaptadores ni frameworks. Los tipos de comando se tipan como Any
en el contrato para evitar acoplar puertos a DTOs de framework; los casos de uso
concretos sí tipan con DTOs de aplicación.
"""

from __future__ import annotations

from typing import Any, Protocol


class AuthenticateUseCasePort(Protocol):
    def execute(self, command: Any) -> dict[str, Any]: ...


class RegisterLotUseCasePort(Protocol):
    def execute(self, ctx: Any, command: Any) -> dict[str, Any]: ...


class ReviewAlertUseCasePort(Protocol):
    def execute(self, ctx: Any, alert_id: str, command: Any) -> dict[str, Any]: ...


class InviteUserUseCasePort(Protocol):
    def execute(self, ctx: Any, command: Any) -> dict[str, Any]: ...


class ActivateAccountUseCasePort(Protocol):
    def execute(self, command: Any) -> dict[str, Any]: ...


class ResolveSessionUseCasePort(Protocol):
    def execute(self, access_token: str) -> Any: ...
