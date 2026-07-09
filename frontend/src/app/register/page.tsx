"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/api/auth";
import { useGuestGuard } from "@/hooks/useAuthGuard";
import { useAuthStore } from "@/store/auth";

export default function RegisterPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const { isHydrated } = useGuestGuard();
  const [form, setForm] = useState({ email: "", username: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (form.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (form.username.length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }

    setLoading(true);

    try {
      const payload = {
        email: form.email,
        username: form.username,
        password: form.password,
        ...(form.full_name.trim() ? { full_name: form.full_name.trim() } : {}),
      };
      const response = await authApi.register(payload);
      const { user, tokens } = response.data;
      login(user, tokens);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  if (!isHydrated) {
    return <div style={{ padding: 40, textAlign: "center" }}>Loading...</div>;
  }

  return (
    <div style={{ maxWidth: 400, margin: "100px auto", padding: 24, border: "1px solid #ccc", borderRadius: 8 }}>
      <h2>Register</h2>
      {error && <div data-testid="register-error" style={{ color: "red", marginBottom: 12 }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 12 }}>
          <input name="email" type="email" placeholder="Email" value={form.email} onChange={handleChange} required style={{ width: "100%", padding: 8 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <input name="username" type="text" placeholder="Username" value={form.username} onChange={handleChange} required style={{ width: "100%", padding: 8 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <input name="full_name" type="text" placeholder="Full Name (optional)" value={form.full_name} onChange={handleChange} style={{ width: "100%", padding: 8 }} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <input
            name="password"
            type="password"
            placeholder="Password (min 6 characters)"
            value={form.password}
            onChange={handleChange}
            required
            minLength={6}
            style={{ width: "100%", padding: 8 }}
          />
        </div>
        <button type="submit" disabled={loading} style={{ width: "100%", padding: 10 }}>
          {loading ? "Loading..." : "Create Account"}
        </button>
      </form>
      <p style={{ marginTop: 12, textAlign: "center" }}>
        <a href="/login">Already have an account?</a>
      </p>
    </div>
  );
}