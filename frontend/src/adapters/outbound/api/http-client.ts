import {
  handleDemoRequest,
  isDemoCredentials,
  isDemoToken,
} from "@/adapters/outbound/demo/demo-catalog";
import { env } from "@/config/env";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}

const messages: Record<number, string> = {
  400: "Revisa la información ingresada.",
  401: "El correo o la contraseña no son correctos.",
  403: "No tienes permisos para realizar esta acción.",
  404: "El recurso solicitado no existe o ya no está disponible.",
  409: "Este registro fue actualizado por otro usuario.",
  422: "No pudimos validar la información enviada.",
  429: "Has realizado demasiadas solicitudes. Intenta más tarde.",
  500: "No pudimos completar la solicitud.",
  503: "El servicio no está disponible en este momento.",
};

function token(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem("wm_access_token");
}

export function persistSession(access?: string, refresh?: string) {
  if (access) sessionStorage.setItem("wm_access_token", access);
  if (refresh) sessionStorage.setItem("wm_refresh_token", refresh);
}

export function clearSession() {
  sessionStorage.removeItem("wm_access_token");
  sessionStorage.removeItem("wm_refresh_token");
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (shouldUseDemo(path, init)) {
    try {
      return handleDemoRequest(path, init) as T;
    } catch {
      throw new ApiError(401, "unauthorized", "El correo o la contraseña no son correctos.");
    }
  }

  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const auth = token();
  if (auth) headers.set("Authorization", `Bearer ${auth}`);

  let response: Response;
  try {
    response = await fetch(`${env.apiUrl}${path}`, {
      ...init,
      headers,
      credentials: "include",
    });
  } catch {
    throw new ApiError(0, "offline", "No hay conexión con el servidor.");
  }

  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const error = payload?.error;
    throw new ApiError(
      response.status,
      error?.code ?? "http_error",
      error?.message ?? messages[response.status] ?? "No pudimos completar la solicitud.",
    );
  }
  return payload as T;
}

function shouldUseDemo(path: string, init: RequestInit): boolean {
  if (isDemoToken(token())) return true;
  if (path === "/api/v1/auth/login") {
    try {
      const body = JSON.parse(String(init.body ?? "{}")) as { email?: string; password?: string };
      return isDemoCredentials(body.email ?? "", body.password ?? "");
    } catch {
      return false;
    }
  }
  return false;
}
