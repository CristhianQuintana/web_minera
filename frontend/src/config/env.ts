/**
 * Base URL del API.
 * - Desarrollo local (npm run dev): http://localhost:8000
 * - Docker + Nginx: cadena vacía → fetch relativo a /api/v1/... (mismo origen)
 *
 * No usar NEXT_PUBLIC_API_URL=/api: las rutas del cliente ya incluyen /api.
 */
function resolveApiUrl(): string {
  if (typeof process.env.NEXT_PUBLIC_API_URL === "string") {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  return "http://localhost:8000";
}

export const env = {
  apiUrl: resolveApiUrl(),
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ?? "https://oewpepqrtoezbvrxhrfe.supabase.co",
  supabaseAnonKey:
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ??
    "sb_publishable_51MkYSgxXND4Sfqzhz1smA_pke0IOJY",
};
