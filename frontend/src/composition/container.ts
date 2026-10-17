/**
 * Composition root del frontend.
 * Único lugar que conecta puertos con adaptadores concretos.
 */
import { platformAdapter } from "@/adapters/outbound/api/platform-adapter";
import { createAuthUseCases } from "@/application/use-cases/auth";
import type { PlatformPort } from "@/ports/outbound/platform-port";

export const platform: PlatformPort = platformAdapter;

export const auth = createAuthUseCases(platform);

/** Compatibilidad con imports previos de casos de uso. */
export const loginUseCase = auth.login;
export const logoutUseCase = auth.logout;
export const getCurrentUserUseCase = auth.me;
export const forgotPasswordUseCase = auth.forgotPassword;
export const activateAccountUseCase = auth.activate;
export const validateInvitationUseCase = auth.validateActivation;
