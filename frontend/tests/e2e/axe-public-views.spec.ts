import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";

const outDir = path.resolve(
  __dirname,
  "../../../audit/AUDITORIA_WEB_MINERA_S11/14_ENTREGA_COMPLEMENTARIA/axe",
);

async function runAxe(page: import("@playwright/test").Page, route: string, file: string) {
  await page.goto(route);
  const results = await new AxeBuilder({ page }).analyze();
  const blocking = results.violations.filter((v) => ["critical", "serious"].includes(v.impact || ""));
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(
    path.join(outDir, file),
    JSON.stringify(
      {
        route,
        url: page.url(),
        timestamp: new Date().toISOString(),
        blockingCount: blocking.length,
        violations: results.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          description: v.description,
          helpUrl: v.helpUrl,
          nodes: v.nodes.length,
        })),
      },
      null,
      2,
    ),
    "utf-8",
  );
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
}

test.describe("Axe — vistas publicas S11 complemento", () => {
  test("AXE /login", async ({ page }) => {
    await runAxe(page, "/login", "axe_login.json");
  });

  test("AXE /forgot-password", async ({ page }) => {
    await runAxe(page, "/forgot-password", "axe_forgot_password.json");
  });

  test("AXE /activate-account", async ({ page }) => {
    await runAxe(page, "/activate-account", "axe_activate_account.json");
  });

  test("AXE /forbidden", async ({ page }) => {
    await runAxe(page, "/forbidden", "axe_forbidden.json");
  });

  test("AXE ruta protegida sin sesion termina en login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/login/);
    // No acredita accesibilidad de dashboard autenticado.
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(
      path.join(outDir, "axe_dashboard_AUTH_PENDIENTE.txt"),
      "Dashboard autenticado: NO EJECUTADO — requiere E2E_EMAIL/E2E_PASSWORD.\nSolo se verifico redirect a /login sin sesion.\n",
      "utf-8",
    );
  });
});
