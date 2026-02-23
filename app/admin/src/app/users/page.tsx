"use client";

import React, { useEffect, useMemo, useState } from "react";
import Shell from "../lib/Shell";
import { apiFetch } from "../lib/api";

type UserRow = {
  id: string;
  telegram_id: number;
  username?: string | null;
  first_name?: string | null;
  role: string;
  is_banned: boolean;
  balance: number;
};

export default function UsersPage() {
  const [items, setItems] = useState<UserRow[]>([]);
  const [search, setSearch] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const qs = search ? `?search=${encodeURIComponent(search)}` : "";
      const data = await apiFetch(`/v1/admin/users${qs}`);
      setItems(data.items || []);
    } catch (e: any) {
      setErr(e?.message || "Failed");
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <Shell title="Users">
      <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
        <input value={search} onChange={(e)=>setSearch(e.target.value)} placeholder="Search telegram_id / username / first name"
               style={{ flex: 1, padding: 10, borderRadius: 8, border: "1px solid #24324a", background: "#121826", color: "white" }} />
        <button onClick={load} style={{ padding: "10px 12px", borderRadius: 8, border: "none", background: "#3b82f6", color: "white", fontWeight: 600 }}>Search</button>
      </div>

      {err && <div style={{ color: "#fb7185", marginBottom: 12, whiteSpace: "pre-wrap" }}>{err}</div>}

      <div style={{ overflowX: "auto", border: "1px solid #1f2a3d", borderRadius: 12 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#121826" }}>
              {["Telegram", "Username", "Name", "Role", "Banned", "Balance", "User ID"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #1f2a3d", fontWeight: 700 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((u) => (
              <tr key={u.id}>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{u.telegram_id}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{u.username || "-"}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{u.first_name || "-"}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{u.role}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{u.is_banned ? "yes" : "no"}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{u.balance}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d", fontFamily: "monospace", fontSize: 12 }}>{u.id}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={7} style={{ padding: 12, opacity: 0.8 }}>No users</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Shell>
  );
}
