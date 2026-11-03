# Riesgos residuales aceptados — cierre PMV2 WEB

Fecha: 2026-11-03
SHA base remediacion: `ad30938bedec5b3ea6618e61382749a27440b538` (mas commit de informes de cierre)
Dictamen asociado: **APTA CON RIESGOS ACEPTADOS**

| ID | Riesgo | Severidad | Mitigacion | Vence revision |
|---|---|---|---|---|
| WEB-AUD-012 | RLS multi-org no probado con JWT reales en esta corrida | Alta | Politicas SQL en migraciones + require() backend; prueba viva pendiente | 2026-11-17 |
| WEB-AUD-005 | E2E login/logout/create con usuario real omitidos (sin E2E_EMAIL/PASSWORD) | Alta | Casos negativos publicos aprobados; CI debe inyectar secretos | 2026-11-17 |
| WEB-AUD-002 | Axe solo en /login (no dashboard/lots autenticados) | Media | 0 violaciones critical/serious en login | 2026-11-17 |
| WEB-AUD-003 | k6 solo smoke `/health` (no 500 VU ni endpoints de negocio) | Media | p95 health 16.93 ms < 800 ms; ampliar perfil | 2026-11-17 |
| WEB-AUD-004 | Disponibilidad >=99.5% / MTTR <5 min | Media | No verificable; requiere monitoreo | 2026-12-01 |
| SEC-WEB-01 residual | npm: vulns residuales (zod/postcss/toolchain) | Media | EXCEPCIONES_FORMALES.md; Next 15.5.28 | 2026-11-17 |
| SEC-WEB-03/04 prod | Revalidacion Render live incompleta | Baja | Codigo: demo reject + docs off si APP_ENV=production; verificado local | 2026-11-17 |

Aceptacion de desarrollo: riesgos documentados no impiden cierre documental PMV2 I1-I2 con evidencia de codigo/pruebas locales.
Aceptacion formal QA: pendiente firma humana sobre este registro.
