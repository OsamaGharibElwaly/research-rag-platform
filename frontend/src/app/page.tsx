"use client";

import Link from "next/link";
import { useAuthStore } from "@/store/auth";

export default function HomePage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const user = useAuthStore((s) => s.user);

  return (
    <div style={{ maxWidth: 720, margin: "80px auto", padding: 24 }}>
      <h1>AI Research Paper Assistant</h1>
      <p>Upload PDF research papers, manage your library, and prepare for AI-powered analysis.</p>

      {isHydrated && isAuthenticated && user && (
        <p style={{ marginTop: 16, color: "#444" }}>
          Welcome back, {user.full_name || user.username}.
        </p>
      )}

      <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
        {isHydrated && isAuthenticated ? (
          <>
            <Link href="/dashboard" data-testid="home-dashboard-link">Go to Dashboard</Link>
            <Link href="/upload" data-testid="home-upload-link">Upload Papers</Link>
          </>
        ) : (
          <>
            <Link href="/login" data-testid="home-login-link">Login</Link>
            <Link href="/register" data-testid="home-register-link">Register</Link>
          </>
        )}
      </div>
    </div>
  );
}
