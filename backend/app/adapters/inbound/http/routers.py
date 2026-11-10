from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import PlainTextResponse

from app.adapters.inbound.http.dependencies import (
    get_activate_account,
    get_authenticate,
    get_context,
    get_invite_user,
    get_platform,
    get_register_lot,
    get_review_alert,
)
from app.application.auth_context import AuthContext
from app.application.dto import (
    ActivateCommand,
    AlertReviewCommand,
    CustodyCommand,
    InviteCommand,
    LoginCommand,
    MlModelStatusCommand,
    PageQuery,
    ProfileCommand,
    ReceptionCommand,
    RegisterLotCommand,
    SettingsCommand,
    ToleranceCommand,
    TransportCommand,
    TransportEventCommand,
    UpdateUserRoleCommand,
    WeighingCommand,
)
from app.application.services.platform import PlatformService
from app.application.use_cases import (
    ActivateAccountUseCase,
    AuthenticateUseCase,
    InviteUserUseCase,
    RegisterLotUseCase,
    ReviewAlertUseCase,
)
from app.domain.value_objects import Permission

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
api_router = APIRouter(prefix="/api/v1", tags=["api"])


def _cookie_secure() -> bool:
    """Secure cookies en producción (HTTPS). En local HTTP se omiten para no romper login."""
    from app.infrastructure.configuration.settings import get_settings

    return get_settings().is_production


def _set_session(response: Response, tokens: dict) -> None:
    secure = _cookie_secure()
    if tokens.get("access_token"):
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            httponly=True,
            secure=secure,
            samesite="lax",
            max_age=tokens.get("expires_in") or 3600,
        )
    if tokens.get("refresh_token"):
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"],
            httponly=True,
            secure=secure,
            samesite="lax",
            max_age=60 * 60 * 24 * 14,
        )


@auth_router.post("/login")
def login(
    command: LoginCommand,
    response: Response,
    authenticate: AuthenticateUseCase = Depends(get_authenticate),
):
    result = authenticate.execute(command)
    _set_session(response, result)
    return result


