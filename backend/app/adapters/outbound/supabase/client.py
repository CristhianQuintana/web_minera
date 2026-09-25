from __future__ import annotations

from typing import Any

import httpx

from app.domain.entities import Actor
from app.domain.exceptions import UnauthorizedError
from app.domain.value_objects import UserRole
from app.infrastructure.configuration.settings import Settings


class SupabaseGateway:
    """Adaptador outbound. El dominio nunca importa este módulo."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._url = settings.supabase_url.rstrip("/")
        self._anon = settings.supabase_anon_key
        self._service = settings.supabase_service_role_key

    def _headers(self, access_token: str | None = None, admin: bool = False) -> dict[str, str]:
        key = self._service if admin and self._service else self._anon
        token = key
        if access_token and not admin:
            token = access_token
        elif admin and self._service:
            token = self._service
        return {
            "apikey": key if (admin and self._service) else self._anon,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _rest(self, admin: bool = False, access_token: str | None = None) -> httpx.Client:
        return httpx.Client(
            base_url=f"{self._url}/rest/v1",
            headers=self._headers(access_token, admin=admin),
            timeout=30.0,
        )

    def sign_in(self, email: str, password: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self._url}/auth/v1/token?grant_type=password",
            headers={"apikey": self._anon, "Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise UnauthorizedError("El correo o la contraseña no son correctos.")
        return response.json()

    def get_user(self, access_token: str) -> dict[str, Any] | None:
        response = httpx.get(
            f"{self._url}/auth/v1/user",
            headers=self._headers(access_token),
            timeout=30.0,
        )
        if response.status_code >= 400:
            return None
        return response.json()

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self._url}/auth/v1/token?grant_type=refresh_token",
            headers={"apikey": self._anon, "Content-Type": "application/json"},
            json={"refresh_token": refresh_token},
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
        return response.json()

    def recover(self, email: str) -> None:
        httpx.post(
            f"{self._url}/auth/v1/recover",
            headers={"apikey": self._anon, "Content-Type": "application/json"},
            json={"email": email},
            timeout=30.0,
        )

    def sign_out(self, access_token: str) -> None:
        httpx.post(
            f"{self._url}/auth/v1/logout",
            headers=self._headers(access_token),
            timeout=30.0,
        )

    def create_user(self, email: str, password: str, full_name: str) -> dict[str, Any]:
        if self._service:
            response = httpx.post(
                f"{self._url}/auth/v1/admin/users",
                headers=self._headers(admin=True),
                json={
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"full_name": full_name},
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        response = httpx.post(
            f"{self._url}/auth/v1/signup",
            headers={"apikey": self._anon, "Content-Type": "application/json"},
            json={"email": email, "password": password, "data": {"full_name": full_name}},
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise UnauthorizedError("No pudimos activar la cuenta. Intenta nuevamente.")
        return response.json()

    def invite_user(self, email: str, full_name: str) -> dict[str, Any] | None:
        if not self._service:
            return None
        response = httpx.post(
            f"{self._url}/auth/v1/invite",
            headers=self._headers(admin=True),
            json={"email": email, "data": {"full_name": full_name}},
            timeout=30.0,
        )
        if response.status_code >= 400:
            return None
        return response.json()

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
    ) -> tuple[list[dict[str, Any]], int]:
        params: list[tuple[str, str]] = [("select", select)]
        if filters:
            for key, value in filters.items():
                if value is None or value == "":
                    continue
                if key.endswith("__gte"):
                    params.append((key.replace("__gte", ""), f"gte.{value}"))
                elif key.endswith("__lte"):
                    params.append((key.replace("__lte", ""), f"lte.{value}"))
                elif key.endswith("__neq"):
                    params.append((key.replace("__neq", ""), f"neq.{value}"))
                elif key.endswith("__in"):
                    params.append((key.replace("__in", ""), f"in.({value})"))
                else:
                    params.append((key, f"eq.{value}"))
        if search and search[1]:
            or_parts = ",".join(f"{col}.ilike.*{search[1]}*" for col in search[0])
            params.append(("or", f"({or_parts})"))
        params.append(("order", order.replace(".", ".")))
        params.append(("limit", str(limit)))
        params.append(("offset", str(offset)))
        with self._rest(admin=admin, access_token=access_token) as client:
            response = client.get(
                f"/{table}",
                params=params,
                headers={"Prefer": "count=exact"},
            )
            response.raise_for_status()
            total = 0
            content_range = response.headers.get("content-range", "")
            if "/" in content_range:
                total_part = content_range.split("/")[-1]
                total = int(total_part) if total_part.isdigit() else 0
            data = response.json()
            return data if isinstance(data, list) else [], total

    def get(
        self,
        table: str,
        record_id: str,
        select: str = "*",
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any] | None:
        items, _ = self.select(
            table,
            {"id": record_id},
            select=select,
            limit=1,
            access_token=access_token,
            admin=admin,
        )
        return items[0] if items else None

    def insert(
        self,
        table: str,
        payload: dict[str, Any],
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any]:
        with self._rest(admin=admin, access_token=access_token) as client:
            response = client.post(
                f"/{table}",
                json=payload,
                headers={"Prefer": "return=representation"},
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if isinstance(data, list) else data

    def update(
        self,
        table: str,
        record_id: str,
        payload: dict[str, Any],
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any]:
        with self._rest(admin=admin, access_token=access_token) as client:
            response = client.patch(
                f"/{table}",
                params={"id": f"eq.{record_id}"},
                json=payload,
                headers={"Prefer": "return=representation"},
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})

    def upsert(
        self,
        table: str,
        payload: dict[str, Any],
        on_conflict: str,
        access_token: str | None = None,
        admin: bool = False,
    ) -> dict[str, Any]:
        with self._rest(admin=admin, access_token=access_token) as client:
            response = client.post(
                f"/{table}",
                params={"on_conflict": on_conflict},
                json=payload,
                headers={"Prefer": "return=representation,resolution=merge-duplicates"},
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if isinstance(data, list) else data

    def signed_url(self, bucket: str, path: str, expires: int = 300) -> str:
        key = self._service or self._anon
        response = httpx.post(
            f"{self._url}/storage/v1/object/sign/{bucket}/{path}",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={"expiresIn": expires},
            timeout=30.0,
        )
        response.raise_for_status()
        signed = response.json().get("signedURL", "")
        if signed.startswith("http"):
            return signed
        return f"{self._url}/storage/v1{signed}"

    def map_actor(self, row: dict[str, Any], email: str = "") -> Actor:
        return Actor(
            id=row["id"],
            email=row.get("email") or email,
            full_name=row.get("full_name") or "",
            role=UserRole(row.get("role") or "auditor"),
            organization_id=row.get("organization_id") or "",
            status=row.get("status") or "inactive",
            invitation_status=row.get("invitation_status") or "active",
            last_activity_at=row.get("last_activity_at"),
        )
