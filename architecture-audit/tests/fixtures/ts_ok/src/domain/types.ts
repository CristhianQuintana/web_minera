/** Dominio limpio: sin React/Next. */
export type Estimate = { expected_quantity: number; model_version: string };

export function label(v: number): string {
  return `qty:${v}`;
}
