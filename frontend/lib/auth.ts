/**
 * JWT helpers for client-side token management.
 * Access token: localStorage (short TTL, 15 min).
 * Refresh token: httpOnly cookie (managed server-side).
 */

const TOKEN_KEY = "abs_access_token";

export function setToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}
