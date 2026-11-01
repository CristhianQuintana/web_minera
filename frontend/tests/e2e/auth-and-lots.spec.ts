import { expect, type Page, test } from "@playwright/test";

const email = process.env.E2E_EMAIL ?? "";
const password = process.env.E2E_PASSWORD ?? "";
const hasRealCredentials = Boolean(email && password);

async function login(page: Page, userEmail: string, userPassword: string) {
  await page.goto("/login");
  await page.getByLabel("Correo electrónico").fill(userEmail);
  await page.locator('input[name="password"]').fill(userPassword);
  await page.getByRole("button", { name: "Ingresar" }).click();
}

test.describe("WEB_MINERA — autenticación real (Supabase)", () => {
  test("CP-W02 credenciales incorrectas no entran al panel", async ({ page }) => {
    await login(page, "no-existe@ejemplo.com", "clave-incorrecta");
    await expect(page).toHaveURL(/login/);
    await expect(page.getByText(/correo o la contraseña|sesión|iniciar sesión|completar/i)).toBeVisible();
  });

  test("CP-W01 login correcto llega al dashboard", async ({ page }) => {
    test.skip(!hasRealCredentials, "Define E2E_EMAIL y E2E_PASSWORD con un usuario real de Supabase.");
    await login(page, email, password);
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  });

  test("CP-W13 logout regresa al login", async ({ page }) => {
    test.skip(!hasRealCredentials, "Define E2E_EMAIL y E2E_PASSWORD con un usuario real de Supabase.");
    await login(page, email, password);
    await expect(page).toHaveURL(/dashboard/);
    await page.getByRole("button", { name: /Cerrar sesión/i }).first().click();
    await expect(page).toHaveURL(/login/);
  });

  test("sin sesión redirige al login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/login/);
  });
});
