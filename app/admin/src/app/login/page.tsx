"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, setToken } from "../lib/api";

export default function LoginPage() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const r = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const data = await apiFetch("/v1/admin/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
        headers: {}
      });
      setToken(data.access_token);
      r.replace("/dashboard");
    } catch (e: any) {
      setErr(e?.message || "Login failed");
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#0b0f14", color: "white" }}>
      <form onSubmit={onSubmit} style={{ width: 360, padding: 24, background: "#121826", borderRadius: 12 }}>
        <h1 style={{ marginTop: 0 }}>GenieHub Admin</h1>
        <div style={{ display: "grid", gap: 10 }}>
          <label style={{ display: "grid", gap: 6 }}>
            <span>Username</span>
            <input value={username} onChange={(e) => setUsername(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #24324a", background: "#0b0f14", color: "white" }} />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span>Password</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #24324a", background: "#0b0f14", color: "white" }} />
          </label>
          <button style={{ padding: 10, borderRadius: 8, border: "none", background: "#3b82f6", color: "white", fontWeight: 600 }}>Login</button>
          {err && <div style={{ color: "#fb7185", whiteSpace: "pre-wrap" }}>{err}</div>}
        </div>
      </form>
    </div>
  );
}
