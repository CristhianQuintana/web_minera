# architecture-audit — WEB_MINERA

Auditoría hexagonal automatizada (Import Linter + Dependency Cruiser + ML + acoplamiento).

## Comando central

```bash
python architecture-audit/scripts/run_architecture_audit.py
```

En Windows (venv backend):

```powershell
.\backend\.venv\Scripts\python.exe architecture-audit\scripts\run_architecture_audit.py
```

## Salidas

- `reports/architecture-report.md`
- `reports/architecture-report.json`
- `reports/violations.csv`
- `reports/dependency-graph.json`

## Documentación de reglas

Ver `docs/REGLAS_ARQUITECTONICAS.md`.
