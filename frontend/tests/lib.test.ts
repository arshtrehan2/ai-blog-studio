import { describe, it, expect, beforeEach, vi } from "vitest";
import { setToken, getToken, clearToken, isAuthenticated } from "../lib/auth";

describe("auth helpers", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("setToken stores in localStorage", () => {
    setToken("abc123");
    expect(localStorage.getItem("abs_access_token")).toBe("abc123");
  });

  it("getToken retrieves stored token", () => {
    localStorage.setItem("abs_access_token", "mytoken");
    expect(getToken()).toBe("mytoken");
  });

  it("getToken returns null when not set", () => {
    expect(getToken()).toBeNull();
  });

  it("clearToken removes the token", () => {
    setToken("to-be-cleared");
    clearToken();
    expect(getToken()).toBeNull();
  });

  it("isAuthenticated returns false when no token", () => {
    expect(isAuthenticated()).toBe(false);
  });

  it("isAuthenticated returns true when token exists", () => {
    setToken("valid-token");
    expect(isAuthenticated()).toBe(true);
  });
});
