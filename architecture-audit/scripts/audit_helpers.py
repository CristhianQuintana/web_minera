"""Helpers de baja complejidad para run_architecture_audit.py."""

from __future__ import annotations

import ast
import csv
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

# Types kept loose to avoid circular imports with the runner module.


def build_module_adjacency(graph: Any, modules: list[str]) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {}
    module_set = set(modules)
    for mod in modules:
        try:
            deps = graph.find_modules_directly_imported_by(mod)
        except Exception:  # noqa: BLE001
            deps = []
        adj[mod] = sorted(d for d in deps if d in module_set)
    return adj


def find_cycles_dfs(adj: dict[str, list[str]], modules: list[str]) -> list[list[str]]:
    cycles: list[list[str]] = []
    seen_cycle_keys: set[tuple[str, ...]] = set()
    color: dict[str, int] = {m: 0 for m in modules}
    stack: list[str] = []

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for nxt in adj.get(node, []):
            _handle_edge(nxt, color, stack, seen_cycle_keys, cycles, visit)
        stack.pop()
        color[node] = 2

    for m in modules:
        if color[m] == 0:
            visit(m)
    return cycles


def _handle_edge(
    nxt: str,
    color: dict[str, int],
    stack: list[str],
    seen_cycle_keys: set[tuple[str, ...]],
    cycles: list[list[str]],
    visit: Callable[[str], None],
) -> None:
    if color[nxt] == 1:
        i = stack.index(nxt)
        cycle = stack[i:] + [nxt]
        key = tuple(sorted(set(cycle)))
        if key not in seen_cycle_keys:
            seen_cycle_keys.add(key)
            cycles.append(cycle)
        return
    if color[nxt] == 0:
        visit(nxt)


def backend_recommendation(rule: str, dep: str) -> str:
    dep_l = dep.lower()
    if "composition" in dep_l:
        return (
            "Inyectar el contenedor desde el composition root (p. ej. app.state) "
            "sin que adapters importen app.composition."
        )
    frameworks = ("fastapi", "starlette", "uvicorn", "httpx", "supabase", "sqlalchemy", "pydantic")
    if any(x in dep_l for x in frameworks):
        return "Mover el import a adapters/infrastructure o expresar la necesidad vía un puerto."
    if "adapters" in dep_l:
        return "Depender del puerto (Protocol) e inyectar el adaptador en composition."
    return f"Reorientar la dependencia para respetar el contrato '{rule}'."


def parse_arrow_violation(line: str, current_contract: str, violation_cls: type) -> Any | None:
    m = re.search(
        r"-\s+(?P<source>app\.[\w\.]+)\s+->\s+(?P<dep>app\.[\w\.]+|[\w\.]+)\s*(?:\(l\.(?P<line>\d+)\))?",
        line,
    )
    if not m:
        return None
    source = m.group("source")
    dep = m.group("dep")
    line_no = int(m.group("line")) if m.group("line") else None
    return violation_cls(
        component="backend",
        severity="error",
        rule=current_contract if current_contract else "import-linter",
        file="backend/" + source.replace(".", "/") + ".py",
        line=line_no,
        dependency=dep,
        message=line.lstrip("- ").strip(),
        recommendation=backend_recommendation(current_contract, dep),
    )


def parse_imports_violation(line: str, current_contract: str, violation_cls: type) -> Any | None:
    m2 = re.search(r"(?P<source>app\.[\w\.]+)\s+imports\s+(?P<dep>[\w\.]+)", line, re.I)
    if not m2:
        return None
    source = m2.group("source")
    dep = m2.group("dep")
    return violation_cls(
        component="backend",
        severity="error",
        rule=current_contract,
        file=f"backend/{source.replace('.', '/')}.py",
        line=None,
        dependency=dep,
        message=line,
        recommendation=backend_recommendation(current_contract, dep),
    )


def update_contract_name(line: str, current: str) -> str:
    lower = line.lower()
    if "independence" not in lower and "layer direction" not in lower:
        return current
    if "KEPT" in line or "BROKEN" in line or "Contracts" in line:
        return current
    return line[:120]


def frontend_recommendation(rule: str) -> str:
    mapping = {
        "domain-no-ui-or-outer-layers": "Mantener domain como tipos/reglas puras; mover UI a presentation.",
        "domain-no-node-modules-ui": "Eliminar import de React/Next del dominio.",
        "application-no-adapters-or-next": "Inyectar PlatformPort; cablear adaptador solo en composition.",
        "ports-no-adapters": "El puerto solo declara contratos TypeScript.",
        "no-direct-database-from-ui": "Toda persistencia debe pasar por API/adaptadores outbound.",
        "presentation-prefer-ports-over-adapters": (
            "Importar desde @/composition o hooks que usen PlatformPort; no desde @/adapters/...."
        ),
        "no-circular": "Romper el ciclo con un puerto o módulo neutro de tipos.",
    }
    return mapping.get(rule, "Ajustar imports para respetar la dirección hexagonal.")


