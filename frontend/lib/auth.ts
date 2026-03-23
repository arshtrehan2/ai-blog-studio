import { authApi, type User } from "./api";

// ─── Token helpers (localStorage for access token) ───────────────────────────

export function saveToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", token);
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function removeToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
  }
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// ─── Auth actions ────────────────────────────────────────────────────────────

export async function login(
  email: string,
  password: string
): Promise<User> {
  const data = await authApi.login(email, password);
  saveToken(data.access_token);
  return data.user;
}

export async function signup(
  email: string,
  password: string,
  displayName: string
): Promise<User> {
  const data = await authApi.signup(email, password, displayName);
  saveToken(data.access_token);
  return data.user;
}

export async function logout(): Promise<void> {
  try {
    await authApi.logout();
  } finally {
    removeToken();
  }
}

export async function getCurrentUser(): Promise<User | null> {
  if (!isAuthenticated()) return null;
  try {
    return await authApi.me();
  } catch {
    removeToken();
    return null;
  }
}
