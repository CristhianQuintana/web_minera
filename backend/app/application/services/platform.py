from __future__ import annotations

import csv
import hashlib
import io
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.application.auth_context import AuthContext
from app.application.profile_access import assert_profile_can_login, normalize_profile_row
from app.application.dto import (
    ActivateCommand,
    AlertReviewCommand,
    CustodyCommand,
    InviteCommand,
    LoginCommand,
    PageQuery,
    ProfileCommand,
    ReceptionCommand,
    RegisterLotCommand,
    SettingsCommand,
    ToleranceCommand,
    TransportCommand,
    WeighingCommand,
)
from app.domain.entities import Actor
from app.domain.exceptions import (
    ForbiddenError,
    InactiveAccountError,
    InvitationInvalidError,
    NotFoundError,
    UnauthorizedError,
)
from app.domain.rules import CustodyTransferRules, LotRegistrationRules, ReceptionRules
from app.domain.services import DeviationCalculator, MassBalanceCalculator
from app.domain.value_objects import Permission, UserRole, allows
from app.ports.outbound.gateway import AppConfigPort, DataGatewayPort
from app.ports.outbound.repositories import EmailPort, MLInferencePort

# Organización piloto del bootstrap (UUID estable de migraciones). No es demo-org.
PILOTO_ORG_ID = "e857fa80-1678-4b27-b80f-c38f471a8931"
PILOTO_ORG_NAME = "Cooperativa piloto"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _page(query: PageQuery) -> tuple[int, int, str]:
    order = f"{query.sort}.{query.order}"
    return query.page_size, (query.page - 1) * query.page_size, order


def _envelope(items: list[Any], total: int, query: PageQuery) -> dict[str, Any]:
    return {
        "items": items,
        "page": query.page,
        "page_size": query.page_size,
        "total": total,
    }


