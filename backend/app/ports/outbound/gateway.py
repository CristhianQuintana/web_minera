"""Puertos outbound de persistencia, autenticación y configuración.

La capa de aplicación depende de estos contratos, nunca de adaptadores concretos
(Supabase, SMTP, HTTP, etc.).
"""

from __future__ import annotations

from typing import Any, Protocol

from app.domain.entities import Actor


class AppConfigPort(Protocol):
    """Configuración técnica inyectable. Sin acoplar a archivos .env ni frameworks."""

    @property
    def has_service_role(self) -> bool: ...

    @property
    def invite_expiry_hours(self) -> int: ...

    @property
    def invite_base_url(self) -> str: ...


class DataGatewayPort(Protocol):
    """Contrato unificado de persistencia + auth + storage firmado.

    Implementado por el adaptador outbound de Supabase (u otro proveedor).
    """

    def sign_in(self, email: str, password: str) -> dict[str, Any]: ...

    def get_user(self, access_token: str) -> dict[str, Any] | None: ...

    def refresh(self, refresh_token: str) -> dict[str, Any]: ...

    def recover(self, email: str) -> None: ...

    def create_user(self, email: str, password: str, full_name: str) -> dict[str, Any]: ...

    def invite_user(self, email: str, full_name: str) -> dict[str, Any] | None: ...

    def sign_out(self, access_token: str) -> None: ...

    def select(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        search: tuple[list[str], str] | None = None,
        order: str = "created_at.desc",
        limit: int = 20,
        offset: int = 0,
        select: str = "*",
        access_token: str | None = None,
        admin: bool = False,
    ) -> tuple[list[dict[str, Any]], int]: ...

    def get(
        self,
        table: str,
        record_id: str,
        select: str = "*",
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any] | None: ...

    def insert(
        self,
        table: str,
        payload: dict[str, Any],
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any]: ...

    def update(
        self,
        table: str,
        record_id: str,
        payload: dict[str, Any],
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any]: ...

    def upsert(
        self,
        table: str,
        payload: dict[str, Any],
        on_conflict: str,
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any]: ...

    def signed_url(self, bucket: str, path: str, expires: int = 300) -> str: ...

    def map_actor(self, row: dict[str, Any], email: str = "") -> Actor: ...
