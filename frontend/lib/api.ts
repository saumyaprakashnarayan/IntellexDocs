/**
 * frontend/lib/api.ts
 * ====================
 * Central fetch wrapper that every page component uses to call the backend.
 *
 * Centralising the base URL here means the entire frontend switches backends
 * by changing one environment variable (NEXT_PUBLIC_API_URL) — no grep-and-replace.
 *
 * Next.js inlines NEXT_PUBLIC_ variables into the browser bundle at build time,
 * so the value must be known when `npm run build` runs, not just at runtime.
 * This is why docker-compose passes it as a build ARG to the frontend image.
 */

/** Resolved at build time from the environment; falls back to local dev default */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Wraps the native fetch API with two automatic behaviours:
 *   1. Prepends API_BASE_URL so callers only write the path (e.g. "/auth/login")
 *   2. Attaches the JWT Bearer token from localStorage when one is present
 *
 * Content-Type is set to application/json for all bodies except FormData,
 * because setting it on FormData would override the browser-generated
 * multipart boundary and break file uploads.
 */
export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  // localStorage is only available in the browser; typeof window guards against
  // calling it during Next.js server-side rendering where window is undefined
  const token =
    typeof window !== "undefined" ? localStorage.getItem("rag_token") : null;

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  // Every protected endpoint requires this header; attaching it here removes
  // the boilerplate from every individual page component
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // FormData sets its own Content-Type with the multipart boundary embedded;
  // forcing application/json on it would produce a malformed request
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
}
