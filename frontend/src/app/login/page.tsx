"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/api/auth";
import { useGuestGuard } from "@/hooks/useAuthGuard";
import { useAuthStore } from "@/store/auth";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const { isHydrated } = useGuestGuard();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await authApi.login({ email, password });
      const { user, tokens } = response.data;
      login(user, tokens);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  if (!isHydrated) {
    return <div style={{ padding: 40, textAlign: "center" }}>Loading...</div>;
  }

  return (
    <div style={{ maxWidth: 400, margin: "100px auto", padding: 24, border: "1px solid #ccc", borderRadius: 8 }}>
      <h2>Login</h2>
      {error && <div data-testid="login-error" style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 12 }}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%", padding: 8 }}
          />
        </div>
        <div style={{ marginBottom: 12 }}>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: 8 }}
          />
        </div>
        <button type="submit" disabled={loading} style={{ width: "100%", padding: 10 }}>
          {loading ? "Loading..." : "Sign In"}
        </button>
      </form>
      <p style={{ marginTop: 12, textAlign: "center" }}>
        <a href="/register">Create account</a>
      </p>
    </div>
  );
}