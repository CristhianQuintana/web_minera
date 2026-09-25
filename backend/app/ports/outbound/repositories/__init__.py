from __future__ import annotations

from typing import Any, Protocol

from app.domain.entities import Actor


class QueryPort(Protocol):
    def select(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        search: tuple[list[str], str] | None = None,
        order: str = "created_at.desc",
        limit: int = 20,
        offset: int = 0,
        select: str = "*",
    ) -> tuple[list[dict[str, Any]], int]:
        ...

    def get(self, table: str, record_id: str, select: str = "*") -> dict[str, Any] | None:
        ...

    def insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    def update(self, table: str, record_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    def upsert(self, table: str, payload: dict[str, Any], on_conflict: str) -> dict[str, Any]:
        ...


class AuthPort(Protocol):
    def sign_in(self, email: str, password: str) -> dict[str, Any]:
        ...

    def get_user(self, access_token: str) -> dict[str, Any] | None:
        ...

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        ...

    def recover(self, email: str) -> None:
        ...

    def create_user(self, email: str, password: str, full_name: str) -> dict[str, Any]:
        ...

    def invite_user(self, email: str, full_name: str) -> dict[str, Any] | None:
        ...

    def sign_out(self, access_token: str) -> None:
        ...


class ProfilePort(Protocol):
    def get_by_id(self, user_id: str) -> Actor | None:
        ...

    def get_by_email(self, email: str) -> Actor | None:
        ...

    def list_users(self, organization_id: str) -> list[dict[str, Any]]:
        ...

    def upsert_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    def update_profile(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...


class StoragePort(Protocol):
    def signed_url(self, bucket: str, path: str, expires: int = 300) -> str:
        ...


class EmailPort(Protocol):
    def send(self, to: str, subject: str, body: str) -> None:
        ...


class MLInferencePort(Protocol):
    def estimate(self, features: dict[str, Any]) -> dict[str, Any]:
        ...


class AuditPort(Protocol):
    def record(self, payload: dict[str, Any]) -> None:
        ...


class NotificationPort(Protocol):
    def notify(self, payload: dict[str, Any]) -> None:
        ...
