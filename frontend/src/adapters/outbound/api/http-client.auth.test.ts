import { beforeEach, describe, expect, it, vi } from "vitest";

describe("http-client sesión real", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.resetModules();
  });

  it("rechaza persistir tokens demo", async () => {
    const { persistSession, ApiError } = await import("./http-client");
    expect(() => persistSession("demo-local-cristhian", "demo-local-cristhian")).toThrow(ApiError);
    expect(sessionStorage.getItem("wm_access_token")).toBeNull();
  });

  it("hasAccessToken es false para tokens demo residuales", async () => {
    sessionStorage.setItem("wm_access_token", "demo-local-cristhian");
    const { hasAccessToken } = await import("./http-client");
    expect(hasAccessToken()).toBe(false);
  });

  it("persiste tokens JWT reales", async () => {
    const { persistSession, hasAccessToken } = await import("./http-client");
    persistSession("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real", "refresh-real");
    expect(sessionStorage.getItem("wm_access_token")).toContain("eyJ");
    expect(hasAccessToken()).toBe(true);
  });
});
