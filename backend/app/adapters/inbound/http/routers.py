from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import PlainTextResponse

from app.adapters.inbound.http.dependencies import get_context, get_platform
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
from app.application.services.platform import PlatformService
from app.domain.value_objects import Permission
from app.infrastructure.security.auth_context import AuthContext

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
api_router = APIRouter(prefix="/api/v1", tags=["api"])


def _set_session(response: Response, tokens: dict) -> None:
    if tokens.get("access_token"):
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            httponly=True,
            samesite="lax",
            max_age=tokens.get("expires_in") or 3600,
        )
    if tokens.get("refresh_token"):
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"],
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 14,
        )


@auth_router.post("/login")
def login(command: LoginCommand, response: Response, platform: PlatformService = Depends(get_platform)):
    result = platform.authenticate(command)
    _set_session(response, result)
    return result


@auth_router.post("/logout")
def logout(
    response: Response,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    platform.logout(ctx.access_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
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
def activate(command: ActivateCommand, platform: PlatformService = Depends(get_platform)):
    return platform.activate_account(command)


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
    platform: PlatformService = Depends(get_platform),
):
    return platform.register_lot(ctx, command)


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
    return platform.list_table(ctx, "transports", Permission.VIEW_TRANSPORT, query, ["vehicle", "plate", "driver", "code"])


@api_router.get("/transport/{record_id}")
def transport_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_row(ctx, "transports", record_id, Permission.VIEW_TRANSPORT)


@api_router.post("/transport")
def create_transport(command: TransportCommand, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.register_transport(ctx, command)


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
    return platform.list_table(ctx, "mass_balances", Permission.VIEW_BALANCE, query, ["status"])


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
    return platform.get_row(ctx, "alerts", record_id, Permission.VIEW_ALERTS)


@api_router.post("/alerts/{record_id}/review")
def review_alert(
    record_id: str,
    command: AlertReviewCommand,
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
):
    return platform.review_alert(ctx, record_id, command)


@api_router.get("/audits")
def audits(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(ctx, "audit_log", Permission.VIEW_AUDIT, query, ["action", "entity", "result"])


@api_router.get("/audits/cases/{lot_id}")
def audit_case(lot_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.audit_case(ctx, lot_id)


@api_router.get("/ml/models")
def ml_models(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(ctx, "ml_models", Permission.VIEW_ML, query, ["name", "version"])


@api_router.get("/ml/inferences")
def ml_inferences(
    ctx: AuthContext = Depends(get_context),
    platform: PlatformService = Depends(get_platform),
    query: PageQuery = Depends(_query),
):
    return platform.list_table(ctx, "ml_inferences", Permission.VIEW_ML, query, ["model_version", "signal"])


@api_router.get("/ml/inferences/{record_id}")
def ml_inference_detail(record_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.get_row(ctx, "ml_inferences", record_id, Permission.VIEW_ML)


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


@api_router.post("/users/invite")
def invite(command: InviteCommand, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.invite_user(ctx, command)


@api_router.post("/users/{user_id}/resend-invite")
def resend(user_id: str, ctx: AuthContext = Depends(get_context), platform: PlatformService = Depends(get_platform)):
    return platform.resend_invite(ctx, user_id)


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
