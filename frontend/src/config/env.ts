/**
 * Base URL del API.
 * - Desarrollo local (npm run dev): http://localhost:8000 si no se define env
 * - Docker + Nginx: cadena vacía → fetch relativo a /api/v1/... (mismo origen)
 * - Render: URL absoluta pública del backend, p. ej. https://web-minera-backend.onrender.com
 *
 * No usar NEXT_PUBLIC_API_URL=/api: las rutas del cliente ya incluyen /api.
 */
function resolveApiUrl(): string {
  if (typeof process.env.NEXT_PUBLIC_API_URL === "string") {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (process.env.NODE_ENV === "production") {
    return "";
  }
  return "http://localhost:8000";
}

export const env = {
  apiUrl: resolveApiUrl(),
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
  supabaseAnonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
};
