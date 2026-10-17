"""Pruebas de conformidad hexagonal: orientación de dependencias."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND_APP = Path(__file__).resolve().parents[2] / "app"

FORBIDDEN_IN_DOMAIN = (
    "fastapi",
    "uvicorn",
    "httpx",
    "supabase",
    "sqlalchemy",
    "starlette",
    "pydantic",
    "app.adapters",
    "app.infrastructure",
    "app.composition",
)

FORBIDDEN_IN_APPLICATION = (
    "fastapi",
    "uvicorn",
    "httpx",
    "supabase",
    "app.adapters",
    "app.composition",
)

FORBIDDEN_IN_PORTS = (
    "fastapi",
    "httpx",
    "supabase",
    "app.adapters",
    "app.composition",
    "app.infrastructure",
)


def _imports_in(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
    return found


def _python_files(relative: str) -> list[Path]:
    root = BACKEND_APP / relative
    return sorted(root.rglob("*.py"))


def _assert_no_forbidden(files: list[Path], forbidden: tuple[str, ...], layer: str) -> None:
    violations: list[str] = []
    for file in files:
        if file.name == "__init__.py" and file.read_text(encoding="utf-8").strip() == "":
            continue
        for imported in _imports_in(file):
            for banned in forbidden:
                if imported == banned or imported.startswith(f"{banned}."):
                    violations.append(f"{file.relative_to(BACKEND_APP)} imports {imported}")
    assert not violations, f"Violaciones en {layer}:\n" + "\n".join(violations)


def test_domain_has_no_framework_or_adapter_imports() -> None:
    _assert_no_forbidden(_python_files("domain"), FORBIDDEN_IN_DOMAIN, "domain")


def test_application_has_no_adapter_or_framework_imports() -> None:
    # AuthContext vive en application; platform no debe importar adapters.
    files = [f for f in _python_files("application") if "auth_context" not in f.name or True]
    _assert_no_forbidden(files, FORBIDDEN_IN_APPLICATION, "application")


def test_ports_have_no_adapter_or_framework_imports() -> None:
    _assert_no_forbidden(_python_files("ports"), FORBIDDEN_IN_PORTS, "ports")


def test_supabase_gateway_lives_only_in_outbound_adapters() -> None:
    offenders: list[str] = []
    for file in BACKEND_APP.rglob("*.py"):
        relative = file.relative_to(BACKEND_APP)
        parts = relative.parts
        if parts[:3] == ("adapters", "outbound", "supabase"):
            continue
        if parts[:1] == ("composition",):
            # composition root puede ensamblar el adaptador
            continue
        text = file.read_text(encoding="utf-8")
        if "SupabaseGateway" in text or "from app.adapters.outbound.supabase" in text:
            offenders.append(str(relative))
    assert not offenders, "SupabaseGateway filtrado fuera de adapters/outbound y composition:\n" + "\n".join(
        offenders
    )


def test_platform_service_depends_on_gateway_port() -> None:
    source = (BACKEND_APP / "application" / "services" / "platform.py").read_text(encoding="utf-8")
    assert "DataGatewayPort" in source
    assert "AppConfigPort" in source
    assert "SupabaseGateway" not in source
    assert "from app.adapters" not in source
