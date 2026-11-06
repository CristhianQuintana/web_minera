from __future__ import annotations

from typing import Any

import httpx

from app.domain.entities import Actor
from app.domain.exceptions import NotFoundError, UnauthorizedError
from app.domain.services.profile_status import normalize_role
from app.domain.value_objects import UserRole
from app.application.messages import JSON_MIME, MSG_BAD_CREDENTIALS, MSG_SESSION_EXPIRED, MSG_ACTIVATE_FAILED
from app.infrastructure.configuration.settings import Settings


class SupabaseGateway:
    """Adaptador outbound. El dominio nunca importa este módulo."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._url = settings.supabase_url.rstrip("/")
        self._anon = settings.supabase_anon_key
        self._service = settings.supabase_service_role_key

    def _headers(self, access_token: str | None = None, admin: bool = False) -> dict[str, str]:
        # Service role solo cuando existe; si no, usar JWT del usuario (nunca anon sin token
        # para lecturas de perfil autenticado).
        if admin and self._service:
            return {
                "apikey": self._anon or self._service,
                "Authorization": f"Bearer {self._service}",
                "Content-Type": JSON_MIME,
                "Accept": JSON_MIME,
            }
        token = access_token or self._anon
        return {
            "apikey": self._anon,
            "Authorization": f"Bearer {token}",
            "Content-Type": JSON_MIME,
            "Accept": JSON_MIME,
        }

    def _rest(self, admin: bool = False, access_token: str | None = None) -> httpx.Client:
        return httpx.Client(
            base_url=f"{self._url}/rest/v1",
            headers=self._headers(access_token, admin=admin),
            timeout=30.0,
        )

    def _ensure_table_available(self, table: str, response: httpx.Response) -> None:
        body: dict[str, Any] = {}
        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                body = parsed
        except Exception:
            body = {}
        message = str(body.get("message") or body.get("error") or "")
        code = str(body.get("code") or "")
        missing = (
            response.status_code == 404
            or code in {"PGRST205", "42P01"}
            or "Could not find the table" in message
            or f"'{table}'" in message and "does not exist" in message.lower()
            or f"public.{table}" in message and "schema cache" in message.lower()
        )
        if missing:
            raise NotFoundError(
                f"La tabla '{table}' no está disponible en Supabase. "
                "Ejecuta database/seeds/APPLY_FIX_BALANCE_ML_DEMO.sql en el SQL Editor."
            )
        if response.status_code >= 400:
            response.raise_for_status()

    def sign_in(self, email: str, password: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self._url}/auth/v1/token?grant_type=password",
            headers={"apikey": self._anon, "Content-Type": JSON_MIME},
            json={"email": email, "password": password},
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise UnauthorizedError(MSG_BAD_CREDENTIALS)
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
            headers={"apikey": self._anon, "Content-Type": JSON_MIME},
            json={"refresh_token": refresh_token},
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise UnauthorizedError(MSG_SESSION_EXPIRED)
        return response.json()

    def recover(self, email: str) -> None:
        httpx.post(
            f"{self._url}/auth/v1/recover",
            headers={"apikey": self._anon, "Content-Type": JSON_MIME},
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
            headers={"apikey": self._anon, "Content-Type": JSON_MIME},
            json={"email": email, "password": password, "data": {"full_name": full_name}},
            timeout=30.0,
        )
        if response.status_code >= 400:
            raise UnauthorizedError(MSG_ACTIVATE_FAILED)
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


    @staticmethod
    def _filter_param(key: str, value: Any) -> tuple[str, str]:
        if key.endswith("__gte"):
            return key.replace("__gte", ""), f"gte.{value}"
        if key.endswith("__lte"):
            return key.replace("__lte", ""), f"lte.{value}"
        if key.endswith("__neq"):
            return key.replace("__neq", ""), f"neq.{value}"
        if key.endswith("__in"):
            return key.replace("__in", ""), f"in.({value})"
        return key, f"eq.{value}"

    def _build_select_params(
        self,
        filters: dict[str, Any] | None,
        search: tuple[list[str], str] | None,
        order: str,
        limit: int,
        offset: int,
        select: str,
    ) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = [("select", select)]
        if filters:
            for key, value in filters.items():
                if value is None or value == "":
                    continue
                params.append(self._filter_param(key, value))
        if search and search[1]:
            or_parts = ",".join(f"{col}.ilike.*{search[1]}*" for col in search[0])
            params.append(("or", f"({or_parts})"))
        params.append(("order", order))
        params.append(("limit", str(limit)))
        params.append(("offset", str(offset)))
        return params

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
        params = self._build_select_params(filters, search, order, limit, offset, select)
        with self._rest(admin=admin, access_token=access_token) as client:
            response = client.get(
                f"/{table}",
                params=params,
                headers={"Prefer": "count=exact"},
            )
            self._ensure_table_available(table, response)
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
            self._ensure_table_available(table, response)
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
            if isinstance(data, list) and data:
                return data[0]
            if isinstance(data, dict):
                return data
            return {}

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
                "Content-Type": JSON_MIME,
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
        role = UserRole(normalize_role(row.get("role")))
        status = str(row.get("status") or "inactive").strip().lower()
        if status not in {"active", "inactive"}:
            status = "active" if status in {"true", "1", "yes"} else "inactive"
        return Actor(
            id=row["id"],
            email=row.get("email") or email,
            full_name=row.get("full_name") or "",
            role=role,
            organization_id=str(row.get("organization_id") or ""),
            status=status,
            invitation_status=str(row.get("invitation_status") or "active"),
            last_activity_at=row.get("last_activity_at"),
        )
