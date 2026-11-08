import type { Estimate } from "../domain/types";

export function toEstimate(n: number): Estimate {
  return { expected_quantity: n, model_version: "1.0.0" };
}
