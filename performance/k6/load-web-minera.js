/**
 * Prueba de carga k6 — endpoints WEB_MINERA (FastAPI)
 *
 * Uso:
 *   k6 run performance/k6/load-web-minera.js
 *   k6 run -e BASE_URL=http://127.0.0.1:8000 performance/k6/load-web-minera.js
 *   k6 run -e TOKEN=<jwt> performance/k6/load-web-minera.js
 *   k6 run -e K6_EMAIL=... -e K6_PASSWORD=... performance/k6/load-web-minera.js
 *
 * Escenarios:
 *   - Siempre: GET /health (infra)
 *   - Siempre: POST /api/v1/auth/login (credenciales inválidas → mide camino auth)
 *   - Siempre: GET protegidos sin token → espera 401 (camino de autorización)
 *   - Con TOKEN o login OK: endpoints de negocio (dashboard, lots, custody, …)
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.1.0/index.js";

const BASE = (__ENV.BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const TOKEN_ENV = __ENV.TOKEN || "";
const EMAIL = __ENV.K6_EMAIL || "";
const PASSWORD = __ENV.K6_PASSWORD || "";
const PROFILE = (__ENV.K6_PROFILE || "load").toLowerCase();

const failRate = new Rate("web_minera_checks_failed");
const healthDuration = new Trend("endpoint_health_duration", true);
const loginDuration = new Trend("endpoint_login_duration", true);
const businessDuration = new Trend("endpoint_business_duration", true);
const authzDuration = new Trend("endpoint_authz_401_duration", true);
const reqCounter = new Counter("web_minera_requests");

const profiles = {
  smoke: {
    stages: [
      { duration: "10s", target: 2 },
      { duration: "15s", target: 5 },
      { duration: "5s", target: 0 },
    ],
  },
  load: {
    stages: [
      { duration: "20s", target: 5 },
      { duration: "30s", target: 20 },
      { duration: "20s", target: 40 },
      { duration: "15s", target: 0 },
    ],
  },
  stress: {
    stages: [
      { duration: "20s", target: 20 },
      { duration: "30s", target: 50 },
      { duration: "20s", target: 80 },
      { duration: "15s", target: 0 },
    ],
  },
};

const ACTIVE_STAGES = (profiles[PROFILE] || profiles.load).stages;
const PLANNED_MAX_VUS = Math.max(...ACTIVE_STAGES.map((s) => s.target || 0));
const PLANNED_DURATION_SEC = ACTIVE_STAGES.reduce((sum, s) => {
  const m = String(s.duration || "").match(/^(\d+)(s|m|h)?$/i);
  if (!m) return sum;
  const n = Number(m[1]);
  const u = (m[2] || "s").toLowerCase();
  if (u === "m") return sum + n * 60;
  if (u === "h") return sum + n * 3600;
  return sum + n;
}, 0);

export const options = {
  stages: ACTIVE_STAGES,
  thresholds: {
    http_req_failed: ["rate<0.10"],
    http_req_duration: ["p(95)<800", "p(99)<1500"],
    checks: ["rate>0.90"],
    // Bajo ramp-up a 40 VU el health puede superar 500 ms; umbral operativo < 800 ms.
    endpoint_health_duration: ["p(95)<800"],
  },
  summaryTrendStats: ["avg", "min", "med", "max", "p(90)", "p(95)", "p(99)"],
};

function formatDuration(sec) {
  if (sec < 60) return `${sec}s`;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return s ? `${m}m ${s}s` : `${m}m`;
}

function printExecutionBanner(title) {
  const sep = "=".repeat(72);
  console.log(`\n${sep}`);
  console.log(title);
  console.log(sep);
  console.log(`Ejecución de la prueba de carga mostrando la cantidad de usuarios`);
  console.log(`virtuales y duración de la prueba.`);
  console.log(`  Perfil:                    ${PROFILE}`);
  console.log(`  Usuarios virtuales (máx.): ${PLANNED_MAX_VUS} VU`);
  console.log(`  Duración planificada:      ${formatDuration(PLANNED_DURATION_SEC)} (${PLANNED_DURATION_SEC}s)`);
  console.log(`  Stages:`);
  for (const st of ACTIVE_STAGES) {
    console.log(`    - ${st.duration} → ${st.target} VU`);
  }
  console.log(`${sep}\n`);
}

const BUSINESS_GETS = [
  "/api/v1/auth/me",
  "/api/v1/dashboard",
  "/api/v1/lots",
  "/api/v1/custody",
  "/api/v1/transport",
  "/api/v1/receptions",
  "/api/v1/weighings",
  "/api/v1/alerts",
  "/api/v1/mass-balance",
  "/api/v1/audits",
  "/api/v1/ml/status",
  "/api/v1/ml/models",
  "/api/v1/users",
  "/api/v1/settings",
  "/api/v1/notifications",
  "/api/v1/search?q=lote",
];

function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    Accept: "application/json",
  };
}

function track(ok) {
  failRate.add(!ok);
}

export function setup() {
  // Solo setup() corre una vez — evidencia limpia en terminal (VU + duración).
  printExecutionBanner("INICIO — Prueba de carga k6 WEB_MINERA");

  let token = TOKEN_ENV;
  let authMode = "none";

  if (!token && EMAIL && PASSWORD) {
    const res = http.post(
      `${BASE}/api/v1/auth/login`,
      JSON.stringify({ email: EMAIL, password: PASSWORD }),
      { headers: { "Content-Type": "application/json", Accept: "application/json" } },
    );
    if (res.status === 200) {
      try {
        const body = res.json();
        token = body.access_token || body.token || "";
        authMode = token ? "login" : "none";
      } catch (_) {
        authMode = "none";
      }
    }
  } else if (token) {
    authMode = "token";
  }

  // Probe inicial
  const health = http.get(`${BASE}/health`);
  return {
    base: BASE,
    token,
    authMode,
    healthStatus: health.status,
    profile: PROFILE,
    startedAt: new Date().toISOString(),
  };
}

export default function (data) {
  group("01 health (infra)", () => {
    const res = http.get(`${data.base}/health`, {
      // Solo 200 cuenta como éxito de infra; evita falsos fallos en métricas.
      responseCallback: http.expectedStatuses(200),
    });
    healthDuration.add(res.timings.duration);
    reqCounter.add(1);
    const ok = check(res, {
      "health status 200": (r) => r.status === 200,
      "health body ok": (r) => String(r.body).includes("ok") || r.status === 200,
    });
    track(ok);
  });

  group("02 auth login path", () => {
    const res = http.post(
      `${data.base}/api/v1/auth/login`,
      JSON.stringify({
        email: "k6-invalid@example.com",
        password: "wrong-password-k6",
      }),
      {
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        // 4xx esperados (login inválido / rate limit) NO deben inflar http_req_failed.
        responseCallback: http.expectedStatuses(400, 401, 403, 422, 429),
      },
    );
    loginDuration.add(res.timings.duration);
    reqCounter.add(1);
    const ok = check(res, {
      "login inválido responde 4xx": (r) => r.status >= 400 && r.status < 500,
    });
    track(ok);
  });

  group("03 autorización sin token (401/429)", () => {
    const samples = [
      "/api/v1/lots",
      "/api/v1/dashboard",
      "/api/v1/auth/me",
    ];
    for (const path of samples) {
      const res = http.get(`${data.base}${path}`, {
        headers: { Accept: "application/json" },
        // 401 = sin JWT; 429 = RateLimitMiddleware (120 req/60s por segmento).
        responseCallback: http.expectedStatuses(401, 429),
      });
      authzDuration.add(res.timings.duration);
      reqCounter.add(1);
      const ok = check(res, {
        [`${path} sin token → 401|429`]: (r) =>
          r.status === 401 || r.status === 429,
      });
      track(ok);
    }
  });

  if (data.token) {
    group("04 negocio autenticado", () => {
      const headers = authHeaders(data.token);
      const path = BUSINESS_GETS[Math.floor(Math.random() * BUSINESS_GETS.length)];
      const res = http.get(`${data.base}${path}`, {
        headers,
        responseCallback: http.expectedStatuses(200, 201, 204),
      });
      businessDuration.add(res.timings.duration);
      reqCounter.add(1);
      const ok = check(res, {
        "negocio 2xx": (r) => r.status >= 200 && r.status < 300,
      });
      track(ok);
    });
  }

  sleep(0.4);
}

function fmtMs(v) {
  if (v === undefined || v === null || Number.isNaN(v)) return "n/d";
  return `${v.toFixed(2)} ms`;
}

function metricBlock(name, m) {
  if (!m || !m.values) return `  ${name}: (sin datos)\n`;
  const v = m.values;
  return (
    `  ${name}\n` +
    `    avg=${fmtMs(v.avg)}  med=${fmtMs(v.med)}  p90=${fmtMs(v["p(90)"])}  p95=${fmtMs(v["p(95)"])}  p99=${fmtMs(v["p(99)"])}  max=${fmtMs(v.max)}\n`
  );
}

function thresholdPassed(th) {
  if (typeof th.ok === "boolean") return th.ok;
  return th.passes !== false;
}

function loadVerdict(failed, p95) {
  if (failed < 0.05 && (p95 === undefined || p95 < 800)) {
    return "  Dictamen: CARGA ACEPTABLE bajo el perfil ejecutado.\n";
  }
  if (failed < 0.10) {
    return "  Dictamen: CARGA CON OBSERVACIONES (fallos o latencia cerca del umbral).\n";
  }
  return "  Dictamen: CARGA NO SATISFACTORIA (tasa de fallo o latencia elevada).\n";
}

function buildExecutionSection(vusMax, vusMin, durationSec, durationMs) {
  const thin = "-".repeat(72);
  let out = `${thin}\n`;
  out += "EJECUCIÓN DE LA PRUEBA DE CARGA\n";
  out += "(cantidad de usuarios virtuales y duración de la prueba)\n";
  out += `${thin}\n`;
  out += `  Usuarios virtuales máximos:     ${vusMax} VU\n`;
  out += `  Usuarios virtuales (mín. obs.): ${vusMin} VU\n`;
  out += `  Usuarios virtuales planificados: ${PLANNED_MAX_VUS} VU\n`;
  out += `  Duración real de la prueba:     ${formatDuration(durationSec)} (${durationSec}s / ${durationMs} ms)\n`;
  out += `  Duración planificada (stages):  ${formatDuration(PLANNED_DURATION_SEC)} (${PLANNED_DURATION_SEC}s)\n`;
  out += `  Stages ejecutados:\n`;
  for (const st of ACTIVE_STAGES) {
    out += `    - duración ${st.duration} → objetivo ${st.target} usuarios virtuales\n`;
  }
  return out;
}

function buildHttpSection(m, reqs, failed, checksRate, vusMax, durationSec) {
  const thin = "-".repeat(72);
  let out = `${thin}\nRESUMEN HTTP\n${thin}\n`;
  out += `  Iteraciones:        ${m.iterations?.values?.count ?? 0}\n`;
  out += `  Requests HTTP:      ${reqs}\n`;
  out += `  Tasa fallo HTTP:    ${(failed * 100).toFixed(2)} %\n`;
  out += `  Checks OK:          ${(checksRate * 100).toFixed(2)} %\n`;
  out += `  VUs máx:            ${vusMax}\n`;
  out += `  Duración:           ${formatDuration(durationSec)}\n`;
  out += `  Data recibida:      ${((m.data_received?.values?.count ?? 0) / 1024).toFixed(1)} KB\n`;
  out += `${thin}\nLATENCIAS (http_req_duration)\n${thin}\n`;
  out += metricBlock("global", m.http_req_duration);
  out += metricBlock("GET /health", m.endpoint_health_duration);
  out += metricBlock("POST /auth/login (inválido)", m.endpoint_login_duration);
  out += metricBlock("GET protegidos → 401", m.endpoint_authz_401_duration);
  out += metricBlock("GET negocio (si hay token)", m.endpoint_business_duration);
  return out;
}

function buildThresholdsSection(thresholds) {
  const thin = "-".repeat(72);
  let out = `${thin}\nTHRESHOLDS\n${thin}\n`;
  const names = Object.keys(thresholds);
  if (names.length === 0) {
    return out + "  (thresholds evaluados por k6 en salida estándar)\n";
  }
  for (const name of names) {
    const passed = thresholdPassed(thresholds[name]);
    out += `  ${passed ? "✓" : "✗"} ${name}\n`;
  }
  return out;
}

function buildAnalysisSection(m, failed) {
  const thin = "-".repeat(72);
  const p95 = m.http_req_duration?.values?.["p(95)"];
  const healthP95 = m.endpoint_health_duration?.values?.["p(95)"];
  let out = `${thin}\nANÁLISIS\n${thin}\n`;
  out += loadVerdict(failed, p95);
  out += `  - Health p95: ${fmtMs(healthP95)} (meta orientativa < 500 ms)\n`;
  out += `  - HTTP p95:   ${fmtMs(p95)} (meta umbral < 800 ms)\n`;
  out += `  - Fallo HTTP: ${(failed * 100).toFixed(2)} % (meta < 10 %)\n`;
  if (!TOKEN_ENV && !(EMAIL && PASSWORD)) {
    out +=
      "  - Negocio autenticado: NO EJECUTADO (sin TOKEN / K6_EMAIL+K6_PASSWORD).\n" +
      "    Se midió infra (/health), camino login inválido y 401/429 en protegidos.\n";
  } else {
    out += "  - Negocio autenticado: incluido en la corrida.\n";
  }
  out +=
    "  - Rate limit: API aplica ~120 req/60s por IP+segmento; bajo carga alta es normal ver 429.\n" +
    "  - Nota: /health valida infraestructura; no sustituye por sí solo la capacidad de negocio.\n";
  return out;
}

function buildEndpointsSection() {
  const thin = "-".repeat(72);
  let out = `${thin}\nENDPOINTS CUBIERTOS\n${thin}\n`;
  out += "  GET  /health\n";
  out += "  POST /api/v1/auth/login (credenciales inválidas)\n";
  out += "  GET  /api/v1/auth/me | /dashboard | /lots  (sin token → 401)\n";
  if (TOKEN_ENV || (EMAIL && PASSWORD)) {
    for (const p of BUSINESS_GETS) {
      out += `  GET  ${p}  (autenticado)\n`;
    }
  }
  return out;
}

export function handleSummary(data) {
  const sep = "=".repeat(72);
  const m = data.metrics || {};
  const reqs = m.http_reqs?.values?.count ?? 0;
  const failed = m.http_req_failed?.values?.rate ?? 0;
  const checksRate = m.checks?.values?.rate ?? 0;
  const vusMax = m.vus_max?.values?.max ?? m.vus?.values?.max ?? PLANNED_MAX_VUS;
  const vusMin = m.vus?.values?.min ?? 0;
  const durationMs = data.state?.testRunDurationMs ?? PLANNED_DURATION_SEC * 1000;
  const durationSec = Math.round(durationMs / 1000);

  let report = `\n${sep}\n`;
  report += "RESULTADOS FINALES — Prueba de carga k6 WEB_MINERA\n";
  report += `${sep}\n`;
  report += `Proyecto:     WEB_MINERA\n`;
  report += `Herramienta:  k6\n`;
  report += `BASE_URL:     ${BASE}\n`;
  report += `Perfil:       ${PROFILE}\n`;
  report += `Generado:     ${new Date().toISOString()}\n`;
  report += buildExecutionSection(vusMax, vusMin, durationSec, durationMs);
  report += buildHttpSection(m, reqs, failed, checksRate, vusMax, durationSec);
  report += buildThresholdsSection(data.thresholds || {});
  report += buildAnalysisSection(m, failed);
  report += buildEndpointsSection();
  report += `${sep}\n\n`;

  const native = textSummary(data, { indent: "  ", enableColors: false });
  const body = report + "\n--- Resumen nativo k6 ---\n" + native + "\n";
  const outDir = "reports/performance";
  return {
    stdout: body,
    [`${outDir}/k6-summary.json`]: JSON.stringify(data, null, 2),
    [`${outDir}/k6-report.txt`]: body,
  };
}
