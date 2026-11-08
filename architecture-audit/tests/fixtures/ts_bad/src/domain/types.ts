/** Violación intencional: dominio importa React (fixture de prueba de reglas). */
import { useState } from "react";

/** Nombre con prefijo use* para cumplir la regla de Hooks; el defecto real es el import en domain. */
export function useBadFixtureState() {
  return useState(0);
}
