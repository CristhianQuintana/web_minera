import { api, clearSession, persistSession } from "@/adapters/outbound/api/http-client";
import type { CurrentUser, PageResult } from "@/domain/entities";
import type { ListQuery, PlatformPort } from "@/ports/outbound/platform-port";

function qs(query?: ListQuery): string {
  if (!query) return "";
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value));
  });
  const encoded = params.toString();
  return encoded ? `?${encoded}` : "";
}

export const platformAdapter: PlatformPort = {
  async login(email, password) {
    const result = await api<{ user: CurrentUser; access_token: string; refresh_token: string }>(
      "/api/v1/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) },
    );
    persistSession(result.access_token, result.refresh_token);
    return result;
  },
  async logout() {
    try {
      await api("/api/v1/auth/logout", { method: "POST" });
    } finally {
      clearSession();
    }
  },
  me: () => api<CurrentUser>("/api/v1/auth/me"),
  forgotPassword: (email) =>
    api("/api/v1/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),
  validateActivation: (token) => api(`/api/v1/auth/activate?token=${encodeURIComponent(token)}`),
  activate: (payload) =>
    api("/api/v1/auth/activate", { method: "POST", body: JSON.stringify(payload) }),
  dashboard: () => api("/api/v1/dashboard"),
  list: <T>(path: string, query?: ListQuery) => api<PageResult<T>>(`${path}${qs(query)}`),
  get: <T>(path: string) => api<T>(path),
  post: <T>(path: string, body?: unknown) =>
    api<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  search: (q: string) => api(`/api/v1/search?q=${encodeURIComponent(q)}`),
};
