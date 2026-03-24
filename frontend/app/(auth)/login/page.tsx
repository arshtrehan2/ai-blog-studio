"use client";
import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authAPI } from "@/lib/api";
import { setToken, setStoredUser } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await authAPI.login({ email, password });
      setToken(data.access_token);
      setStoredUser({ id: data.user.id, email: data.user.email, display_name: data.user.display_name });
      router.push("/");
    } catch {
      setError("Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "80px auto", padding: "0 24px" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Sign in</h1>
      <p style={{ color: "var(--color-text-muted)", marginBottom: 32 }}>Welcome back to AI Blog Studio</p>
      <form onSubmit={handleSubmit}>
        {error && <div role="alert" style={{ padding: "12px 16px", background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 6, color: "var(--color-error)", marginBottom: 16, fontSize: 14 }}>{error}</div>}
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="email" style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>Email</label>
          <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} required autoComplete="email"
            style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 16 }} />
        </div>
        <div style={{ marginBottom: 24 }}>
          <label htmlFor="password" style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>Password</label>
          <input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} required
            style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 16 }} />
        </div>
        <button type="submit" disabled={loading}
          style={{ width: "100%", padding: 12, background: loading ? "#93c5fd" : "var(--color-primary)", color: "white", border: "none", borderRadius: 6, fontSize: 16, fontWeight: 600 }}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
      <p style={{ marginTop: 24, textAlign: "center", color: "var(--color-text-muted)" }}>
        Don&apos;t have an account? <Link href="/signup">Sign up</Link>
      </p>
    </div>
  );
}
