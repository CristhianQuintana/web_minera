import { describe, expect, it } from "vitest";
import { loginSchema } from "./login-schema";

describe("loginSchema", () => {
  it("acepta un correo y contraseña válidos", () => {
    const result = loginSchema.safeParse({
      email: "cristhian@gmail.com",
      password: "Cristhian123",
    });
    expect(result.success).toBe(true);
  });

  it("rechaza un correo con formato inválido", () => {
    const result = loginSchema.safeParse({
      email: "correo-invalido",
      password: "Cristhian123",
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe("Formato de correo no válido.");
    }
  });

  it("rechaza una contraseña demasiado corta", () => {
    const result = loginSchema.safeParse({
      email: "cristhian@gmail.com",
      password: "123",
    });
    expect(result.success).toBe(false);
  });
});