def circular_violation(source: str, dep: dict[str, Any], violation_cls: type) -> Any:
    cycle = dep.get("cycle") or []
    return violation_cls(
        component="frontend",
        severity="error",
        rule="no-circular",
        file=f"frontend/{source}",
        line=None,
        dependency=" -> ".join(cycle) if cycle else (dep.get("resolved") or ""),
        message=f"Dependencia circular desde {source}",
        recommendation="Extraer contrato compartido o invertir la dependencia vía ports/composition.",
    )


def rule_violation(source: str, dep: dict[str, Any], rule: dict[str, Any], violation_cls: type) -> Any | None:
    name = rule.get("name") or "unknown"
    severity = rule.get("severity") or "error"
    if severity == "ignore":
        return None
    to_mod = dep.get("module") or dep.get("resolved") or ""
    return violation_cls(
        component="frontend",
        severity="error" if severity == "error" else "warning",
        rule=name,
        file=f"frontend/{source}",
        line=None,
        dependency=str(to_mod),
        message=f"{source} → {to_mod} incumple {name}",
        recommendation=frontend_recommendation(name),
    )


def dedupe_violations(violations: list[Any]) -> list[Any]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[Any] = []
    for v in violations:
        key = (v.rule, v.file, v.dependency)
        if key in seen:
            continue
        seen.add(key)
        unique.append(v)
    return unique


def check_adapters_composition(dep_file: Path, rel: Callable[[Path], str], violation_cls: type) -> list[Any]:
    if not dep_file.exists():
        return []
    text = dep_file.read_text(encoding="utf-8")
    if "app.composition" not in text and "from app.composition" not in text:
        return []
    line_no = None
    for i, ln in enumerate(text.splitlines(), 1):
        if "composition" in ln and "import" in ln:
            line_no = i
            break
    return [
        violation_cls(
            component="backend",
            severity="error",
            rule="adapters-must-not-import-composition",
            file=rel(dep_file),
            line=line_no,
            dependency="app.composition.container",
            message="El adaptador inbound HTTP importa el composition root (Container).",
            recommendation=(
                "Leer container solo desde request.app.state inyectado en composition; "
                "tipar Depends con Protocol/callable sin importar Container."
            ),
        )
    ]


def check_presentation_adapters(
    paths: list[Path],
    rel: Callable[[Path], str],
    violation_cls: type,
) -> list[Any]:
    out: list[Any] = []
    pattern = re.compile(r"""from\s+["'](@/adapters/[^"']+)["']""")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            out.append(
                violation_cls(
                    component="frontend",
                    severity="error",
                    rule="presentation-prefer-ports-over-adapters",
                    file=rel(path),
                    line=line_no,
                    dependency=m.group(1),
                    message=f"UI importa adaptador concreto {m.group(1)}",
                    recommendation="Usar @/composition o un hook sobre PlatformPort; tipar errores vía dominio/ports.",
                )
            )
    return out


def coupling_candidate_notes(
    candidates: list[tuple[Path, str, str]],
    rel: Callable[[Path], str],
    violation_cls: type,
) -> list[Any]:
    out: list[Any] = []
    for path, justification, reco in candidates:
        if not path.exists():
            continue
        nlines = len(path.read_text(encoding="utf-8").splitlines())
        out.append(
            violation_cls(
                component="backend" if "backend" in str(path) else "frontend",
                severity="observation",
                rule="responsibility-concentration",
                file=rel(path),
                line=None,
                dependency="",
                message=(
                    f"{justification} (tamaño actual: {nlines} líneas; "
                    "el tamaño solo contextualiza, no define defecto)."
                ),
                recommendation=reco,
            )
        )
    return out


def collect_imports(tree: ast.AST) -> list[str]:
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def ml_domain_checks(
    domain_est: Path,
    rel: Callable[[Path], str],
    check: Callable[[str, bool, str], None],
    result: dict[str, Any],
) -> None:
    forbidden = ("fastapi", "uvicorn", "sklearn", "torch", "tensorflow", "numpy", "pandas", "pydantic")
    if not domain_est.exists():
        return
    tree = ast.parse(domain_est.read_text(encoding="utf-8"))
    imports = collect_imports(tree)
    bad = [i for i in imports if i.split(".")[0] in forbidden]
    check("domain_free_of_ml_frameworks", not bad, f"imports={imports}; forbidden_hits={bad}")
    if bad:
        result["violations"].append(
            {
                "rule": "ml-domain-no-framework",
                "file": rel(domain_est),
                "dependency": ",".join(bad),
                "message": "Dominio ML importa framework prohibido",
            }
        )
    src = domain_est.read_text(encoding="utf-8")
    has_version = "version" in src and "1.0.0" in src
    check("model_version_identified", has_version, "ExpectedQuantityEstimator.version == '1.0.0'")


def ml_use_case_checks(use_case: Path, check: Callable[[str, bool, str], None]) -> None:
    if not use_case.exists():
        return
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


