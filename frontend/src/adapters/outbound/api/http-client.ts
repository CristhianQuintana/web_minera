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

function refreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem("wm_refresh_token");
}

export function persistSession(access?: string, refresh?: string) {
  if (access) {
    if (access.startsWith("demo-")) {
      throw new ApiError(401, "unauthorized", "Token de sesión no válido.");
    }
    sessionStorage.setItem("wm_access_token", access);
  }
  if (refresh) {
    if (refresh.startsWith("demo-")) {
      throw new ApiError(401, "unauthorized", "Token de sesión no válido.");
    }
    sessionStorage.setItem("wm_refresh_token", refresh);
  }
}

export function clearSession() {
  sessionStorage.removeItem("wm_access_token");
  sessionStorage.removeItem("wm_refresh_token");
}

export function hasAccessToken(): boolean {
  const value = token();
  return Boolean(value && !value.startsWith("demo-"));
}

let refreshInFlight: Promise<boolean> | null = null;

async function tryRefreshSession(): Promise<boolean> {
  const currentRefresh = refreshToken();
  if (!currentRefresh || currentRefresh.startsWith("demo-")) {
    clearSession();
    return false;
  }
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    try {
      const response = await fetch(`${env.apiUrl}/api/v1/auth/refresh`, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ refresh_token: currentRefresh }),
      });
      if (!response.ok) {
        clearSession();
        return false;
      }
      const payload = (await response.json()) as {
        access_token?: string;
        refresh_token?: string;
      };
      if (!payload.access_token || payload.access_token.startsWith("demo-")) {
        clearSession();
        return false;
      }
      persistSession(payload.access_token, payload.refresh_token);
      return true;
    } catch {
      clearSession();
      return false;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

export async function api<T>(path: string, init: RequestInit = {}, retried = false): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const auth = token();
  if (auth) {
    if (auth.startsWith("demo-")) {
      clearSession();
      throw new ApiError(401, "unauthorized", "Tu sesión ha expirado. Vuelve a iniciar sesión.");
    }
    headers.set("Authorization", `Bearer ${auth}`);
  }

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

  if (response.status === 401 && !retried && !path.includes("/auth/login") && !path.includes("/auth/refresh")) {
    const renewed = await tryRefreshSession();
    if (renewed) {
      return api<T>(path, init, true);
    }
  }

  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    if (response.status === 401) {
      clearSession();
    }
    const error = payload?.error;
    throw new ApiError(
      response.status,
      error?.code ?? "http_error",
      error?.message ?? messages[response.status] ?? "No pudimos completar la solicitud.",
    );
  }
  return payload as T;
}
