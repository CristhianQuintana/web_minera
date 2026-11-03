import { describe, expect, it } from "vitest";
import { parseForm, registerLotSchema, transportEventSchema } from "./resource-schemas";

describe("resource schemas", () => {
  it("acepta un lote valido", () => {
    const result = parseForm(registerLotSchema, {
      code: "LOT-1",
      mineral: "Oro",
      quantity: "12.5",
      unit: "kg",
    });
    expect(result.ok).toBe(true);
  });

  it("rechaza cantidad invalida", () => {
    const result = parseForm(registerLotSchema, {
      code: "LOT-1",
      mineral: "Oro",
      quantity: "0",
      unit: "kg",
    });
    expect(result.ok).toBe(false);
  });

  it("valida evento de transporte", () => {
    const result = parseForm(transportEventSchema, {
      event_type: "checkpoint",
      description: "Paso control",
    });
    expect(result.ok).toBe(true);
  });
});
