import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("PMV2 — flujos publicos", () => {
  test("CP-WEB-RF01-02 credenciales invalidas", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Correo electrónico").fill("no-existe@ejemplo.com");
    await page.locator('input[name="password"]').fill("clave-incorrecta");
    await page.getByRole("button", { name: "Ingresar" }).click();
    await expect(page).toHaveURL(/login/);
  });

  test("ruta protegida sin sesion redirige a login", async ({ page }) => {
    await page.goto("/lots");
    await expect(page).toHaveURL(/login/);
  });

  test("AXE-login sin violaciones criticas/serias", async ({ page }) => {
    await page.goto("/login");
    const results = await new AxeBuilder({ page }).analyze();
    const blocking = results.violations.filter((v) => ["critical", "serious"].includes(v.impact || ""));
    // Persist summary for audit package via console for playwright report
    console.log("AXE_VIOLATIONS", JSON.stringify(results.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length }))));
    expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
  });
});
