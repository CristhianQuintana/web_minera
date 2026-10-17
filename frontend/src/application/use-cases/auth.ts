import type { PlatformPort } from "@/ports/outbound/platform-port";

/**
 * Fábricas de casos de uso de autenticación.
 * Dependen del puerto outbound, nunca del adaptador HTTP concreto.
 */
export function createAuthUseCases(platform: PlatformPort) {
  return {
    login: (email: string, password: string) => platform.login(email, password),
    logout: () => platform.logout(),
    me: () => platform.me(),
    forgotPassword: (email: string) => platform.forgotPassword(email),
    activate: platform.activate.bind(platform),
    validateActivation: platform.validateActivation.bind(platform),
  };
}

export type AuthUseCases = ReturnType<typeof createAuthUseCases>;
