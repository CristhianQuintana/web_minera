/** Violación intencional: dominio importa React. */
import { useState } from "react";

export function badHook() {
  return useState(0);
}
