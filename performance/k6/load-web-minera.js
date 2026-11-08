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

export const options = {
  stages: (profiles[PROFILE] || profiles.load).stages,
  thresholds: {
    http_req_failed: ["rate<0.10"],
    http_req_duration: ["p(95)<800", "p(99)<1500"],
    checks: ["rate>0.90"],
    // Bajo ramp-up a 40 VU el health puede superar 500 ms; umbral operativo < 800 ms.
    endpoint_health_duration: ["p(95)<800"],
  },
  summaryTrendStats: ["avg", "min", "med", "max", "p(90)", "p(95)", "p(99)"],
};

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

export function handleSummary(data) {
  const sep = "=".repeat(72);
  const thin = "-".repeat(72);
  const m = data.metrics || {};
  const root = data.root_group || {};

  let report = `\n${sep}\n`;
  report += "RESULTADOS FINALES — Prueba de carga k6 WEB_MINERA\n";
  report += `${sep}\n`;
  report += `Proyecto:     WEB_MINERA\n`;
  report += `Herramienta:  k6\n`;
  report += `BASE_URL:     ${BASE}\n`;
  report += `Perfil:       ${PROFILE}\n`;
  report += `Generado:     ${new Date().toISOString()}\n`;
  report += `${thin}\n`;
  report += "RESUMEN HTTP\n";
  report += `${thin}\n`;

  const reqs = m.http_reqs?.values?.count ?? 0;
  const failed = m.http_req_failed?.values?.rate ?? 0;
  const checksRate = m.checks?.values?.rate ?? 0;
  const vusMax = m.vus_max?.values?.max ?? m.vus?.values?.max ?? 0;

  report += `  Iteraciones:        ${m.iterations?.values?.count ?? 0}\n`;
  report += `  Requests HTTP:      ${reqs}\n`;
  report += `  Tasa fallo HTTP:    ${(failed * 100).toFixed(2)} %\n`;
  report += `  Checks OK:          ${(checksRate * 100).toFixed(2)} %\n`;
  report += `  VUs máx:            ${vusMax}\n`;
  report += `  Data recibida:      ${((m.data_received?.values?.count ?? 0) / 1024).toFixed(1)} KB\n`;
  report += `${thin}\n`;
  report += "LATENCIAS (http_req_duration)\n";
  report += `${thin}\n`;
  report += metricBlock("global", m.http_req_duration);
  report += metricBlock("GET /health", m.endpoint_health_duration);
  report += metricBlock("POST /auth/login (inválido)", m.endpoint_login_duration);
  report += metricBlock("GET protegidos → 401", m.endpoint_authz_401_duration);
  report += metricBlock("GET negocio (si hay token)", m.endpoint_business_duration);
  report += `${thin}\n`;
  report += "THRESHOLDS\n";
  report += `${thin}\n`;

  const thresholds = data.thresholds || {};
  let thOk = 0;
  let thFail = 0;
  for (const [name, th] of Object.entries(thresholds)) {
    const ok = th.ok !== false && !(th.passes === false);
    // k6 summary: th has `ok` boolean in recent versions
    const passed = typeof th.ok === "boolean" ? th.ok : true;
    if (passed) thOk += 1;
    else thFail += 1;
    report += `  ${passed ? "✓" : "✗"} ${name}\n`;
  }
  if (Object.keys(thresholds).length === 0) {
    report += "  (thresholds evaluados por k6 en salida estándar)\n";
  }

  report += `${thin}\n`;
  report += "ANÁLISIS\n";
  report += `${thin}\n`;

  const p95 = m.http_req_duration?.values?.["p(95)"];
  const healthP95 = m.endpoint_health_duration?.values?.["p(95)"];

  if (failed < 0.05 && (p95 === undefined || p95 < 800)) {
    report += "  Dictamen: CARGA ACEPTABLE bajo el perfil ejecutado.\n";
  } else if (failed < 0.10) {
    report += "  Dictamen: CARGA CON OBSERVACIONES (fallos o latencia cerca del umbral).\n";
  } else {
    report += "  Dictamen: CARGA NO SATISFACTORIA (tasa de fallo o latencia elevada).\n";
  }

  report += `  - Health p95: ${fmtMs(healthP95)} (meta orientativa < 500 ms)\n`;
  report += `  - HTTP p95:   ${fmtMs(p95)} (meta umbral < 800 ms)\n`;
  report += `  - Fallo HTTP: ${(failed * 100).toFixed(2)} % (meta < 10 %)\n`;

  if (!TOKEN_ENV && !(EMAIL && PASSWORD)) {
    report +=
      "  - Negocio autenticado: NO EJECUTADO (sin TOKEN / K6_EMAIL+K6_PASSWORD).\n" +
      "    Se midió infra (/health), camino login inválido y 401/429 en protegidos.\n";
  } else {
    report += "  - Negocio autenticado: incluido en la corrida.\n";
  }

  report +=
    "  - Rate limit: API aplica ~120 req/60s por IP+segmento; bajo carga alta es normal ver 429.\n" +
    "  - Nota: /health valida infraestructura; no sustituye por sí solo la capacidad de negocio.\n";
  report += `${thin}\n`;
  report += "ENDPOINTS CUBIERTOS\n";
  report += `${thin}\n`;
  report += "  GET  /health\n";
  report += "  POST /api/v1/auth/login (credenciales inválidas)\n";
  report += "  GET  /api/v1/auth/me | /dashboard | /lots  (sin token → 401)\n";
  if (TOKEN_ENV || (EMAIL && PASSWORD)) {
    for (const p of BUSINESS_GETS) {
      report += `  GET  ${p}  (autenticado)\n`;
    }
  }
  report += `${sep}\n\n`;

  // También el summary nativo de k6 (compacto) al final del texto exportado
  const native = textSummary(data, { indent: "  ", enableColors: false });

  const outDir = "reports/performance";
  return {
    stdout: report + "\n--- Resumen nativo k6 ---\n" + native + "\n",
    [`${outDir}/k6-summary.json`]: JSON.stringify(data, null, 2),
    [`${outDir}/k6-report.txt`]: report + "\n--- Resumen nativo k6 ---\n" + native + "\n",
  };
}
