#!/usr/bin/env python3
"""Auditoría M1.1 — Importaciones prohibidas en el dominio ML de WEB_MINERA.

Inspecciona los 3 módulos canónicos de ``ml/domain`` y detecta dependencias
externas o de capas externas que incumplan la separación hexagonal del núcleo.

No modifica archivos del proyecto: solo lectura + reporte por stdout.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# Raíz del repositorio (audit/ml/ → ../..)
REPO_ROOT = Path(__file__).resolve().parents[2]
ML_DOMAIN = REPO_ROOT / "ml" / "domain"

# Los 3 archivos del dominio considerados en la auditoría M1.1 (componente ML).
DOMAIN_FILES: tuple[Path, ...] = (
    ML_DOMAIN / "__init__.py",
    ML_DOMAIN / "services" / "__init__.py",
    ML_DOMAIN / "services" / "estimator.py",
)

# Dependencias / prefijos prohibidos en el núcleo de dominio.
# Justificación: el dominio debe permanecer libre de frameworks, transporte HTTP,
# ORMs, SDKs de infra y de capas externas (application/adapters/composition/…).
FORBIDDEN: dict[str, str] = {
    "fastapi": "Framework web HTTP; pertenece a adapters/presentation, no al dominio.",
    "uvicorn": "Servidor ASGI; infraestructura de ejecución, no dominio.",
    "starlette": "Stack HTTP subyacente a FastAPI; acoplaría el dominio al transporte.",
    "pydantic": "Validación/serialización de API; contrato de borde, no regla de negocio.",
    "httpx": "Cliente HTTP; I/O de red externo al núcleo de dominio.",
    "requests": "Cliente HTTP; misma razón que httpx.",
    "supabase": "SDK de infraestructura/persistencia; viola independencia del dominio.",
    "sqlalchemy": "ORM/persistencia; detalle de infraestructura.",
    "sklearn": "Framework ML externo; el dominio debe expresar reglas sin acoplar librerías.",
    "torch": "Framework ML externo; acoplamiento de infraestructura de modelo.",
    "tensorflow": "Framework ML externo; acoplamiento de infraestructura de modelo.",
    "numpy": "Dependencia numérica externa; no requerida por el dominio heurístico actual.",
    "pandas": "Dependencia de datos externa; no pertenece al núcleo de dominio.",
    "adapters": "Capa hexagonal externa; el dominio no debe conocer adaptadores.",
    "application": "Capa de casos de uso; dependencia invertida incorrecta hacia afuera.",
    "composition": "Composition root / wiring; no debe filtrarse al dominio.",
    "presentation": "Capa de presentación HTTP; borde del sistema.",
    "infrastructure": "Infraestructura; detalle técnico externo al dominio.",
    "ports": "Puertos son contratos de borde; el dominio no debe importarlos en este PMV.",
}


@dataclass(frozen=True)
class Detection:
    file: Path
    line: int
    dependency: str
    statement: str
    reason: str


def _matches_forbidden(imported: str) -> tuple[str, str] | None:
    """Devuelve (prefijo_prohibido, justificación) si ``imported`` incumple."""
    root = imported.split(".", 1)[0]
    if root in FORBIDDEN:
        return root, FORBIDDEN[root]
    # Prefijos de paquete relativos al servicio ML (p.ej. composition.foo).
    for banned, reason in FORBIDDEN.items():
        if imported == banned or imported.startswith(f"{banned}."):
            return banned, reason
    return None


def _extract_imports(path: Path) -> list[tuple[int, str, str]]:
    """Lista (línea, módulo_importado, sentencia_textual) vía AST."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    lines = source.splitlines()
    found: list[tuple[int, str, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                stmt = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else f"import {alias.name}"
                found.append((node.lineno, alias.name, stmt))
        elif isinstance(node, ast.ImportFrom):
            # from X import Y  →  módulo base X (None si from . import …)
            module = node.module or ""
            if node.level and not module:
                # Import relativo puro (from . import foo) — dominio interno, permitido.
                continue
            if node.level and module:
                # from .services import x → dominio interno relativo; no cuenta como externo.
                continue
            stmt = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else f"from {module} import ..."
            found.append((node.lineno, module, stmt))
    return found


def audit(files: tuple[Path, ...] = DOMAIN_FILES) -> list[Detection]:
    detections: list[Detection] = []
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(f"Archivo de dominio no encontrado: {path}")
        for line, imported, stmt in _extract_imports(path):
            hit = _matches_forbidden(imported)
            if hit is None:
                continue
            banned, reason = hit
            detections.append(
                Detection(
                    file=path,
                    line=line,
                    dependency=imported,
                    statement=stmt,
                    reason=f"{banned}: {reason}",
                )
            )
    return detections


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def render_report(files: tuple[Path, ...], detections: list[Detection]) -> str:
    affected = sorted({_rel(d.file) for d in detections})
    lines: list[str] = [
        "=" * 72,
        "AUDITORÍA M1.1 — Importaciones prohibidas (dominio ML / WEB_MINERA)",
        "=" * 72,
        "",
        f"Raíz del repositorio : {REPO_ROOT}",
        f"Directorio de dominio: {_rel(ML_DOMAIN)}",
        "",
        "--- Archivos inspeccionados ---",
    ]
    for path in files:
        lines.append(f"  - {_rel(path)}")

    lines.extend(
        [
            "",
            "--- Dependencias prohibidas (catálogo) ---",
        ]
    )
    for name, reason in FORBIDDEN.items():
        lines.append(f"  - {name}: {reason}")

    lines.extend(
        [
            "",
            "--- Detecciones ---",
        ]
    )
    if not detections:
        lines.append("  (ninguna)")
    else:
        for d in detections:
            lines.append(
                f"  [{_rel(d.file)}:{d.line}] dependencia={d.dependency!r}  |  {d.statement}"
            )
            lines.append(f"      justificación: {d.reason}")

    lines.extend(
        [
            "",
            "--- Resumen ---",
            f"  Archivos inspeccionados : {len(files)}",
            f"  Archivos afectados      : {len(affected)}",
            f"  Total de detecciones    : {len(detections)}",
            f"  Índice de contaminación : {(len(affected) / len(files) * 100.0):.1f} %",
            f"  Meta GQM M1.1           : 0,0 %",
            f"  Estado                  : {'CUMPLE' if not detections else 'NO CUMPLE'}",
            "",
            "=" * 72,
        ]
    )
    if affected:
        lines.append("Archivos afectados:")
        for a in affected:
            lines.append(f"  - {a}")
        lines.append("=" * 72)
    return "\n".join(lines)


def main() -> int:
    try:
        detections = audit()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    report = render_report(DOMAIN_FILES, detections)
    print(report)
    return 0 if not detections else 1


if __name__ == "__main__":
    sys.exit(main())