class PlatformService:
    """Orquesta casos de uso. Recibe únicamente puertos outbound;
    el composition root inyecta adaptadores concretos."""

    def __init__(
        self,
        gateway: DataGatewayPort,
        settings: AppConfigPort,
        email: EmailPort,
        ml: MLInferencePort,
    ) -> None:
        self._db = gateway
        self._settings = settings
        self._email = email
        self._ml = ml
        self._balance = MassBalanceCalculator()
        self._deviation = DeviationCalculator()

    def _admin(self) -> bool:
        return self._settings.has_service_role

    def _token(self, ctx: AuthContext | None) -> str | None:
        return ctx.access_token if ctx else None

    def _reconcile_confirmed_profile(
        self,
        profile: dict[str, Any],
        auth_user: dict[str, Any],
        access_token: str,
    ) -> dict[str, Any]:
        from app.domain.services.profile_status import invitation_blocks_login, profile_is_active

        if profile_is_active(profile):
            return profile
        if invitation_blocks_login(profile):
            return profile
        if not auth_user.get("email_confirmed_at"):
            return profile
        if auth_user.get("banned_until"):
            return profile
        patch = {
            "status": "active",
            "invitation_status": "active",
            "updated_at": _now().isoformat(),
        }
        merged = dict(profile)
        merged.update(patch)
        # Persistir solo con service role (RLS de profiles suele ser solo SELECT).
        if self._admin():
            try:
                updated = self._db.update(
                    "profiles",
                    profile["id"],
                    patch,
                    access_token=access_token,
                    admin=True,
                )
                if isinstance(updated, dict) and updated:
                    merged.update(updated)
            except Exception:
                pass
        return merged

    def _ensure_profile_organization(
        self,
        profile: dict[str, Any],
        auth_user: dict[str, Any],
        access_token: str,
    ) -> dict[str, Any]:
        org_id = str(profile.get("organization_id") or "").strip()
        if org_id and org_id not in {"demo-org", "demo-local-cristhian"}:
            return profile
        if not auth_user.get("email_confirmed_at") or auth_user.get("banned_until"):
            return profile

        merged = dict(profile)
        merged["organization_id"] = PILOTO_ORG_ID
        merged["status"] = "active"
        if not merged.get("invitation_status") or merged.get("invitation_status") == "pending":
            merged["invitation_status"] = "active"

        patch = {
            "organization_id": PILOTO_ORG_ID,
            "status": "active",
            "invitation_status": merged["invitation_status"],
            "updated_at": _now().isoformat(),
        }
        try:
            if self._admin():
                existing = self._db.get("organizations", PILOTO_ORG_ID, admin=True)
                if not existing:
                    self._db.insert(
                        "organizations",
                        {"id": PILOTO_ORG_ID, "name": PILOTO_ORG_NAME},
                        admin=True,
                    )
                patched = self._db.update("profiles", profile["id"], patch, admin=True)
            else:
                patched = self._db.update(
                    "profiles",
                    profile["id"],
                    patch,
                    access_token=access_token,
                )
            if isinstance(patched, dict) and patched:
                merged.update(patched)
                if not merged.get("organization_id"):
                    merged["organization_id"] = PILOTO_ORG_ID
        except Exception:
            pass
        return merged


    def _audit(self, ctx: AuthContext, action: str, entity: str, entity_id: str | None, result: str, extra: dict | None = None) -> None:
        self._db.insert(
            "audit_log",
            {
                "user_id": ctx.actor.id,
                "action": action,
                "entity": entity,
                "entity_id": entity_id,
                "result": result,
                "organization_id": ctx.actor.organization_id,
                "context": extra or {},
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )

    def authenticate(self, command: LoginCommand) -> dict[str, Any]:
        session = self._db.sign_in(command.email.strip(), command.password)
        user = session.get("user") or {}
        user_id = user.get("id") or ""
        access_token = session.get("access_token") or ""
        if not user_id:
            raise UnauthorizedError("El correo o la contraseña no son correctos.")
        if not access_token or access_token.startswith("demo-"):
            raise UnauthorizedError("El correo o la contraseña no son correctos.")
        profile = None
        if self._admin():
            profile = self._db.get("profiles", user_id, admin=True)
        if not profile:
            profile = self._db.get("profiles", user_id, access_token=access_token)
        if not profile:
            raise UnauthorizedError("El correo o la contraseña no son correctos.")
        # Si Auth confirmó al usuario y no está baneado, pero profiles.status quedó
        # inconsistente (p. ej. inactive con invitation activa), alinear el perfil.
        # No rehabilita cuentas con invitation_status inactive/expired (baja explícita).
        profile = self._reconcile_confirmed_profile(profile, user, access_token)
        assert_profile_can_login(profile)
        profile = self._ensure_profile_organization(profile, user, access_token)
        normalized = normalize_profile_row(profile, command.email.strip())
        actor = self._db.map_actor(normalized, command.email.strip())
        if not actor.organization_id or actor.organization_id in {"demo-org", "demo-local-cristhian"}:
            raise UnauthorizedError("Tu cuenta no tiene una organización válida asignada.")
        try:
            self._db.update(
                "profiles",
                actor.id,
                {
                    "last_activity_at": _now().isoformat(),
                    "email": command.email.strip(),
                    "status": "active",
                    "role": actor.role.value,
                    "organization_id": actor.organization_id,
                },
                access_token=access_token,
                admin=self._admin(),
            )
        except Exception:
            # La sesión Auth ya es válida; no fallar el login por telemetría/RLS.
            pass
        return {
            "access_token": access_token,
            "refresh_token": session.get("refresh_token"),
            "expires_in": session.get("expires_in"),
            "user": self.serialize_actor(actor),
        }

    def serialize_actor(self, actor: Any) -> dict[str, Any]:
        from app.domain.value_objects import permissions_for

        return {
            "id": actor.id,
            "email": actor.email,
            "full_name": actor.full_name,
            "role": actor.role.value,
            "role_label": actor.role.label,
            "organization_id": actor.organization_id,
            "status": actor.status,
            "invitation_status": actor.invitation_status,
            "permissions": sorted(p.value for p in permissions_for(actor.role)),
        }

    def resolve_context(self, access_token: str) -> AuthContext:
        if not access_token or access_token.startswith("demo-"):
            raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
        user = self._db.get_user(access_token)
        if not user or not user.get("id"):
            raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
        profile = self._db.get("profiles", user["id"], access_token=access_token, admin=self._admin())
        if not profile:
            raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
        profile = self._reconcile_confirmed_profile(profile, user, access_token)
        assert_profile_can_login(profile)
        profile = self._ensure_profile_organization(profile, user, access_token)
        email = user.get("email") or profile.get("email") or ""
        actor = self._db.map_actor(normalize_profile_row(profile, email), email)
        if not actor.organization_id or actor.organization_id in {"demo-org", "demo-local-cristhian"}:
            raise UnauthorizedError("Tu cuenta no tiene una organización válida asignada.")
        return AuthContext(actor=actor, access_token=access_token)

    def forgot_password(self, email: str) -> dict[str, str]:
        self._db.recover(email)
        return {
            "message": "Si existe una cuenta asociada a este correo, recibirás instrucciones para recuperar el acceso."
        }

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        if not refresh_token or refresh_token.startswith("demo-"):
            raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
        session = self._db.refresh(refresh_token)
        access_token = session.get("access_token") or ""
        if not access_token or access_token.startswith("demo-"):
            raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
        return session

    def logout(self, access_token: str) -> None:
        if not access_token or access_token.startswith("demo-"):
            return
        self._db.sign_out(access_token)

    def dashboard(self, ctx: AuthContext) -> dict[str, Any]:
        org = ctx.actor.organization_id
        token = ctx.access_token
        lots, lots_total = self._db.select("lots", {"organization_id": org}, limit=5, access_token=token, admin=self._admin())
        transfers, transfers_total = self._db.select("custody_transfers", limit=1, access_token=token, admin=self._admin())
        receptions, receptions_total = self._db.select("receptions", limit=1, access_token=token, admin=self._admin())
        alerts, alerts_total = self._db.select(
            "alerts",
            {"organization_id": org, "status__in": "new,in_review"},
            limit=5,
            access_token=token,
            admin=self._admin(),
        )
        transports, transports_total = self._db.select("transports", limit=5, access_token=token, admin=self._admin())
        role = ctx.actor.role.canonical
        cards: list[dict[str, Any]]
        if role == UserRole.AUDITOR:
            cards = [
                {"key": "alerts", "label": "Alertas abiertas", "value": alerts_total, "href": "/alerts"},
                {"key": "lots", "label": "Lotes", "value": lots_total, "href": "/lots"},
                {"key": "receptions", "label": "Recepciones", "value": receptions_total, "href": "/receptions"},
                {"key": "transfers", "label": "Transferencias", "value": transfers_total, "href": "/custody"},
            ]
        elif role == UserRole.PRODUCER:
            cards = [
                {"key": "lots", "label": "Mis lotes", "value": lots_total, "href": "/lots"},
                {"key": "transfers", "label": "Custodias", "value": transfers_total, "href": "/custody"},
                {"key": "alerts", "label": "Alertas", "value": alerts_total, "href": "/alerts"},
                {"key": "transports", "label": "Transportes", "value": transports_total, "href": "/transport"},
            ]
        elif role == UserRole.CARRIER:
            cards = [
                {"key": "transports", "label": "Transportes", "value": transports_total, "href": "/transport"},
                {"key": "lots", "label": "Lotes", "value": lots_total, "href": "/lots"},
                {"key": "transfers", "label": "Custodias", "value": transfers_total, "href": "/custody"},
                {"key": "alerts", "label": "Alertas", "value": alerts_total, "href": "/alerts"},
            ]
        elif role == UserRole.RECEIVER:
            cards = [
                {"key": "receptions", "label": "Recepciones", "value": receptions_total, "href": "/receptions"},
                {"key": "alerts", "label": "Alertas", "value": alerts_total, "href": "/alerts"},
                {"key": "lots", "label": "Lotes", "value": lots_total, "href": "/lots"},
                {"key": "transfers", "label": "Transferencias", "value": transfers_total, "href": "/custody"},
            ]
        else:
            cards = [
                {"key": "lots", "label": "Lotes", "value": lots_total, "href": "/lots"},
                {"key": "transfers", "label": "Transferencias", "value": transfers_total, "href": "/custody"},
                {"key": "receptions", "label": "Recepciones", "value": receptions_total, "href": "/receptions"},
                {"key": "alerts", "label": "Alertas abiertas", "value": alerts_total, "href": "/alerts"},
            ]
        return {
            "role": ctx.actor.role.value,
            "cards": cards,
            "recent_lots": lots,
            "recent_alerts": alerts,
            "recent_transports": transports,
        }

    def list_lots(self, ctx: AuthContext, query: PageQuery) -> dict[str, Any]:
        ctx.require(Permission.VIEW_LOTS)
        limit, offset, order = _page(query)
        filters: dict[str, Any] = {"organization_id": ctx.actor.organization_id}
        if query.status:
            filters["status"] = query.status
        filters.update(query.extra)
        items, total = self._db.select(
            "lots",
            filters,
            search=(["code", "qr_payload", "mineral"], query.q or ""),
            order=order,
            limit=limit,
            offset=offset,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        return _envelope(items, total, query)

    def _related_rows(self, ctx: AuthContext, table: str, lot_id: str, limit: int = 50) -> list[Any]:
        try:
            items, _ = self._db.select(
                table,
                {"lot_id": lot_id},
                limit=limit,
                access_token=ctx.access_token,
                admin=self._admin(),
            )
            return items
        except Exception:
            return []

    def get_lot(self, ctx: AuthContext, lot_id: str) -> dict[str, Any]:
        ctx.require(Permission.VIEW_LOTS)
        lot = self._db.get("lots", lot_id, access_token=ctx.access_token, admin=self._admin())
        if not lot:
            raise NotFoundError("El lote no existe.")
        if str(lot.get("organization_id") or "") != str(ctx.actor.organization_id):
            raise ForbiddenError("No tienes permisos para realizar esta acción.")
        evidences = self._related_rows(ctx, "evidences", lot_id)
        transfers = self._related_rows(ctx, "custody_transfers", lot_id)
        transports = self._related_rows(ctx, "transports", lot_id)
        receptions = self._related_rows(ctx, "receptions", lot_id)
        weighings = self._related_rows(ctx, "weighings", lot_id)
        audits = self._related_rows(ctx, "audit_log", lot_id)
        balance = None
        try:
            if allows(ctx.actor.role, Permission.VIEW_BALANCE):
                received = float(receptions[0]["received_quantity"]) if receptions else None
                balance = self._balance_for_lot(ctx, lot, received, self._active_tolerance(ctx))
        except Exception:
            balance = None
        return {
            **lot,
            "evidences": evidences,
            "custody": transfers,
            "transports": transports,
            "receptions": receptions,
            "weighings": weighings,
            "balance": balance,
            "audit": audits,
        }

    def lot_timeline(self, ctx: AuthContext, lot_id: str) -> dict[str, Any]:
        ctx.require(Permission.VIEW_LOTS)
        events, _ = self._db.select(
            "lot_events",
            {"lot_id": lot_id},
            order="occurred_at.asc",
            limit=200,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        return {"items": events}

    def register_lot(self, ctx: AuthContext, command: RegisterLotCommand) -> dict[str, Any]:
        ctx.require(Permission.REGISTER_LOT)
        LotRegistrationRules.validate(command.code, command.mineral, command.quantity, command.unit)
        client_id = command.client_operation_id or str(uuid.uuid4())
        payload = {
            "client_operation_id": client_id,
            "organization_id": ctx.actor.organization_id,
            "mining_operation_id": command.mining_operation_id,
            "code": command.code.strip(),
            "mineral": command.mineral,
            "quantity": command.quantity,
            "unit": command.unit,
            "status": "registered",
            "latitude": command.latitude,
            "longitude": command.longitude,
            "qr_payload": command.qr_payload or command.code.strip(),
            "observation": command.observation,
            "created_by": ctx.actor.id,
        }
        lot = self._db.insert("lots", payload, access_token=ctx.access_token, admin=self._admin())
        self._db.insert(
            "lot_events",
            {
                "client_operation_id": str(uuid.uuid4()),
                "lot_id": lot["id"],
                "event_type": "registered",
                "occurred_at": _now().isoformat(),
                "user_id": ctx.actor.id,
                "notes": "Registro digital de lote",
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        self._audit(ctx, "register_lot", "lot", lot["id"], "success")
        return lot

    def export_lots(self, ctx: AuthContext, query: PageQuery) -> str:
        ctx.require(Permission.EXPORT)
        data = self.list_lots(ctx, PageQuery(page=1, page_size=500, q=query.q, status=query.status))
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=["code", "mineral", "quantity", "unit", "status", "created_at"],
            extrasaction="ignore",
        )
        writer.writeheader()
        for item in data["items"]:
            writer.writerow(item)
        return buffer.getvalue()

    def list_table(
        self,
        ctx: AuthContext,
        table: str,
        permission: Permission,
        query: PageQuery,
        search_cols: list[str],
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ctx.require(permission)
        limit, offset, order = _page(query)
        applied = dict(filters or {})
        if query.status:
            applied["status"] = query.status
        applied.update(query.extra)
        items, total = self._db.select(
            table,
            applied,
            search=(search_cols, query.q or ""),
            order=order,
            limit=limit,
            offset=offset,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        return _envelope(items, total, query)

    def get_row(self, ctx: AuthContext, table: str, record_id: str, permission: Permission) -> dict[str, Any]:
        ctx.require(permission)
        row = self._db.get(table, record_id, access_token=ctx.access_token, admin=self._admin())
        if not row:
            raise NotFoundError("El recurso solicitado no existe o ya no está disponible.")
        return row

    def start_custody(self, ctx: AuthContext, command: CustodyCommand) -> dict[str, Any]:
        ctx.require(Permission.TRANSFER_CUSTODY)
        lot = self.get_row(ctx, "lots", command.lot_id, Permission.VIEW_LOTS)
        CustodyTransferRules.validate(command.origin, command.destination, command.quantity, lot.get("status", ""))
        row = self._db.insert(
            "custody_transfers",
            {
                "client_operation_id": command.client_operation_id or str(uuid.uuid4()),
                "lot_id": command.lot_id,
                "origin": command.origin,
                "destination": command.destination,
                "quantity": command.quantity,
                "occurred_at": _now().isoformat(),
                "notes": command.notes,
                "created_by": ctx.actor.id,
                "responsible": ctx.actor.full_name,
                "status": "completed",
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        self._db.update("lots", command.lot_id, {"status": "transferred"}, access_token=ctx.access_token, admin=self._admin())
        self._audit(ctx, "custody_transfer", "custody_transfer", row["id"], "success", {"lot_id": command.lot_id})
        return row

    def register_transport(self, ctx: AuthContext, command: TransportCommand) -> dict[str, Any]:
        ctx.require(Permission.REGISTER_TRANSPORT)
        row = self._db.insert(
            "transports",
            {
                "client_operation_id": command.client_operation_id or str(uuid.uuid4()),
                "lot_id": command.lot_id,
                "vehicle": command.vehicle,
                "plate": command.plate,
                "driver": command.driver,
                "status": "in_progress",
                "started_at": _now().isoformat(),
                "origin": command.origin,
                "destination": command.destination,
                "notes": command.notes,
                "assigned_to": ctx.actor.id,
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        self._db.update("lots", command.lot_id, {"status": "inTransit"}, access_token=ctx.access_token, admin=self._admin())
        self._audit(ctx, "register_transport", "transport", row["id"], "success")
        return row

    def register_reception(self, ctx: AuthContext, command: ReceptionCommand) -> dict[str, Any]:
        ctx.require(Permission.REGISTER_RECEPTION)
        ReceptionRules.validate(command.declared_quantity, command.received_quantity)
        row = self._db.insert(
            "receptions",
            {
                "client_operation_id": command.client_operation_id or str(uuid.uuid4()),
                "lot_id": command.lot_id,
                "declared_quantity": command.declared_quantity,
                "received_quantity": command.received_quantity,
                "unit": command.unit,
                "occurred_at": _now().isoformat(),
                "responsible": command.responsible,
                "status": "confirmed",
                "notes": command.notes,
                "created_by": ctx.actor.id,
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        self._db.update("lots", command.lot_id, {"status": "received"}, access_token=ctx.access_token, admin=self._admin())
        self.recalculate_balance(ctx, command.lot_id)
        self._audit(ctx, "register_reception", "reception", row["id"], "success")
        return row

    def register_weighing(self, ctx: AuthContext, command: WeighingCommand) -> dict[str, Any]:
        ctx.require(Permission.REGISTER_WEIGHING)
        row = self._db.insert(
            "weighings",
            {
                "client_operation_id": command.client_operation_id or str(uuid.uuid4()),
                "lot_id": command.lot_id,
                "reception_id": command.reception_id,
                "weight": command.weight,
                "unit": command.unit,
                "occurred_at": _now().isoformat(),
                "instrument": command.instrument,
                "responsible": command.responsible,
                "notes": command.notes,
                "created_by": ctx.actor.id,
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        self._audit(ctx, "register_weighing", "weighing", row["id"], "success")
        return row

    def _active_tolerance(self, ctx: AuthContext) -> dict[str, Any] | None:
        try:
            items, _ = self._db.select(
                "tolerance_rules",
                {
                    "organization_id": ctx.actor.organization_id,
                    "rule_key": "mass_balance_percent",
                    "is_active": True,
                },
                order="version.desc",
                limit=1,
                access_token=ctx.access_token,
                admin=self._admin(),
            )
            return items[0] if items else None
        except Exception:
            return None

    def _balance_for_lot(
        self,
        ctx: AuthContext,
        lot: dict[str, Any],
        received: float | None,
        rule: dict[str, Any] | None,
    ) -> dict[str, Any]:
        rule_dict = rule if isinstance(rule, dict) else {}
        tolerance = float(rule_dict["value"]) if rule_dict.get("value") is not None else 3.0
        status, difference, percent = self._balance.calculate(
            float(lot["quantity"]),
            float(received) if received is not None else None,
            tolerance,
        )
        return {
            "id": lot["id"],
            "organization_id": ctx.actor.organization_id,
            "lot_id": lot["id"],
            "lot_code": lot.get("code"),
            "mineral": lot.get("mineral"),
            "origin_quantity": lot["quantity"],
            "received_quantity": received,
            "difference": difference,
            "difference_percent": percent,
            "tolerance_value": tolerance,
            "tolerance_unit": rule_dict.get("unit") or "percent",
            "tolerance_rule_id": rule_dict.get("id"),
            "tolerance_version": rule_dict.get("version"),
            "status": status.value,
            "calculated_at": _now().isoformat(),
        }

    def list_balances(self, ctx: AuthContext, query: PageQuery) -> dict[str, Any]:
        """Balance calculado en vivo desde lots + receptions (sin tabla mass_balances)."""
        ctx.require(Permission.VIEW_BALANCE)
        limit, offset, order = _page(query)
        lots, total = self._db.select(
            "lots",
            {"organization_id": ctx.actor.organization_id},
            search=(["code", "mineral"], query.q or ""),
            order=order if query.sort in {"created_at", "code", "quantity"} else "created_at.desc",
            limit=limit,
            offset=offset,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        rule = self._active_tolerance(ctx)
        latest_received: dict[str, float] = {}
        if lots:
            lot_ids = ",".join(str(lot["id"]) for lot in lots)
            receptions, _ = self._db.select(
                "receptions",
                {"lot_id__in": lot_ids},
                order="occurred_at.desc",
                limit=max(limit * 5, 50),
                access_token=ctx.access_token,
                admin=self._admin(),
            )
            for reception in receptions:
                lot_id = str(reception.get("lot_id") or "")
                if lot_id and lot_id not in latest_received:
                    latest_received[lot_id] = float(reception["received_quantity"])
        items = [
            self._balance_for_lot(ctx, lot, latest_received.get(str(lot["id"])), rule)
            for lot in lots
        ]
        if query.status:
            items = [item for item in items if item.get("status") == query.status]
        return _envelope(items, total, query)

    def get_balance(self, ctx: AuthContext, lot_id: str) -> dict[str, Any]:
        ctx.require(Permission.VIEW_BALANCE)
        lot = self.get_row(ctx, "lots", lot_id, Permission.VIEW_LOTS)
        if str(lot.get("organization_id") or "") != str(ctx.actor.organization_id):
            raise ForbiddenError("No tienes permisos para realizar esta acción.")
        receptions, _ = self._db.select(
            "receptions",
            {"lot_id": lot_id},
            order="occurred_at.desc",
            limit=1,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        received = float(receptions[0]["received_quantity"]) if receptions else None
        return self._balance_for_lot(ctx, lot, received, self._active_tolerance(ctx))

    def recalculate_balance(self, ctx: AuthContext, lot_id: str) -> dict[str, Any]:
        row = self.get_balance(ctx, lot_id)
        if row.get("status") == "review_required":
            percent = float(row.get("difference_percent") or 0)
            tolerance = float(row.get("tolerance_value") or 3)
            self._ensure_alert(
                ctx,
                lot_id,
                "mass_balance",
                "high",
                "Desviación de balance de masas",
                f"La diferencia ({percent:.2f}%) supera la tolerancia {tolerance}% "
                f"(versión {row.get('tolerance_version')}).",
            )
        return row

    def _ensure_alert(self, ctx: AuthContext, lot_id: str, alert_type: str, severity: str, title: str, reason: str) -> None:
        existing, _ = self._db.select(
            "alerts",
            {"lot_id": lot_id, "alert_type": alert_type, "status__in": "new,in_review"},
            limit=1,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        if existing:
            return
        self._db.insert(
            "alerts",
            {
                "organization_id": ctx.actor.organization_id,
                "lot_id": lot_id,
                "severity": severity,
                "alert_type": alert_type,
                "title": title,
                "summary": reason,
                "reason": reason,
                "status": "new",
                "rule_applied": "mass_balance_percent",
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )

    def review_alert(self, ctx: AuthContext, alert_id: str, command: AlertReviewCommand) -> dict[str, Any]:
        ctx.require(Permission.REVIEW_ALERT)
        alert = self.get_row(ctx, "alerts", alert_id, Permission.VIEW_ALERTS)
        self._db.insert(
            "alert_reviews",
            {
                "alert_id": alert_id,
                "reviewer_id": ctx.actor.id,
                "result": command.result,
                "observation": command.observation,
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        updated = self._db.update(
            "alerts",
            alert_id,
            {"status": "attended", "updated_at": _now().isoformat()},
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        self._audit(ctx, "review_alert", "alert", alert_id, "success", {"previous": alert.get("status")})
        return updated

    def audit_case(self, ctx: AuthContext, lot_id: str) -> dict[str, Any]:
        ctx.require(Permission.VIEW_AUDIT)
        return self.get_lot(ctx, lot_id)

    def invite_user(self, ctx: AuthContext, command: InviteCommand) -> dict[str, Any]:
        ctx.require(Permission.MANAGE_USERS)
        if command.role not in {r.value for r in UserRole}:
            raise ForbiddenError("El rol indicado no es válido.")
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires = _now() + timedelta(hours=self._settings.invite_expiry_hours)
        invitation = self._db.insert(
            "invitations",
            {
                "email": command.email.lower(),
                "full_name": command.full_name,
                "role": command.role,
                "organization_id": ctx.actor.organization_id,
                "token_hash": token_hash,
                "invited_by": ctx.actor.id,
                "expires_at": expires.isoformat(),
                "status": "pending",
            },
            access_token=ctx.access_token,
            admin=True,
        )
        self._db.invite_user(command.email, command.full_name)
        link = f"{self._settings.invite_base_url}?token={token}"
        self._email.send(
            command.email,
            "Invitación a WEB_MINERA",
            (
                f"Hola {command.full_name},\n\n"
                f"Has sido invitado a WEB_MINERA con el rol {command.role}.\n"
                f"Activa tu cuenta: {link}\n"
                f"El enlace expira el {expires.isoformat()}.\n"
                "Si no esperabas este correo, ignóralo.\n"
            ),
        )
        self._audit(ctx, "invite_user", "invitation", invitation["id"], "success")
        return {"id": invitation["id"], "status": "pending", "message": "Invitación enviada correctamente."}

    def validate_invitation(self, token: str) -> dict[str, Any]:
        invitation = self._find_invitation(token)
        return {
            "full_name": invitation["full_name"],
            "email": invitation["email"],
            "role": invitation["role"],
            "expires_at": invitation["expires_at"],
        }

    def activate_account(self, command: ActivateCommand) -> dict[str, Any]:
        invitation = self._find_invitation(command.token)
        created = self._db.create_user(invitation["email"], command.password, command.full_name)
        user = created.get("user") or created
        user_id = user.get("id") or created.get("id")
        if not user_id:
            raise InvitationInvalidError("No pudimos activar la cuenta. Intenta nuevamente.")
        self._db.upsert(
            "profiles",
            {
                "id": user_id,
                "full_name": command.full_name,
                "role": invitation["role"],
                "organization_id": invitation["organization_id"],
                "status": "active",
                "invitation_status": "active",
                "email": invitation["email"],
            },
            "id",
            admin=True,
        )
        self._db.update(
            "invitations",
            invitation["id"],
            {"status": "accepted", "accepted_at": _now().isoformat()},
            admin=True,
        )
        return {"message": "Cuenta activada correctamente."}

    def _find_invitation(self, token: str) -> dict[str, Any]:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        items, _ = self._db.select("invitations", {"token_hash": token_hash}, limit=1, admin=True)
        if not items:
            raise InvitationInvalidError("Esta invitación ya no es válida.")
        invitation = items[0]
        expires = datetime.fromisoformat(invitation["expires_at"].replace("Z", "+00:00"))
        if invitation["status"] != "pending" or expires < _now():
            if invitation["status"] == "pending":
                self._db.update("invitations", invitation["id"], {"status": "expired"}, admin=True)
            raise InvitationInvalidError("Esta invitación ya no es válida.")
        return invitation

    def list_users(self, ctx: AuthContext, query: PageQuery) -> dict[str, Any]:
        ctx.require(Permission.MANAGE_USERS)
        return self.list_table(
            ctx,
            "profiles",
            Permission.MANAGE_USERS,
            query,
            ["full_name", "email", "role"],
            {"organization_id": ctx.actor.organization_id},
        )

    def set_user_status(self, ctx: AuthContext, user_id: str, active: bool) -> dict[str, Any]:
        ctx.require(Permission.MANAGE_USERS)
        payload = {
            "status": "active" if active else "inactive",
            "invitation_status": "active" if active else "inactive",
            "updated_at": _now().isoformat(),
        }
        row = self._db.update("profiles", user_id, payload, access_token=ctx.access_token, admin=True)
        self._audit(ctx, "activate_user" if active else "deactivate_user", "profile", user_id, "success")
        return row

    def resend_invite(self, ctx: AuthContext, user_id: str) -> dict[str, str]:
        ctx.require(Permission.MANAGE_USERS)
        profile = self.get_row(ctx, "profiles", user_id, Permission.MANAGE_USERS)
        if not profile.get("email"):
            raise NotFoundError("El usuario no tiene correo asociado.")
        self.invite_user(
            ctx,
            InviteCommand(full_name=profile["full_name"], email=profile["email"], role=profile["role"]),
        )
        return {"message": "Invitación reenviada correctamente."}

    def notifications(self, ctx: AuthContext, query: PageQuery) -> dict[str, Any]:
        return self.list_table(
            ctx,
            "notifications",
            Permission.VIEW_LOTS,
            query,
            ["title", "body"],
            {"user_id": ctx.actor.id},
        )

    def read_notification(self, ctx: AuthContext, notification_id: str) -> dict[str, Any]:
        return self._db.update(
            "notifications",
            notification_id,
            {"read_at": _now().isoformat()},
            access_token=ctx.access_token,
            admin=self._admin(),
        )

    def settings(self, ctx: AuthContext) -> dict[str, Any]:
        items, _ = self._db.select(
            "organization_settings",
            {"organization_id": ctx.actor.organization_id},
            limit=1,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        tolerances, _ = self._db.select(
            "tolerance_rules",
            {"organization_id": ctx.actor.organization_id},
            order="version.desc",
            limit=20,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        return {"settings": items[0] if items else {}, "tolerances": tolerances}

    def update_settings(self, ctx: AuthContext, command: SettingsCommand) -> dict[str, Any]:
        ctx.require(Permission.MANAGE_SETTINGS)
        current = self.settings(ctx)["settings"]
        payload = {
            "organization_id": ctx.actor.organization_id,
            "general": command.general or current.get("general") or {},
            "security": command.security or current.get("security") or {},
            "notifications": command.notifications or current.get("notifications") or {},
            "integrations": command.integrations or current.get("integrations") or {},
            "updated_by": ctx.actor.id,
            "updated_at": _now().isoformat(),
        }
        if current.get("id"):
            row = self._db.update("organization_settings", current["id"], payload, access_token=ctx.access_token, admin=True)
        else:
            row = self._db.insert("organization_settings", payload, access_token=ctx.access_token, admin=True)
        self._audit(ctx, "update_settings", "organization_settings", row.get("id"), "success")
        return row

    def create_tolerance(self, ctx: AuthContext, command: ToleranceCommand) -> dict[str, Any]:
        ctx.require(Permission.MANAGE_SETTINGS)
        current, _ = self._db.select(
            "tolerance_rules",
            {"organization_id": ctx.actor.organization_id, "rule_key": command.rule_key},
            order="version.desc",
            limit=1,
            access_token=ctx.access_token,
            admin=True,
        )
        version = (current[0]["version"] + 1) if current else 1
        if current:
            self._db.update(
                "tolerance_rules",
                current[0]["id"],
                {"is_active": False, "effective_to": _now().isoformat()},
                admin=True,
            )
        row = self._db.insert(
            "tolerance_rules",
            {
                "organization_id": ctx.actor.organization_id,
                "rule_key": command.rule_key,
                "name": command.name,
                "value": command.value,
                "unit": command.unit,
                "version": version,
                "is_active": True,
                "created_by": ctx.actor.id,
            },
            admin=True,
        )
        self._audit(ctx, "update_tolerance", "tolerance_rule", row["id"], "success", {"version": version})
        return row

    def estimate_quantity(self, ctx: AuthContext, lot_id: str) -> dict[str, Any]:
        ctx.require(Permission.ESTIMATE_ML)
        lot = self.get_row(ctx, "lots", lot_id, Permission.VIEW_LOTS)
        if str(lot.get("organization_id") or "") != str(ctx.actor.organization_id):
            raise ForbiddenError("No tienes permisos para realizar esta acción.")
        receptions, _ = self._db.select(
            "receptions",
            {"lot_id": lot_id},
            limit=1,
            order="occurred_at.desc",
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        observed = float(receptions[0]["received_quantity"]) if receptions else None
        features = {
            "origin_quantity": float(lot["quantity"]),
            "mineral": lot.get("mineral"),
            "unit": lot.get("unit"),
            "observed_quantity": observed,
            "lot_id": lot_id,
            "lot_code": lot.get("code"),
            "mining_operation_id": lot.get("mining_operation_id"),
        }
        result = self._ml.estimate(features)
        expected = float(result["expected_quantity"])
        deviation = self._deviation.percent(expected, observed)
        signal = "review_signal" if deviation is not None and abs(deviation) > 5 else "none"
        models, _ = self._db.select(
            "ml_models",
            {"status": "active"},
            order="registered_at.desc",
            limit=5,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        preferred_version = str(result.get("model_version") or "")
        model = next(
            (m for m in models if str(m.get("version")) == preferred_version and not preferred_version.endswith("-fallback")),
            models[0] if models else {"id": None, "version": preferred_version or "1.0.0"},
        )
        stored_features = dict(result.get("features") or features)
        stored_features["source"] = result.get("source") or stored_features.get("source") or "unknown"
        inference = self._db.insert(
            "ml_inferences",
            {
                "organization_id": ctx.actor.organization_id,
                "lot_id": lot_id,
                "model_id": model.get("id"),
                "model_version": preferred_version or model.get("version") or "1.0.0",
                "expected_quantity": expected,
                "observed_quantity": observed,
                "deviation": (observed - expected) if observed is not None else None,
                "deviation_percent": deviation,
                "signal": signal,
                "features": stored_features,
            },
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        if signal == "review_signal" and deviation is not None:
            self._ensure_alert(
                ctx,
                lot_id,
                "ml_deviation",
                "medium",
                "Señal para revisión (estimación ML)",
                f"Desviación estimada {deviation:.2f}% respecto a la cantidad esperada. No constituye sentencia.",
            )
        return inference

    def search(self, ctx: AuthContext, term: str) -> dict[str, Any]:
        if not allows(ctx.actor.role, Permission.VIEW_LOTS):
            raise ForbiddenError("No tienes permisos para realizar esta acción.")
        lots, _ = self._db.select(
            "lots",
            {"organization_id": ctx.actor.organization_id},
            search=(["code", "qr_payload", "mineral"], term),
            limit=8,
            access_token=ctx.access_token,
            admin=self._admin(),
        )
        return {"lots": lots}

    def evidence_url(self, ctx: AuthContext, evidence_id: str) -> dict[str, str]:
        ctx.require(Permission.VIEW_LOTS)
        evidence = self.get_row(ctx, "evidences", evidence_id, Permission.VIEW_LOTS)
        path = evidence.get("storage_path")
        if not path:
            raise NotFoundError("La evidencia no tiene archivo asociado.")
        return {"url": self._db.signed_url("evidencias", path)}

    def update_profile(self, ctx: AuthContext, command: ProfileCommand) -> dict[str, Any]:
        payload = {"updated_at": _now().isoformat()}
        if command.full_name:
            payload["full_name"] = command.full_name
        return self._db.update("profiles", ctx.actor.id, payload, access_token=ctx.access_token, admin=self._admin())
