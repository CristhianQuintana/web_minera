import type { CurrentUser, PageResult } from "@/domain/entities";

export const DEMO_EMAIL = "cristhian@gmail.com";
export const DEMO_PASSWORD = "Cristhian123";
export const DEMO_TOKEN = "demo-local-cristhian";

export const demoUser: CurrentUser = {
  id: "demo-user-cristhian",
  email: DEMO_EMAIL,
  full_name: "Cristhian",
  role: "admin",
  role_label: "Administrador",
  organization_id: "demo-org",
  status: "active",
  invitation_status: "active",
  permissions: [
    "view_lots",
    "register_lot",
    "view_custody",
    "transfer_custody",
    "view_transport",
    "register_transport",
    "view_receptions",
    "register_reception",
    "register_weighing",
    "view_balance",
    "view_alerts",
    "review_alert",
    "view_audit",
    "view_ml",
    "estimate_ml",
    "manage_users",
    "manage_settings",
    "export",
  ],
};

const now = "2026-09-24T15:20:00.000Z";

const tables: Record<string, Array<Record<string, unknown>>> = {
  lots: [
    {
      id: "lot-1",
      code: "LOT-2026-00021",
      mineral: "Oro",
      quantity: 125.4,
      unit: "kg",
      status: "received",
      created_at: now,
      qr_payload: "LOT-2026-00021",
      latitude: 5.07,
      longitude: -75.52,
      evidences: [{ id: "ev-1" }],
      custody: [{ id: "ct-1" }],
    },
    {
      id: "lot-2",
      code: "LOT-2026-00022",
      mineral: "Plata",
      quantity: 80,
      unit: "kg",
      status: "inTransit",
      created_at: "2026-09-23T10:00:00.000Z",
      qr_payload: "LOT-2026-00022",
      evidences: [],
      custody: [],
    },
  ],
  custody: [
    {
      id: "ct-1",
      lot_id: "lot-1",
      origin: "Mina El Alto",
      destination: "Planta piloto",
      quantity: 125.4,
      occurred_at: now,
      status: "completed",
      responsible: "Cristhian",
    },
  ],
  transport: [
    {
      id: "tr-1",
      lot_id: "lot-2",
      driver: "Luis Pérez",
      vehicle: "Turbo 2.5",
      plate: "ABC123",
      started_at: now,
      ended_at: null,
      status: "in_progress",
      origin: "Mina El Alto",
      destination: "Planta piloto",
    },
  ],
  receptions: [
    {
      id: "rc-1",
      lot_id: "lot-1",
      responsible: "Ana Receptor",
      occurred_at: now,
      declared_quantity: 125.4,
      received_quantity: 123.1,
      unit: "kg",
      status: "confirmed",
    },
  ],
  weighings: [
    {
      id: "wg-1",
      lot_id: "lot-1",
      responsible: "Ana Receptor",
      occurred_at: now,
      weight: 123.1,
      unit: "kg",
      instrument: "Báscula planta",
    },
  ],
  "mass-balance": [
    {
      id: "mb-1",
      lot_id: "lot-1",
      origin_quantity: 125.4,
      received_quantity: 123.1,
      difference: -2.3,
      difference_percent: -1.83,
      tolerance_value: 3,
      tolerance_unit: "percent",
      tolerance_version: 1,
      status: "within_tolerance",
      calculated_at: now,
    },
  ],
  alerts: [
    {
      id: "al-1",
      severity: "medium",
      alert_type: "ml_deviation",
      lot_id: "lot-2",
      created_at: now,
      status: "new",
      title: "Señal para revisión de cantidad esperada",
      reason: "Desviación estimada superior al umbral de revisión. No constituye sentencia.",
      rule_applied: "expected-quantity-baseline",
    },
  ],
  audits: [
    {
      id: "au-1",
      created_at: now,
      user_id: "Cristhian",
      action: "register_lot",
      entity: "lot",
      entity_id: "lot-1",
      lot_id: "lot-1",
      result: "success",
    },
  ],
  "ml/inferences": [
    {
      id: "ml-1",
      lot_id: "lot-1",
      model_version: "1.0.0",
      expected_quantity: 123.5,
      observed_quantity: 123.1,
      deviation_percent: -0.32,
      signal: "none",
    },
  ],
  users: [
    {
      id: "demo-user-cristhian",
      full_name: "Cristhian",
      email: DEMO_EMAIL,
      role: "admin",
      invitation_status: "active",
      status: "active",
      last_activity_at: now,
    },
    {
      id: "user-2",
      full_name: "Productor de prueba",
      email: "productor.prueba@cooperativa.org",
      role: "producer",
      invitation_status: "active",
      status: "active",
      last_activity_at: now,
    },
  ],
  notifications: [
    {
      id: "nt-1",
      title: "Modo demostración",
      body: "Sesión local sin Supabase. Los datos son simulados.",
    },
  ],
};

function paginate(items: Array<Record<string, unknown>>, path: string): PageResult<Record<string, unknown>> {
  const url = new URL(path, "http://local");
  const q = (url.searchParams.get("q") ?? "").toLowerCase();
  const status = url.searchParams.get("status") ?? "";
  const page = Number(url.searchParams.get("page") ?? 1);
  const pageSize = Number(url.searchParams.get("page_size") ?? 20);
  let filtered = items;
  if (q) {
    filtered = filtered.filter((item) => JSON.stringify(item).toLowerCase().includes(q));
  }
  if (status) {
    filtered = filtered.filter((item) => item.status === status);
  }
  const start = (page - 1) * pageSize;
  return {
    items: filtered.slice(start, start + pageSize),
    page,
    page_size: pageSize,
    total: filtered.length,
  };
}

