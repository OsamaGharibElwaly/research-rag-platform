"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth";

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const hydrateFromStorage = useAuthStore((s) => s.hydrateFromStorage);
  const setHydrated = useAuthStore((s) => s.setHydrated);
  const setUser = useAuthStore((s) => s.setUser);
  const logout = useAuthStore((s) => s.logout);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    const hasSession = hydrateFromStorage();

    if (!hasSession) {
      setHydrated();
      return;
    }

    authApi
      .getMe()
      .then((res) => setUser(res.data.user))
      .catch(() => logout())
      .finally(() => setHydrated());
  }, [hydrateFromStorage, setHydrated, setUser, logout]);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <>
      <header
        style={{
          borderBottom: "1px solid #e5e5e5",
          padding: "12px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Link href="/" data-testid="nav-home" style={{ fontWeight: 600, textDecoration: "none", color: "inherit" }}>
          AI Research Assistant
        </Link>

        <nav style={{ display: "flex", gap: 16, alignItems: "center" }}>
          {!isHydrated ? (
            <span style={{ color: "#888" }}>Loading...</span>
          ) : isAuthenticated ? (
            <>
              <Link href="/dashboard" data-testid="nav-dashboard">Dashboard</Link>
              <Link href="/upload" data-testid="nav-upload">Upload</Link>
              <span style={{ color: "#666", fontSize: 14 }}>{user?.email}</span>
              <button
                type="button"
                data-testid="nav-logout"
                onClick={handleLogout}
                style={{ padding: "6px 12px", cursor: "pointer" }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" data-testid="nav-login">Login</Link>
              <Link href="/register" data-testid="nav-register">Register</Link>
            </>
          )}
        </nav>
      </header>
      {children}
    </>
  );
}
