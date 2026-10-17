import { describe, expect, it } from "vitest";
import { toneFor } from "./ui";

describe("toneFor", () => {
  it("asigna tono de éxito a estados concluidos", () => {
    expect(toneFor("within_tolerance")).toBe("success");
    expect(toneFor("attended")).toBe("success");
  });

  it("asigna tono de advertencia a alertas abiertas", () => {
    expect(toneFor("new")).toBe("warning");
    expect(toneFor("review_required")).toBe("warning");
  });

  it("asigna tono de error a estados críticos", () => {
    expect(toneFor("inactive")).toBe("error");
    expect(toneFor("high")).toBe("error");
  });
});
