"use client";
import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getToken, clearToken } from "./api";

export default function Shell({ title, children }: { title: string; children: React.ReactNode }) {
  const r = useRouter();
  useEffect(() => {
    const t = getToken();
    if (!t) r.replace("/login");
  }, [r]);

  return (
    <div style={{ minHeight: "100vh", background: "#0b0f14", color: "white" }}>
      <div style={{ display: "flex", gap: 16, padding: "14px 18px", borderBottom: "1px solid #1f2a3d", alignItems: "center" }}>
        <strong style={{ marginRight: 10 }}>GenieHub</strong>
        <Link href="/dashboard" style={{ color: "white", textDecoration: "none" }}>Dashboard</Link>
        <Link href="/users" style={{ color: "white", textDecoration: "none" }}>Users</Link>
        <Link href="/jobs" style={{ color: "white", textDecoration: "none" }}>Jobs</Link>
        <Link href="/payments" style={{ color: "white", textDecoration: "none" }}>Payments</Link>
        <div style={{ flex: 1 }} />
        <button
          onClick={() => { clearToken(); r.replace("/login"); }}
          style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #24324a", background: "#121826", color: "white" }}
        >
          Logout
        </button>
      </div>
      <div style={{ padding: 18, maxWidth: 1200, margin: "0 auto" }}>
        <h1 style={{ marginTop: 0 }}>{title}</h1>
        {children}
      </div>
    </div>
  );
}
