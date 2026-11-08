#!/usr/bin/env python3
"""Auditoría hexagonal automatizada — WEB_MINERA (BE + FE + ML).

Uso (desde la raíz del repositorio):
  python architecture-audit/scripts/run_architecture_audit.py

No modifica código de negocio. Consolida Import Linter, Dependency Cruiser,
detección de ciclos (grimp), revisión de acoplamiento y auditoría del servicio ML.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_helpers import (
    build_module_adjacency,
    check_adapters_composition,
    check_presentation_adapters,
    circular_violation,
    coupling_candidate_notes,
    dedupe_violations,
    fallback_depcruise_err,
    find_cycles_dfs,
    ml_adapter_checks,
    ml_arch_ok,
    ml_domain_checks,
    ml_test_checks,
    ml_use_case_checks,
    parse_arrow_violation,
    parse_imports_violation,
    rule_violation,
    update_contract_name,
    write_csv_report,
    write_depcruise_graph,
    write_json_report,
    write_markdown_report,
)

REPO = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO / "architecture-audit"
CONFIGS = AUDIT_ROOT / "configs"
REPORTS = AUDIT_ROOT / "reports"
BACKEND = REPO / "backend"
FRONTEND = REPO / "frontend"
ML = REPO / "ml"

BACKEND_CONTRACTS = CONFIGS / "backend-contracts.ini"
FRONTEND_RULES = CONFIGS / "frontend-rules.cjs"


@dataclass
class Violation:
    component: str
    severity: str  # error | warning | observation
    rule: str
    file: str
    line: int | None
    dependency: str
    message: str
    recommendation: str


@dataclass
class ComponentReport:
    component: str
    files_inspected: list[str] = field(default_factory=list)
    rules_evaluated: list[dict[str, str]] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)
    circular_dependencies: list[list[str]] = field(default_factory=list)
    tool_exit_code: int | None = None
    tool_stdout: str = ""
    result: str = "no_verificable"


@dataclass
class AuditReport:
    project: str = "WEB_MINERA"
    date: str = ""
    commit: str = ""
    branch: str = ""
    components: dict[str, ComponentReport] = field(default_factory=dict)
    ml_audit: dict[str, Any] = field(default_factory=dict)
    coupling_observations: list[Violation] = field(default_factory=list)
    overall_result: str = "no_verificable"
    notes: list[str] = field(default_factory=list)


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=merged,
    )


def _git(args: list[str]) -> str:
    try:
        p = _run(["git", *args], REPO)
        return p.stdout.strip() if p.returncode == 0 else "unknown"
    except OSError:
        return "unknown"


def _list_py(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def _list_ts(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    out: list[Path] = []
    for p in root.rglob("*"):
        if p.suffix in {".ts", ".tsx"} and p.is_file() and "node_modules" not in p.parts:
            out.append(p)
    return sorted(out)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _classify(violations: list[Violation], inspected: bool, tool_ok: bool | None) -> str:
    if not inspected or tool_ok is None:
        return "no_verificable"
    errors = [v for v in violations if v.severity == "error"]
    warnings = [v for v in violations if v.severity == "warning"]
    if not errors and not warnings:
        return "conforme"
    if errors:
        return "no_conforme" if len(errors) >= 3 else "parcialmente_conforme"
    return "parcialmente_conforme"


# ---------------------------------------------------------------------------
# Backend — Import Linter + grimp cycles
# ---------------------------------------------------------------------------

def audit_backend() -> ComponentReport:
    report = ComponentReport(component="backend")
    app_root = BACKEND / "app"
    files = _list_py(app_root)
    report.files_inspected = [_rel(f) for f in files]

    report.rules_evaluated = [
        {"id": "domain-independence", "description": "Dominio sin frameworks ni capas externas"},
        {"id": "application-independence", "description": "Application sin adapters/HTTP/Supabase"},
        {"id": "ports-independence", "description": "Ports sin adapters/infra/frameworks"},
        {"id": "hexagonal-layers", "description": "Dirección de capas hexagonal"},
        {"id": "no-circular-grimp", "description": "Sin ciclos entre módulos app.* (grimp)"},
    ]

    py = BACKEND / ".venv" / "Scripts" / "python.exe"
    if not py.exists():
        py = Path(sys.executable)

    config = BACKEND_CONTRACTS if BACKEND_CONTRACTS.exists() else BACKEND / ".importlinter"
    lint = BACKEND / ".venv" / "Scripts" / "lint-imports.exe"
    if lint.exists():
        proc = _run([str(lint), "--config", str(config)], cwd=BACKEND)
    else:
        proc = _run([str(py), "-m", "importlinter.cli", "--config", str(config)], cwd=BACKEND)

    report.tool_exit_code = proc.returncode
    report.tool_stdout = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")

    report.violations.extend(_parse_import_linter_output(report.tool_stdout))

    # Cycles via grimp (API sin find_cycles en grimp actual → DFS propio)
    try:
        sys.path.insert(0, str(BACKEND))
        import grimp  # type: ignore

        graph = grimp.build_graph("app", include_external_packages=False)
        cycles = _find_import_cycles(graph)
        report.circular_dependencies = cycles
        for cycle in cycles:
            report.violations.append(
                Violation(
                    component="backend",
                    severity="error",
                    rule="no-circular-grimp",
                    file="app",
                    line=None,
                    dependency=" -> ".join(cycle),
                    message=f"Ciclo de dependencias: {' → '.join(cycle)}",
                    recommendation="Romper el ciclo extrayendo un puerto/contrato o moviendo tipos compartidos al dominio.",
                )
            )
    except Exception as exc:  # noqa: BLE001 — evidencia de no verificable
        report.violations.append(
            Violation(
                component="backend",
                severity="warning",
                rule="no-circular-grimp",
                file="app",
                line=None,
                dependency="",
                message=f"No se pudo analizar ciclos con grimp: {exc}",
                recommendation="Instalar import-linter (incluye grimp) en el venv del backend.",
            )
        )
    finally:
        if str(BACKEND) in sys.path:
            sys.path.remove(str(BACKEND))

    tool_ok = report.tool_exit_code in (0, 1)
    report.result = _classify(report.violations, bool(files), tool_ok if report.tool_exit_code is not None else None)
    if report.tool_exit_code not in (0, 1):
        report.result = "no_verificable"
        report.violations.append(
            Violation(
                component="backend",
                severity="warning",
                rule="import-linter-execution",
                file=str(config),
                line=None,
                dependency="",
                message=f"Import Linter no ejecutó correctamente (exit={report.tool_exit_code}). Ver tool_stdout.",
                recommendation="pip install -r architecture-audit/requirements.txt en el venv backend.",
            )
        )
    return report


def _find_import_cycles(graph: Any) -> list[list[str]]:
    """DFS para ciclos entre módulos internos app.*."""
    modules = sorted(m for m in graph.modules if isinstance(m, str) and m.startswith("app."))
    adj = build_module_adjacency(graph, modules)
    return find_cycles_dfs(adj, modules)


def _parse_import_linter_output(text: str) -> list[Violation]:
    """Extrae violaciones del texto de lint-imports (best-effort)."""
    violations: list[Violation] = []
    current_contract = "hexagonal-layers"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        current_contract = update_contract_name(line, current_contract)
        arrow = parse_arrow_violation(line, current_contract, Violation)
        if arrow:
            violations.append(arrow)
            continue
        imports_v = parse_imports_violation(line, current_contract, Violation)
        if imports_v:
            violations.append(imports_v)
    return violations


# ---------------------------------------------------------------------------
# Frontend — Dependency Cruiser
# ---------------------------------------------------------------------------

def audit_frontend() -> ComponentReport:
    report = ComponentReport(component="frontend")
    src = FRONTEND / "src"
    files = _list_ts(src)
    report.files_inspected = [_rel(f) for f in files]
    report.rules_evaluated = [
        {"id": "domain-no-ui-or-outer-layers", "description": "Domain sin React/Next/capas externas"},
        {"id": "application-no-adapters-or-next", "description": "Application sin adapters/Next/React"},
        {"id": "ports-no-adapters", "description": "Ports sin adapters/composition"},
        {"id": "no-direct-database-from-ui", "description": "UI sin acceso directo a BD/SDK"},
        {"id": "presentation-prefer-ports-over-adapters", "description": "Presentation/App no importan adapters"},
        {"id": "no-circular", "description": "Sin dependencias circulares"},
    ]

    config = FRONTEND / ".dependency-cruiser.cjs"
    if not config.exists():
        config = FRONTEND_RULES

    npx = "npx.cmd" if os.name == "nt" else "npx"
    proc_json = _run(
        [npx, "--yes", "depcruise", "--config", str(config), "--output-type", "json", "src"],
        cwd=FRONTEND,
    )
    proc_err = _run(
        [npx, "--yes", "depcruise", "--config", str(config), "--output-type", "err", "src"],
        cwd=FRONTEND,
    )
    report.tool_exit_code = proc_err.returncode
    report.tool_stdout = (proc_err.stdout or "") + (("\n" + proc_err.stderr) if proc_err.stderr else "")

    graph_data = write_depcruise_graph(
        REPORTS / "dependency-graph.json",
        proc_json.stdout or "",
        proc_json.returncode,
        proc_json.stderr or "",
    )
    report.violations.extend(_parse_depcruise_json(graph_data))
    if not report.violations and report.tool_stdout:
        report.violations.extend(fallback_depcruise_err(report.tool_stdout, Violation))

    report.circular_dependencies = [
        v.dependency.split(" -> ")
        for v in report.violations
        if v.rule == "no-circular" and v.dependency
    ]

    tool_ran = (
        bool(graph_data.get("modules"))
        or "dependency violations" in report.tool_stdout
        or "modules" in report.tool_stdout
    )
    if not tool_ran and not report.violations:
        report.result = "no_verificable"
        report.violations.append(
            Violation(
                component="frontend",
                severity="warning",
                rule="dependency-cruiser-execution",
                file=str(config),
                line=None,
                dependency="",
                message=f"depcruise no produjo grafo usable (exit={report.tool_exit_code}).",
                recommendation="cd frontend && npm install --save-dev dependency-cruiser",
            )
        )
    else:
        report.result = _classify(report.violations, bool(files), True)
    return report


def _parse_depcruise_json(data: dict[str, Any]) -> list[Violation]:
    if not data:
        return []
    violations: list[Violation] = []
    for mod in data.get("modules") or []:
        source = mod.get("source") or ""
        for dep in mod.get("dependencies") or []:
            if dep.get("circular"):
                violations.append(circular_violation(source, dep, Violation))
            for rule in dep.get("rules") or []:
                item = rule_violation(source, dep, rule, Violation)
                if item:
                    violations.append(item)
    return dedupe_violations(violations)


# ---------------------------------------------------------------------------
# Coupling / responsibilities (observations, not auto-fail by LOC)
# ---------------------------------------------------------------------------

COUPLING_CANDIDATES = [
    (
        BACKEND / "app" / "application" / "services" / "platform.py",
        "PlatformService concentra muchos casos de uso; riesgo de god-service.",
        "Evaluar split por bounded contexts manteniendo DataGatewayPort.",
    ),
    (
        BACKEND / "app" / "adapters" / "inbound" / "http" / "routers.py",
        "Router HTTP amplio: mezcla superficie API; acoplamiento de presentación inbound.",
        "Partir routers por recurso si crece el churn.",
    ),
    (
        BACKEND / "app" / "adapters" / "outbound" / "supabase" / "client.py",
        "Gateway Supabase monolítico implementa el puerto unificado.",
        "Aceptable como adaptador; vigilar que application no lo importe (ya vetado).",
    ),
    (
        FRONTEND / "src" / "presentation" / "modules" / "resource-page.tsx",
        "ResourcePage mezcla listado, detalle, create y export en un módulo UI.",
        "Observación de cohesión UI; no es violación hexagonal por sí sola.",
    ),
]


def review_coupling() -> list[Violation]:
    dep_file = BACKEND / "app" / "adapters" / "inbound" / "http" / "dependencies.py"
    out: list[Violation] = []
    out.extend(check_adapters_composition(dep_file, _rel, Violation))
    ui_paths = _list_ts(FRONTEND / "src" / "app") + _list_ts(FRONTEND / "src" / "presentation")
    out.extend(check_presentation_adapters(ui_paths, _rel, Violation))
    out.extend(coupling_candidate_notes(COUPLING_CANDIDATES, _rel, Violation))
    return out


# ---------------------------------------------------------------------------
# ML estimation service
# ---------------------------------------------------------------------------

def audit_ml() -> dict[str, Any]:
    result: dict[str, Any] = {
        "component": "ml",
        "architectural_conformance": {},
        "analytical_validation_note": (
            "La conformidad modular NO demuestra precisión ni reproducibilidad analítica "
            "del modelo (MAE/RMSE/R²). El estimador actual es heurístico."
        ),
        "violations": [],
        "checks": [],
    }
    domain_est = ML / "domain" / "services" / "estimator.py"
    use_case = ML / "application" / "use_cases" / "estimate.py"
    composition = ML / "composition" / "__init__.py"
    adapter = ML / "adapters" / "inbound" / "http" / "main.py"
    test = ML / "tests" / "unit" / "test_estimator.py"

    def check(name: str, ok: bool, detail: str) -> None:
        result["checks"].append({"name": name, "ok": ok, "detail": detail})

    check("domain_estimator_exists", domain_est.exists(), _rel(domain_est) if domain_est.exists() else "missing")
    check("application_use_case_exists", use_case.exists(), _rel(use_case) if use_case.exists() else "missing")
    check("composition_wiring_exists", composition.exists(), _rel(composition) if composition.exists() else "missing")
    check("http_adapter_exists", adapter.exists(), _rel(adapter) if adapter.exists() else "missing")
    check("unit_test_exists", test.exists(), _rel(test) if test.exists() else "missing")

    ml_domain_checks(domain_est, _rel, check, result)
    ml_use_case_checks(use_case, check)
    ml_adapter_checks(adapter, check)
    ml_test_checks(test, _rel, check)

    result["architectural_conformance"] = {
        "result": "conforme" if ml_arch_ok(result) else "parcialmente_conforme",
        "note": "Separación modular verificada estáticamente; validación analítica del modelo = fuera de alcance.",
    }
    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _overall(components: dict[str, ComponentReport], coupling: list[Violation]) -> str:
    results = [c.result for c in components.values()]
    err = [v for c in components.values() for v in c.violations if v.severity == "error"]
    err += [v for v in coupling if v.severity == "error"]
    if any(r == "no_verificable" for r in results):
        return "parcialmente_conforme" if err else "no_verificable"
    if not err:
        return "conforme"
    if len(err) <= 5:
        return "parcialmente_conforme"
    return "no_conforme"


def write_reports(audit: AuditReport) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    all_violations: list[Violation] = []
    for comp in audit.components.values():
        all_violations.extend(comp.violations)
    all_violations.extend(audit.coupling_observations)
    write_json_report(REPORTS, audit)
    write_csv_report(REPORTS, all_violations)
    write_markdown_report(REPORTS, audit)


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    audit = AuditReport(
        date=datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
        commit=_git(["rev-parse", "--short", "HEAD"]),
        branch=_git(["rev-parse", "--abbrev-ref", "HEAD"]),
    )

    print("=" * 72)
    print("WEB_MINERA — Auditoría arquitectura hexagonal")
    print("=" * 72)
    print(f"Commit: {audit.commit}  Branch: {audit.branch}")
    print(f"Fecha:  {audit.date}")
    print()

    print("→ Backend (Import Linter + grimp)...")
    be = audit_backend()
    audit.components["backend"] = be
    print(f"  archivos={len(be.files_inspected)} violaciones={len(be.violations)} ciclos={len(be.circular_dependencies)} resultado={be.result}")

    print("→ Frontend (Dependency Cruiser)...")
    fe = audit_frontend()
    audit.components["frontend"] = fe
    print(f"  archivos={len(fe.files_inspected)} violaciones={len(fe.violations)} ciclos={len(fe.circular_dependencies)} resultado={fe.result}")

    print("→ Acoplamiento / responsabilidades...")
    coupling = review_coupling()
    # Merge coupling errors into component buckets for visibility; keep list on audit
    audit.coupling_observations = coupling
    print(f"  items={len(coupling)} (errors={sum(1 for v in coupling if v.severity=='error')})")

    print("→ ML estimation service...")
    audit.ml_audit = audit_ml()
    print(f"  conformidad={audit.ml_audit.get('architectural_conformance', {}).get('result')}")

    audit.notes.append(
        "Hallazgos reales no se excluyen para forzar 'conforme'. "
        "Observaciones de tamaño/cohesión no son defectos automáticos."
    )
    audit.overall_result = _overall(audit.components, coupling)

    write_reports(audit)

    print()
    print("=" * 72)
    print(f"RESULTADO GLOBAL: {audit.overall_result}")
    print(f"Reportes: {REPORTS}")
    print("  - architecture-report.md")
    print("  - architecture-report.json")
    print("  - violations.csv")
    print("  - dependency-graph.json")
    print("=" * 72)

    # Exit 0 always for report generation success; architectural non-conformance reflected in report
    # Use exit 1 only if tools could not run at all
    if all(c.result == "no_verificable" for c in audit.components.values()):
        return 2
    return 0 if audit.overall_result in {"conforme", "parcialmente_conforme"} else 1


if __name__ == "__main__":
    sys.exit(main())
