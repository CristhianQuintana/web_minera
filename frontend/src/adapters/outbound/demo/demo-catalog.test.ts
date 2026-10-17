import { describe, expect, it } from "vitest";
import {
  demoLoginResponse,
  handleDemoRequest,
  isDemoCredentials,
} from "./demo-catalog";

describe("acceso de demostración", () => {
  it("acepta las credenciales locales de demostración", () => {
    expect(isDemoCredentials("cristhian@gmail.com", "Cristhian123")).toBe(true);
    expect(isDemoCredentials("otro@gmail.com", "Cristhian123")).toBe(false);
    expect(demoLoginResponse().user.role).toBe("admin");
  });

  it("inicia sesión y entrega token de demostración", () => {
    const result = handleDemoRequest("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "cristhian@gmail.com", password: "Cristhian123" }),
    }) as { access_token: string; user: { permissions: string[] } };
    expect(result.access_token).toBe("demo-local-cristhian");
    expect(result.user.permissions).toContain("view_lots");
  });

  it("consulta el dashboard simulado", () => {
    const dashboard = handleDemoRequest("/api/v1/dashboard") as {
      cards: Array<{ label: string }>;
      recent_lots: Array<{ code: string }>;
    };
    expect(dashboard.cards.length).toBe(4);
    expect(dashboard.recent_lots[0].code).toBe("LOT-2026-00021");
  });

  it("lista lotes y permite abrir el detalle", () => {
    const list = handleDemoRequest("/api/v1/lots?page=1&page_size=20") as {
      items: Array<{ id: string }>;
      total: number;
    };
    expect(list.total).toBeGreaterThan(0);
    const detail = handleDemoRequest("/api/v1/lots/lot-1") as { code: string };
    expect(detail.code).toBe("LOT-2026-00021");
  });

  it("registra la revisión de una alerta", () => {
    const reviewed = handleDemoRequest("/api/v1/alerts/al-1/review", {
      method: "POST",
      body: JSON.stringify({ result: "Dentro de tolerancia operativa", observation: "Revisado" }),
    }) as { status: string };
    expect(reviewed.status).toBe("attended");
  });
});
