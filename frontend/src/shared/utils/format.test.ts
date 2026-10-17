import { describe, expect, it } from "vitest";
import { cn, formatDate, formatQuantity, labelOf } from "./format";

describe("formatQuantity", () => {
  it("siempre incluye la unidad", () => {
    expect(formatQuantity(125.4, "kg")).toContain("kg");
  });

  it("muestra em dash cuando no hay valor", () => {
    expect(formatQuantity(null, "kg")).toBe("—");
  });
});

describe("formatDate", () => {
  it("devuelve em dash si la fecha es inválida", () => {
    expect(formatDate("no-es-fecha")).toBe("—");
    expect(formatDate(null)).toBe("—");
  });

  it("formatea una fecha ISO en formato colombiano", () => {
    expect(formatDate("2026-09-24T15:20:00.000Z")).toMatch(/24\/09\/2026/);
  });
});

describe("labelOf", () => {
  it("traduce estados de dominio a etiquetas de UI", () => {
    expect(labelOf("registered")).toBe("Registrado");
    expect(labelOf("review_required")).toBe("Revisión requerida");
    expect(labelOf(null)).toBe("—");
  });
});

describe("cn", () => {
  it("omite valores nulos o falsos", () => {
    expect(cn("a", false, undefined, "b")).toBe("a b");
  });
});
