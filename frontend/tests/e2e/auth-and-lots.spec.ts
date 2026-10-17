import { expect, type Page, test } from "@playwright/test";

async function login(page: Page, password = "Cristhian123") {
  await page.goto("/login");
  await page.getByLabel("Correo electrónico").fill("cristhian@gmail.com");
  await page.locator('input[name="password"]').fill(password);
  await page.getByRole("button", { name: "Ingresar" }).click();
}

test.describe("WEB_MINERA — flujos E2E de demostración", () => {
  test("CP-W01 login correcto llega al dashboard", async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Lotes", exact: true })).toBeVisible();
  });

  test("CP-W02 credenciales incorrectas no entran al panel", async ({ page }) => {
    await login(page, "clave-incorrecta");
    await expect(page).toHaveURL(/login/);
  });

  test("CP-W07 consulta de lotes y drawer de detalle", async ({ page }) => {
    await login(page);
    await page.goto("/lots");
    await expect(page.getByRole("heading", { name: "Lotes" })).toBeVisible();
    await expect(page.getByText("LOT-2026-00021")).toBeVisible();
    await page.getByRole("button", { name: "Detalle" }).first().click();
    await expect(page.getByRole("heading", { name: "Detalle del lote" })).toBeVisible();
    await expect(page.getByText("LOT-2026-00021").first()).toBeVisible();
  });

  test("CP-W13 logout regresa al login", async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/dashboard/);
    await page.getByRole("button", { name: /Cerrar sesión/i }).first().click();
    await expect(page).toHaveURL(/login/);
  });
});
