"""Pruebas de validación de reglas: caso que cumple + caso que incumple.

No modifican el código de negocio de WEB_MINERA; operan sobre fixtures.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

FIX = Path(__file__).resolve().parent / "fixtures"


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
    return found


FORBIDDEN_DOMAIN = ("fastapi", "uvicorn", "httpx", "supabase", "sqlalchemy", "pydantic")


def test_backend_rule_respected_by_clean_fixture() -> None:
    domain = FIX / "py_ok" / "pkg" / "domain" / "__init__.py"
    imports = _imports(domain)
    hits = [i for i in imports if i.split(".")[0] in FORBIDDEN_DOMAIN]
    assert hits == [], f"Fixture limpia no debe violar: {hits}"


def test_backend_rule_broken_by_contaminated_fixture() -> None:
    domain = FIX / "py_bad" / "pkg" / "domain" / "__init__.py"
    imports = _imports(domain)
    assert any(i.split(".")[0] == "fastapi" for i in imports), "Fixture mala debe importar fastapi"


def test_frontend_rule_respected_by_clean_fixture() -> None:
    src = (FIX / "ts_ok" / "src" / "domain" / "types.ts").read_text(encoding="utf-8")
    imports = re.findall(r"""from\s+["']([^"']+)["']""", src)
    assert not any(i == "react" or i.startswith("react/") or i.startswith("next") for i in imports)


def test_frontend_rule_broken_by_contaminated_fixture() -> None:
    src = (FIX / "ts_bad" / "src" / "domain" / "types.ts").read_text(encoding="utf-8")
    imports = re.findall(r"""from\s+["']([^"']+)["']""", src)
    assert "react" in imports


def test_real_backend_domain_respects_forbidden_list() -> None:
    """Sanity sobre el dominio real (debe cumplir; si falla, es hallazgo real)."""
    repo = Path(__file__).resolve().parents[2]
    domain_root = repo / "backend" / "app" / "domain"
    violations: list[str] = []
    for path in domain_root.rglob("*.py"):
        for imp in _imports(path):
            root = imp.split(".")[0]
            if root in FORBIDDEN_DOMAIN or imp.startswith("app.adapters") or imp.startswith("app.composition"):
                violations.append(f"{path.name}:{imp}")
    assert violations == []


def test_contracts_and_frontend_rules_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "configs" / "backend-contracts.ini").is_file()
    assert (root / "configs" / "frontend-rules.cjs").is_file()
    assert (root / "scripts" / "run_architecture_audit.py").is_file()