function tableKey(pathname: string): string | null {
  const cleaned = pathname.replace("/api/v1/", "").replace(/\/$/, "");
  if (tables[cleaned]) return cleaned;
  const base = cleaned.split("/")[0];
  const aliases: Record<string, string> = {
    lots: "lots",
    custody: "custody",
    transport: "transport",
    receptions: "receptions",
    weighings: "weighings",
    "mass-balance": "mass-balance",
    alerts: "alerts",
    audits: "audits",
    users: "users",
    notifications: "notifications",
    ml: "ml/inferences",
  };
  return aliases[base] ?? null;
}

export function isDemoCredentials(email: string, password: string): boolean {
  return email.trim().toLowerCase() === DEMO_EMAIL && password === DEMO_PASSWORD;
}

export function isDemoToken(value?: string | null): boolean {
  return value === DEMO_TOKEN;
}

export function demoLoginResponse() {
  return {
    access_token: DEMO_TOKEN,
    refresh_token: DEMO_TOKEN,
    expires_in: 60 * 60 * 12,
    user: demoUser,
  };
}

export function handleDemoRequest(path: string, init: RequestInit = {}): unknown {
  const method = (init.method ?? "GET").toUpperCase();
  const [pathname] = path.split("?");

  if (pathname === "/api/v1/auth/login" && method === "POST") {
    const body = JSON.parse(String(init.body ?? "{}")) as { email?: string; password?: string };
    if (!isDemoCredentials(body.email ?? "", body.password ?? "")) {
      throw new Error("unauthorized");
    }
    return demoLoginResponse();
  }
  if (pathname === "/api/v1/auth/logout") return { ok: true };
  if (pathname === "/api/v1/auth/me") return demoUser;
  if (pathname === "/api/v1/auth/forgot-password") {
    return {
      message: "Si existe una cuenta asociada a este correo, recibirás instrucciones para recuperar el acceso.",
    };
  }
  if (pathname === "/api/v1/dashboard") {
    return {
      role: "admin",
      cards: [
        { key: "lots", label: "Lotes", value: tables.lots.length, href: "/lots" },
        { key: "transfers", label: "Transferencias", value: tables.custody.length, href: "/custody" },
        { key: "receptions", label: "Recepciones", value: tables.receptions.length, href: "/receptions" },
        { key: "alerts", label: "Alertas abiertas", value: 1, href: "/alerts" },
      ],
      recent_lots: tables.lots,
      recent_alerts: tables.alerts,
      recent_transports: tables.transport,
    };
  }
  if (pathname === "/api/v1/search") {
    const url = new URL(path, "http://local");
    const q = (url.searchParams.get("q") ?? "").toLowerCase();
    return { lots: tables.lots.filter((lot) => JSON.stringify(lot).toLowerCase().includes(q)) };
  }
  if (pathname === "/api/v1/settings") {
    return {
      settings: { general: { timezone: "America/Bogota" } },
      tolerances: [
        {
          id: "tol-1",
          name: "Tolerancia de balance de masas",
          version: 1,
          value: 3,
          unit: "percent",
          is_active: true,
          created_at: now,
        },
      ],
    };
  }
  if (pathname === "/api/v1/profile" && method === "PATCH") {
    const body = JSON.parse(String(init.body ?? "{}")) as { full_name?: string };
    if (body.full_name) demoUser.full_name = body.full_name;
    return { ...demoUser };
  }
  if (pathname.startsWith("/api/v1/ml/estimate/") && method === "POST") {
    return tables["ml/inferences"][0];
  }
  if (pathname.match(/^\/api\/v1\/mass-balance\/.+\/recalculate$/) && method === "POST") {
    return tables["mass-balance"][0];
  }
  if (pathname.match(/^\/api\/v1\/alerts\/.+\/review$/) && method === "POST") {
    const alert = tables.alerts[0];
    alert.status = "attended";
    return alert;
  }
  if (pathname.startsWith("/api/v1/users/") && method === "POST") {
    return { message: "Operación simulada correctamente." };
  }
  if (pathname === "/api/v1/users/invite" && method === "POST") {
    return { message: "Invitación enviada correctamente.", status: "pending" };
  }

  const key = tableKey(pathname);
  if (key) {
    const items = tables[key];
    const parts = pathname.replace("/api/v1/", "").split("/").filter(Boolean);
    if (parts.length >= 2 && !pathname.includes("export") && method === "GET") {
      const id = parts[parts.length - 1];
      if (id === "cases") return items[0];
      const found = items.find((item) => String(item.id) === id || String(item.lot_id) === id);
      if (found) return found;
      if (parts[0] === "lots" && parts[1]) {
        return items.find((item) => String(item.id) === parts[1]) ?? items[0];
      }
      if (parts[0] === "audits" && parts[1] === "cases") {
        return tables.lots[0];
      }
    }
    if (method === "POST") {
      const created = { id: crypto.randomUUID(), created_at: new Date().toISOString(), ...(init.body ? JSON.parse(String(init.body)) : {}) };
      items.unshift(created);
      return created;
    }
    return paginate(items, path);
  }

  return { ok: true };
}