def ml_adapter_checks(adapter: Path, check: Callable[[str, bool, str], None]) -> None:
    if not adapter.exists():
        return
    ad = adapter.read_text(encoding="utf-8")
    check("adapter_uses_composition", "estimate_use_case" in ad or "composition" in ad, "HTTP adapter cablea composition")
    check("adapter_has_pydantic_request_model", "BaseModel" in ad, "EstimateRequest como contrato de borde HTTP")


def ml_test_checks(test: Path, rel: Callable[[Path], str], check: Callable[[str, bool, str], None]) -> None:
    if not test.exists():
        return
    t = test.read_text(encoding="utf-8")
    check("reproducible_unit_test", "expected_quantity" in t and "model_version" in t, rel(test))
    check("test_input_fixture", "origin_quantity" in t, "features de prueba en test_estimator.py")


def ml_arch_ok(result: dict[str, Any]) -> bool:
    required = {
        "domain_estimator_exists",
        "application_use_case_exists",
        "composition_wiring_exists",
        "domain_free_of_ml_frameworks",
        "model_version_identified",
        "input_output_contract",
        "use_case_depends_on_domain_not_fastapi",
        "reproducible_unit_test",
    }
    return all(c["ok"] for c in result["checks"] if c["name"] in required) and not result["violations"]


def write_json_report(reports: Path, audit: Any) -> None:
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
    (reports / "architecture-report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_csv_report(reports: Path, all_violations: list[Any]) -> None:
    with (reports / "violations.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["component", "severity", "rule", "file", "line", "dependency", "message", "recommendation"],
        )
        writer.writeheader()
        for v in all_violations:
            writer.writerow(asdict(v))


def md_component_section(name: str, c: Any) -> list[str]:
    lines = [
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
    return lines


def md_coupling_section(coupling: list[Any]) -> list[str]:
    lines = ["## Observaciones de acoplamiento / responsabilidades", ""]
    obs = [v for v in coupling if v.severity == "observation"]
    errors_coup = [v for v in coupling if v.severity == "error"]
    if errors_coup:
        lines += ["### Hallazgos (error)", ""]
        for v in errors_coup:
            lines.append(f"- `{v.file}:{v.line or '-'}` — **{v.rule}**: {v.message}")
            lines.append(f"  - Recomendación: {v.recommendation}")
    lines += ["", "### Observaciones (no fallan por LOC sola)", ""]
    for v in obs:
        lines.append(f"- `{v.file}` — {v.message}")
        lines.append(f"  - {v.recommendation}")
    return lines


def md_ml_section(ml: dict[str, Any]) -> list[str]:
    lines = ["", "## Servicio de estimación (ML)", ""]
    lines.append(f"- Conformidad arquitectónica: **{ml.get('architectural_conformance', {}).get('result', 'n/d')}**")
    lines.append(f"- Nota: {ml.get('analytical_validation_note', '')}")
    lines += ["", "| Check | OK | Detalle |", "|---|---|---|"]
    for c in ml.get("checks", []):
        lines.append(f"| `{c['name']}` | {'sí' if c['ok'] else 'no'} | {c['detail']} |")
    return lines


def write_markdown_report(reports: Path, audit: Any) -> None:
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
        lines += md_component_section(name, c)
    lines += md_coupling_section(audit.coupling_observations)
    lines += md_ml_section(audit.ml_audit)
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
    (reports / "architecture-report.md").write_text("\n".join(lines), encoding="utf-8")


def write_depcruise_graph(graph_path: Path, proc_json_stdout: str, proc_json_code: int, proc_json_stderr: str) -> dict[str, Any]:
    graph_data: dict[str, Any] = {}
    raw_json = (proc_json_stdout or "").strip()
    if raw_json.startswith("{"):
        try:
            graph_data = json.loads(raw_json)
            graph_path.write_text(json.dumps(graph_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except json.JSONDecodeError:
            graph_path.write_text(raw_json, encoding="utf-8")
        return graph_data
    graph_path.write_text(
        json.dumps(
            {
                "error": "dependency-cruiser json unavailable",
                "exit": proc_json_code,
                "stderr": proc_json_stderr,
                "stdout_head": raw_json[:2000],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return graph_data


def fallback_depcruise_err(tool_stdout: str, violation_cls: type) -> list[Any]:
    out: list[Any] = []
    for m in re.finditer(
        r"error\s+(?P<rule>[\w-]+):\s+(?P<src>\S+)\s+→\s+(?P<dst>\S+)",
        tool_stdout,
    ):
        out.append(
            violation_cls(
                component="frontend",
                severity="error",
                rule=m.group("rule"),
                file=f"frontend/{m.group('src')}",
                line=None,
                dependency=m.group("dst"),
                message=f"{m.group('src')} → {m.group('dst')} incumple {m.group('rule')}",
                recommendation=frontend_recommendation(m.group("rule")),
            )
        )
    return out
