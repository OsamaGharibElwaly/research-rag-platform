"use client";

import Link from "next/link";
import { useAuthGuard } from "@/hooks/useAuthGuard";
import { useAuthStore } from "@/store/auth";

const cardStyle: React.CSSProperties = {
  border: "1px solid #e5e5e5",
  borderRadius: 12,
  padding: 20,
  background: "#fafafa",
};

export default function DashboardPage() {
  const { isReady } = useAuthGuard();
  const user = useAuthStore((s) => s.user);

  if (!isReady || !user) {
    return <div style={{ padding: 40, textAlign: "center" }}>Loading...</div>;
  }

  const memberSince = new Date(user.created_at).toLocaleDateString();

  return (
    <div style={{ maxWidth: 960, margin: "40px auto", padding: 24 }}>
      <h1 style={{ marginBottom: 8 }}>Dashboard</h1>
      <p style={{ color: "#666", marginBottom: 32 }}>
        Welcome, {user.full_name || user.username}
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 16,
          marginBottom: 24,
        }}
      >
        <div style={cardStyle} data-testid="card-profile">
          <h3 style={{ marginTop: 0 }}>Your Account</h3>
          <p style={{ margin: "8px 0", color: "#444" }}><strong>Username:</strong> {user.username}</p>
          <p style={{ margin: "8px 0", color: "#444" }}><strong>Email:</strong> {user.email}</p>
          <p style={{ margin: "8px 0", color: "#444" }}><strong>Member since:</strong> {memberSince}</p>
          <p style={{ margin: "8px 0", color: "#444" }}>
            <strong>Status:</strong> {user.is_active ? "Active" : "Inactive"}
          </p>
        </div>

        <Link href="/upload" style={{ textDecoration: "none", color: "inherit" }}>
          <div style={cardStyle} data-testid="card-upload">
            <h3 style={{ marginTop: 0 }}>Upload Papers</h3>
            <p style={{ color: "#666", margin: 0 }}>
              Add PDF research papers to your personal library.
            </p>
          </div>
        </Link>

        <div style={cardStyle} data-testid="card-library">
          <h3 style={{ marginTop: 0 }}>Paper Library</h3>
          <p style={{ color: "#666", margin: 0 }}>
            View and manage all uploaded research papers.
          </p>
          <Link href="/upload" style={{ display: "inline-block", marginTop: 12 }}>
            Open library
          </Link>
        </div>

        <div style={{ ...cardStyle, opacity: 0.7 }} data-testid="card-chat">
          <h3 style={{ marginTop: 0 }}>Chat with AI</h3>
          <p style={{ color: "#666", margin: 0 }}>
            Ask questions about your papers. Coming soon.
          </p>
        </div>

        <div style={{ ...cardStyle, opacity: 0.7 }} data-testid="card-reports">
          <h3 style={{ marginTop: 0 }}>Generate Reports</h3>
          <p style={{ color: "#666", margin: 0 }}>
            Summaries, quizzes, and citations. Coming soon.
          </p>
        </div>
      </div>
    </div>
  );
}