@auth_router.post("/logout")
def logout(
    response: Response,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    platform.logout(ctx.access_token)
    secure = _cookie_secure()
    response.delete_cookie("access_token", secure=secure, samesite="lax")
    response.delete_cookie("refresh_token", secure=secure, samesite="lax")
    return {"ok": True}


@auth_router.post("/forgot-password")
def forgot_password(payload: dict, platform: PlatformService = Depends(get_platform)):
    return platform.forgot_password(payload.get("email", ""))


@auth_router.post("/refresh")
def refresh(payload: dict, response: Response, platform: PlatformService = Depends(get_platform)):
    result = platform.refresh(payload.get("refresh_token", ""))
    _set_session(response, result)
    return result


@auth_router.get("/me")
def me(ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.serialize_actor(ctx.actor)


@auth_router.get("/activate")
def validate_activation(token: str, platform: PlatformService = Depends(get_platform)):
    return platform.validate_invitation(token)


@auth_router.post("/activate")
def activate(
    command: ActivateCommand,
    activate_account: ActivateAccountUseCase = Depends(get_activate_account),
):
    return activate_account.execute(command)


@api_router.get("/dashboard")
def dashboard(ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.dashboard(ctx)


def _query(
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    sort: str = "created_at",
    order: str = "desc",
    status: str | None = None,
) -> PageQuery:
    return PageQuery(page=page, page_size=page_size, q=q, sort=sort, order=order, status=status)


@api_router.get("/lots")
def lots(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_lots(ctx, query)


@api_router.get("/lots/export")
def export_lots(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return PlainTextResponse(platform.export_lots(ctx, query), media_type="text/csv")


@api_router.get("/lots/{lot_id}")
def lot_detail(lot_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_lot(ctx, lot_id)


@api_router.get("/lots/{lot_id}/timeline")
def lot_timeline(lot_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.lot_timeline(ctx, lot_id)


@api_router.post("/lots")
def create_lot(
    command: RegisterLotCommand,
    ctx: AuthContext = Depends(get_context),
    register_lot: RegisterLotUseCase = Depends(get_register_lot),
):
    return register_lot.execute(ctx, command)


@api_router.get("/custody")
def custody(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(ctx, "custody_transfers", Permission.VIEW_CUSTODY, query, ["origin", "destination"])


@api_router.get("/custody/{record_id}")
def custody_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_row(ctx, "custody_transfers", record_id, Permission.VIEW_CUSTODY)


@api_router.post("/custody")
def create_custody(command: CustodyCommand, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.start_custody(ctx, command)


@api_router.get("/transport")
def transports(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_transports(ctx, query)


@api_router.get("/transport/carriers")
def transport_carriers(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.list_carriers(ctx)


@api_router.get("/transport/{record_id}")
def transport_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_row(ctx, "transports", record_id, Permission.VIEW_TRANSPORT)


@api_router.post("/transport")
def create_transport(command: TransportCommand, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.register_transport(ctx, command)


@api_router.get("/transport/{record_id}/events")
def transport_events(
    record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)
):
    return platform.list_transport_events(ctx, record_id)


@api_router.post("/transport/{record_id}/events")
def create_transport_event(
    record_id: str,
    command: TransportEventCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.register_transport_event(ctx, record_id, command)


@api_router.get("/receptions")
def receptions(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(ctx, "receptions", Permission.VIEW_RECEPTIONS, query, ["responsible", "status"])


@api_router.get("/receptions/{record_id}")
def reception_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_row(ctx, "receptions", record_id, Permission.VIEW_RECEPTIONS)


@api_router.post("/receptions")
def create_reception(command: ReceptionCommand, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.register_reception(ctx, command)


@api_router.get("/weighings")
def weighings(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(ctx, "weighings", Permission.VIEW_RECEPTIONS, query, ["responsible", "instrument"])


@api_router.get("/weighings/{record_id}")
def weighing_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_row(ctx, "weighings", record_id, Permission.VIEW_RECEPTIONS)


@api_router.post("/weighings")
def create_weighing(command: WeighingCommand, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.register_weighing(ctx, command)


@api_router.get("/mass-balance")
def mass_balance(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    # Calculado en vivo desde lots + receptions (sin tabla mass_balances).
    return platform.list_balances(ctx, query)


@api_router.get("/mass-balance/{lot_id}")
def mass_balance_detail(
    lot_id: str,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.get_balance(ctx, lot_id)


@api_router.post("/mass-balance/{lot_id}/recalculate")
def recalculate(lot_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.recalculate_balance(ctx, lot_id)


@api_router.get("/alerts")
def alerts(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(
        ctx,
        "alerts",
        Permission.VIEW_ALERTS,
        query,
        ["title", "alert_type", "reason"],
        {"organization_id": ctx.actor.organization_id},
    )


@api_router.get("/alerts/{record_id}")
def alert_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_alert(ctx, record_id)


@api_router.post("/alerts/{record_id}/review")
def review_alert(
    record_id: str,
    command: AlertReviewCommand,
    ctx: AuthContext = Depends(get_context),
    review: ReviewAlertUseCase = Depends(get_review_alert),
):
    return review.execute(ctx, record_id, command)


@api_router.post("/alerts/{record_id}/close")
def close_alert_review(
    record_id: str,
    command: AlertReviewCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.close_alert_review(ctx, record_id, command)


@api_router.get("/audits")
def audits(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_audits(ctx, query)


@api_router.get("/audits/cases/{lot_id}/export")
def export_audit_case(lot_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    csv_body = platform.export_case(ctx, lot_id)
    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="expediente-{lot_id}.csv"'},
    )


@api_router.get("/audits/cases/{lot_id}")
def audit_case(lot_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.audit_case(ctx, lot_id)


@api_router.get("/audits/{record_id}")
def audit_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_audit_event(ctx, record_id)


@api_router.get("/ml/status")
def ml_status(ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    """Diagnóstico: conectividad al servicio ML y disponibilidad de tablas."""
    from app.infrastructure.configuration.settings import get_settings
    import httpx

    settings = get_settings()
    ml_url = (settings.ml_service_url or "").rstrip("/")
    service = {"configured": bool(ml_url), "url": ml_url or None, "reachable": False, "health": None}
    if ml_url:
        try:
            resp = httpx.get(f"{ml_url}/health", timeout=5.0)
            service["reachable"] = resp.status_code == 200
            service["health"] = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"status_code": resp.status_code}
        except Exception as exc:  # noqa: BLE001
            service["health"] = {"error": str(exc)}
    tables: dict[str, str] = {}
    for table in ("ml_models", "ml_inferences"):
        try:
            platform._db.select(  # noqa: SLF001 — diagnóstico operativo
                table,
                {"organization_id": ctx.actor.organization_id} if table != "ml_models" else None,
                limit=1,
                access_token=ctx.access_token,
                admin=platform._admin(),  # noqa: SLF001
            )
            tables[table] = "ok"
        except Exception as exc:  # noqa: BLE001
            tables[table] = str(getattr(exc, "message", exc))
    tables["mass_balance"] = "computed_from_lots_and_receptions"
    return {"service": service, "tables": tables}


@api_router.get("/ml/models")
def ml_models(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(ctx, "ml_models", Permission.VIEW_ML, query, ["name", "version"])


@api_router.post("/ml/models/{model_id}/status")
def ml_model_status(
    model_id: str,
    command: MlModelStatusCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.set_ml_model_status(ctx, model_id, command.status)


@api_router.get("/ml/inferences")
def ml_inferences(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    filters: dict = {"organization_id": ctx.actor.organization_id}
    if query.status in {"none", "review_signal"}:
        filters["signal"] = query.status
    # ml_inferences no tiene columna status; mapear filtro a signal.
    query_safe = query.model_copy(update={"status": None})
    return platform.list_table(
        ctx,
        "ml_inferences",
        Permission.VIEW_ML,
        query_safe,
        ["model_version", "signal"],
        filters,
    )


@api_router.get("/ml/inferences/{record_id}")
def ml_inference_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    row = platform.get_row(ctx, "ml_inferences", record_id, Permission.VIEW_ML)
    if str(row.get("organization_id") or "") != str(ctx.actor.organization_id):
        from app.application.messages import MSG_FORBIDDEN
        from app.domain.exceptions import ForbiddenError

        raise ForbiddenError(MSG_FORBIDDEN)
    return row


@api_router.post("/ml/estimate/{lot_id}")
def estimate(lot_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.estimate_quantity(ctx, lot_id)


@api_router.get("/users")
def users(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_users(ctx, query)


@api_router.get("/users/{user_id}")
def user_detail(user_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_row(ctx, "profiles", user_id, Permission.MANAGE_USERS)


@api_router.post("/users/invite")
def invite(
    command: InviteCommand,
    ctx: AuthContext = Depends(get_context),
    invite_user: InviteUserUseCase = Depends(get_invite_user),
):
    return invite_user.execute(ctx, command)


@api_router.post("/users/{user_id}/resend-invite")
def resend(user_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.resend_invite(ctx, user_id)


@api_router.post("/users/{user_id}/role")
def update_user_role(
    user_id: str,
    command: UpdateUserRoleCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.update_user_role(ctx, user_id, command.role)


@api_router.post("/users/{user_id}/deactivate")
def deactivate(user_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.set_user_status(ctx, user_id, False)


@api_router.post("/users/{user_id}/activate")
def activate_user(user_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.set_user_status(ctx, user_id, True)


@api_router.get("/notifications")
def notifications(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.notifications(ctx, query)


@api_router.post("/notifications/{notification_id}/read")
def read_notification(
    notification_id: str,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.read_notification(ctx, notification_id)


@api_router.get("/settings")
def settings(ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.settings(ctx)


@api_router.put("/settings")
def update_settings(
    command: SettingsCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.update_settings(ctx, command)


@api_router.post("/settings/tolerances")
def create_tolerance(
    command: ToleranceCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.create_tolerance(ctx, command)


@api_router.get("/search")
def search(q: str = Query(default=""), ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.search(ctx, q)


@api_router.get("/evidences/{evidence_id}/url")
def evidence_url(evidence_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.evidence_url(ctx, evidence_id)


@api_router.patch("/profile")
def update_profile(
    command: ProfileCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.update_profile(ctx, command)
