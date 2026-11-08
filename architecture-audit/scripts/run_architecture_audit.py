#!/usr/bin/env python3
"""Auditoría hexagonal automatizada — WEB_MINERA (BE + FE + ML).

Uso (desde la raíz del repositorio):
  python architecture-audit/scripts/run_architecture_audit.py

No modifica código de negocio. Consolida Import Linter, Dependency Cruiser,
detección de ciclos (grimp), revisión de acoplamiento y auditoría del servicio ML.
"""

from __future__ import annotations

import ast
import csv
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    adj: dict[str, list[str]] = {}
    for mod in modules:
        try:
            deps = graph.find_modules_directly_imported_by(mod)
        except Exception:  # noqa: BLE001
            deps = []
        adj[mod] = sorted(d for d in deps if d in modules)

    cycles: list[list[str]] = []
    seen_cycle_keys: set[tuple[str, ...]] = set()
    color: dict[str, int] = {m: 0 for m in modules}  # 0=white 1=gray 2=black
    stack: list[str] = []

    def dfs(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for nxt in adj.get(node, []):
            if color[nxt] == 1:
                i = stack.index(nxt)
                cycle = stack[i:] + [nxt]
                key = tuple(sorted(set(cycle)))
                if key not in seen_cycle_keys:
                    seen_cycle_keys.add(key)
                    cycles.append(cycle)
            elif color[nxt] == 0:
                dfs(nxt)
        stack.pop()
        color[node] = 2

    for m in modules:
        if color[m] == 0:
            dfs(m)
    return cycles


def _parse_import_linter_output(text: str) -> list[Violation]:
    """Extrae violaciones del texto de lint-imports (best-effort)."""
    violations: list[Violation] = []
    current_contract = "hexagonal-layers"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if "independence" in line.lower() or "layer direction" in line.lower():
            if "KEPT" not in line and "BROKEN" not in line and "Contracts" not in line:
                current_contract = line[:120]

        # Formato: - app.foo.bar -> app.baz.qux (l.17)
        m = re.search(
            r"-\s+(?P<source>app\.[\w\.]+)\s+->\s+(?P<dep>app\.[\w\.]+|[\w\.]+)\s*(?:\(l\.(?P<line>\d+)\))?",
            line,
        )
        if m:
            source = m.group("source")
            dep = m.group("dep")
            line_no = int(m.group("line")) if m.group("line") else None
            file_guess = "backend/" + source.replace(".", "/") + ".py"
            violations.append(
                Violation(
                    component="backend",
                    severity="error",
                    rule=current_contract if current_contract else "import-linter",
                    file=file_guess,
                    line=line_no,
                    dependency=dep,
                    message=line.lstrip("- ").strip(),
                    recommendation=_backend_recommendation(current_contract, dep),
                )
            )
            continue

        m2 = re.search(
            r"(?P<source>app\.[\w\.]+)\s+imports\s+(?P<dep>[\w\.]+)",
            line,
            re.I,
        )
        if m2:
            source = m2.group("source")
            dep = m2.group("dep")
            violations.append(
                Violation(
                    component="backend",
                    severity="error",
                    rule=current_contract,
                    file=f"backend/{source.replace('.', '/')}.py",
                    line=None,
                    dependency=dep,
                    message=line,
                    recommendation=_backend_recommendation(current_contract, dep),
                )
            )
    return violations


def _backend_recommendation(rule: str, dep: str) -> str:
    dep_l = dep.lower()
    if "composition" in dep_l:
        return "Inyectar el contenedor desde el composition root (p. ej. app.state) sin que adapters importen app.composition."
    if any(x in dep_l for x in ("fastapi", "starlette", "uvicorn", "httpx", "supabase", "sqlalchemy", "pydantic")):
        return "Mover el import a adapters/infrastructure o expresar la necesidad vía un puerto."
    if "adapters" in dep_l:
        return "Depender del puerto (Protocol) e inyectar el adaptador en composition."
    return f"Reorientar la dependencia para respetar el contrato '{rule}'."


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
    # JSON output for machine parsing + text for evidence
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

    graph_path = REPORTS / "dependency-graph.json"
    graph_data: dict[str, Any] = {}
    raw_json = (proc_json.stdout or "").strip()
    # depcruise devuelve exit != 0 cuando hay violaciones; eso es ejecución válida.
    if raw_json.startswith("{"):
        try:
            graph_data = json.loads(raw_json)
            graph_path.write_text(json.dumps(graph_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except json.JSONDecodeError:
            graph_path.write_text(raw_json, encoding="utf-8")
    else:
        graph_path.write_text(
            json.dumps(
                {
                    "error": "dependency-cruiser json unavailable",
                    "exit": proc_json.returncode,
                    "stderr": proc_json.stderr,
                    "stdout_head": raw_json[:2000],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    report.violations.extend(_parse_depcruise_json(graph_data))
    # También parsear salida err si el JSON no trajo rules (fallback)
    if not report.violations and report.tool_stdout:
        for m in re.finditer(
            r"error\s+(?P<rule>[\w-]+):\s+(?P<src>\S+)\s+→\s+(?P<dst>\S+)",
            report.tool_stdout,
        ):
            report.violations.append(
                Violation(
                    component="frontend",
                    severity="error",
                    rule=m.group("rule"),
                    file=f"frontend/{m.group('src')}",
                    line=None,
                    dependency=m.group("dst"),
                    message=f"{m.group('src')} → {m.group('dst')} incumple {m.group('rule')}",
                    recommendation=_frontend_recommendation(m.group("rule")),
                )
            )

    report.circular_dependencies = [
        v.dependency.split(" -> ")
        for v in report.violations
        if v.rule == "no-circular" and v.dependency
    ]

    tool_ran = bool(graph_data.get("modules")) or "dependency violations" in report.tool_stdout or "modules" in report.tool_stdout
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
    violations: list[Violation] = []
    if not data:
        return violations
    modules = data.get("modules") or []
    for mod in modules:
        source = mod.get("source") or ""
        for dep in mod.get("dependencies") or []:
            rules = dep.get("rules") or []
            # Also circular flag
            if dep.get("circular"):
                cycle = dep.get("cycle") or []
                violations.append(
                    Violation(
                        component="frontend",
                        severity="error",
                        rule="no-circular",
                        file=f"frontend/{source}",
                        line=None,
                        dependency=" -> ".join(cycle) if cycle else (dep.get("resolved") or ""),
                        message=f"Dependencia circular desde {source}",
                        recommendation="Extraer contrato compartido o invertir la dependencia vía ports/composition.",
                    )
                )
            for rule in rules:
                name = rule.get("name") or "unknown"
                severity = rule.get("severity") or "error"
                if severity == "ignore":
                    continue
                to_mod = dep.get("module") or dep.get("resolved") or ""
                violations.append(
                    Violation(
                        component="frontend",
                        severity="error" if severity == "error" else "warning",
                        rule=name,
                        file=f"frontend/{source}",
                        line=None,
                        dependency=str(to_mod),
                        message=f"{source} → {to_mod} incumple {name}",
                        recommendation=_frontend_recommendation(name),
                    )
                )
    # Deduplicate
    seen: set[tuple[str, str, str]] = set()
    unique: list[Violation] = []
    for v in violations:
        key = (v.rule, v.file, v.dependency)
        if key in seen:
            continue
        seen.add(key)
        unique.append(v)
    return unique


def _frontend_recommendation(rule: str) -> str:
    mapping = {
        "domain-no-ui-or-outer-layers": "Mantener domain como tipos/reglas puras; mover UI a presentation.",
        "domain-no-node-modules-ui": "Eliminar import de React/Next del dominio.",
        "application-no-adapters-or-next": "Inyectar PlatformPort; cablear adaptador solo en composition.",
        "ports-no-adapters": "El puerto solo declara contratos TypeScript.",
        "no-direct-database-from-ui": "Toda persistencia debe pasar por API/adaptadores outbound.",
        "presentation-prefer-ports-over-adapters": "Importar desde @/composition o hooks que usen PlatformPort; no desde @/adapters/....",
        "no-circular": "Romper el ciclo con un puerto o módulo neutro de tipos.",
    }
    return mapping.get(rule, "Ajustar imports para respetar la dirección hexagonal.")


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
    out: list[Violation] = []
    # Concrete known architectural smell with evidence (adapters → composition)
    dep_file = BACKEND / "app" / "adapters" / "inbound" / "http" / "dependencies.py"
    if dep_file.exists():
        text = dep_file.read_text(encoding="utf-8")
        if "app.composition" in text or "from app.composition" in text:
            line_no = None
            for i, ln in enumerate(text.splitlines(), 1):
                if "composition" in ln and "import" in ln:
                    line_no = i
                    break
            out.append(
                Violation(
                    component="backend",
                    severity="error",
                    rule="adapters-must-not-import-composition",
                    file=_rel(dep_file),
                    line=line_no,
                    dependency="app.composition.container",
                    message="El adaptador inbound HTTP importa el composition root (Container).",
                    recommendation="Leer container solo desde request.app.state inyectado en composition; tipar Depends con Protocol/callable sin importar Container.",
                )
            )

    # Presentation → adapters (complement AST if depcruise missed)
    for path in _list_ts(FRONTEND / "src" / "app") + _list_ts(FRONTEND / "src" / "presentation"):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"""from\s+["'](@/adapters/[^"']+)["']""", text):
            line_no = text[: m.start()].count("\n") + 1
            out.append(
                Violation(
                    component="frontend",
                    severity="error",
                    rule="presentation-prefer-ports-over-adapters",
                    file=_rel(path),
                    line=line_no,
                    dependency=m.group(1),
                    message=f"UI importa adaptador concreto {m.group(1)}",
                    recommendation="Usar @/composition o un hook sobre PlatformPort; tipar errores vía dominio/ports.",
                )
            )

    for path, justification, reco in COUPLING_CANDIDATES:
        if not path.exists():
            continue
        nlines = len(path.read_text(encoding="utf-8").splitlines())
        out.append(
            Violation(
                component="backend" if "backend" in str(path) else "frontend",
                severity="observation",
                rule="responsibility-concentration",
                file=_rel(path),
                line=None,
                dependency="",
                message=f"{justification} (tamaño actual: {nlines} líneas; el tamaño solo contextualiza, no define defecto).",
                recommendation=reco,
            )
        )

    # Mix of persistence + domain in same module? Spot-check supabase client
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

    # Domain independence from ML frameworks / FastAPI
    forbidden = ("fastapi", "uvicorn", "sklearn", "torch", "tensorflow", "numpy", "pandas", "pydantic")
    if domain_est.exists():
        tree = ast.parse(domain_est.read_text(encoding="utf-8"))
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        bad = [i for i in imports if i.split(".")[0] in forbidden]
        check("domain_free_of_ml_frameworks", not bad, f"imports={imports}; forbidden_hits={bad}")
        if bad:
            result["violations"].append(
                {
                    "rule": "ml-domain-no-framework",
                    "file": _rel(domain_est),
                    "dependency": ",".join(bad),
                    "message": "Dominio ML importa framework prohibido",
                }
            )
        src = domain_est.read_text(encoding="utf-8")
        has_version = "version" in src and "1.0.0" in src
        check("model_version_identified", has_version, "ExpectedQuantityEstimator.version == '1.0.0'")

    # I/O contracts (dict features in / dict out) — lightweight
    if use_case.exists():
        uc = use_case.read_text(encoding="utf-8")
        check(
            "input_output_contract",
            "dict[str, Any]" in uc and "execute" in uc,
            "EstimateExpectedQuantity.execute(features: dict) -> dict",
        )
        check(
            "use_case_depends_on_domain_not_fastapi",
            "fastapi" not in uc and "ExpectedQuantityEstimator" in uc,
            "use case importa estimador de dominio",
        )

    if adapter.exists():
        ad = adapter.read_text(encoding="utf-8")
        check("adapter_uses_composition", "estimate_use_case" in ad or "composition" in ad, "HTTP adapter cablea composition")
        check("adapter_has_pydantic_request_model", "BaseModel" in ad, "EstimateRequest como contrato de borde HTTP")

    if test.exists():
        t = test.read_text(encoding="utf-8")
        check("reproducible_unit_test", "expected_quantity" in t and "model_version" in t, _rel(test))
        check("test_input_fixture", "origin_quantity" in t, "features de prueba en test_estimator.py")

    # Separation score
    arch_ok = all(
        c["ok"]
        for c in result["checks"]
        if c["name"]
        in {
            "domain_estimator_exists",
            "application_use_case_exists",
            "composition_wiring_exists",
            "domain_free_of_ml_frameworks",
            "model_version_identified",
            "input_output_contract",
            "use_case_depends_on_domain_not_fastapi",
            "reproducible_unit_test",
        }
    )
    result["architectural_conformance"] = {
        "result": "conforme" if arch_ok and not result["violations"] else "parcialmente_conforme",
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
        if err:
            return "parcialmente_conforme"
        return "no_verificable"
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

    # JSON
    payload = {
        "project": audit.project,
        "date": audit.date,
        "commit": audit.commit,
        "branch": audit.branch,
        "overall_result": audit.overall_result,
        "notes": audit.notes,
        "components": {
            name: {
                "component": c.component,
                "files_inspected_count": len(c.files_inspected),
                "files_inspected": c.files_inspected,
                "rules_evaluated": c.rules_evaluated,
                "violations_count": len([v for v in c.violations if v.severity != "observation"]),
                "violations": [asdict(v) for v in c.violations],
                "circular_dependencies": c.circular_dependencies,
                "tool_exit_code": c.tool_exit_code,
                "result": c.result,
            }
            for name, c in audit.components.items()
        },
        "coupling_observations": [asdict(v) for v in audit.coupling_observations],
        "ml_audit": audit.ml_audit,
    }
    (REPORTS / "architecture-report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # CSV
    with (REPORTS / "violations.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "component",
                "severity",
                "rule",
                "file",
                "line",
                "dependency",
                "message",
                "recommendation",
            ],
        )
        writer.writeheader()
        for v in all_violations:
            writer.writerow(asdict(v))

    # Markdown
    lines: list[str] = [
        "# Architecture Audit Report — WEB_MINERA",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| Proyecto | {audit.project} |",
        f"| Fecha | {audit.date} |",
        f"| Commit | `{audit.commit}` |",
        f"| Rama | `{audit.branch}` |",
        f"| Resultado global | **{audit.overall_result}** |",
        "",
        "> La ausencia de violaciones detectadas por las reglas configuradas **no** es garantía absoluta de cumplimiento arquitectónico total.",
        "",
    ]

    for name, c in audit.components.items():
        lines += [
            f"## Componente: {name}",
            "",
            f"- Archivos inspeccionados: **{len(c.files_inspected)}**",
            f"- Reglas evaluadas: **{len(c.rules_evaluated)}**",
            f"- Violaciones (error/warning): **{len([v for v in c.violations if v.severity != 'observation'])}**",
            f"- Dependencias circulares: **{len(c.circular_dependencies)}**",
            f"- Resultado: **{c.result}**",
            f"- Exit code herramienta: `{c.tool_exit_code}`",
            "",
            "### Reglas",
            "",
        ]
        for r in c.rules_evaluated:
            lines.append(f"- `{r['id']}`: {r['description']}")
        lines += ["", "### Violaciones", ""]
        comp_v = [v for v in c.violations if v.severity != "observation"]
        if not comp_v:
            lines.append("_Ninguna violación error/warning reportada por el analizador._")
        else:
            lines += [
                "| Severidad | Regla | Archivo | Línea | Dependencia | Mensaje | Recomendación |",
                "|---|---|---|---|---|---|---|",
            ]
            for v in comp_v:
                msg = v.message.replace("|", "\\|")[:160]
                reco = v.recommendation.replace("|", "\\|")[:120]
                lines.append(
                    f"| {v.severity} | `{v.rule}` | `{v.file}` | {v.line or ''} | `{v.dependency}` | {msg} | {reco} |"
                )
        if c.circular_dependencies:
            lines += ["", "### Ciclos", ""]
            for cycle in c.circular_dependencies:
                lines.append(f"- {' → '.join(cycle)}")
        lines.append("")

    lines += ["## Observaciones de acoplamiento / responsabilidades", ""]
    obs = [v for v in audit.coupling_observations if v.severity == "observation"]
    errors_coup = [v for v in audit.coupling_observations if v.severity == "error"]
    if errors_coup:
        lines += ["### Hallazgos (error)", ""]
        for v in errors_coup:
            lines.append(f"- `{v.file}:{v.line or '-'}` — **{v.rule}**: {v.message}")
            lines.append(f"  - Recomendación: {v.recommendation}")
    lines += ["", "### Observaciones (no fallan por LOC sola)", ""]
    for v in obs:
        lines.append(f"- `{v.file}` — {v.message}")
        lines.append(f"  - {v.recommendation}")

    lines += ["", "## Servicio de estimación (ML)", ""]
    ml = audit.ml_audit
    lines.append(f"- Conformidad arquitectónica: **{ml.get('architectural_conformance', {}).get('result', 'n/d')}**")
    lines.append(f"- Nota: {ml.get('analytical_validation_note', '')}")
    lines += ["", "| Check | OK | Detalle |", "|---|---|---|"]
    for c in ml.get("checks", []):
        lines.append(f"| `{c['name']}` | {'sí' if c['ok'] else 'no'} | {c['detail']} |")

    lines += [
        "",
        "## Cómo reproducir",
        "",
        "```bash",
        "python architecture-audit/scripts/run_architecture_audit.py",
        "```",
        "",
        "Configs: `architecture-audit/configs/backend-contracts.ini`, `architecture-audit/configs/frontend-rules.cjs`",
        "",
    ]
    (REPORTS / "architecture-report.md").write_text("\n".join(lines), encoding="utf-8")


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
