"use client";

import React, { useEffect, useState } from "react";
import Shell from "../lib/Shell";
import { apiFetch } from "../lib/api";

type JobRow = {
  id: string;
  user_id: string;
  status: string;
  provider: string;
  model: string;
  cost: number;
  created_at: string;
  finished_at?: string | null;
};

export default function JobsPage() {
  const [items, setItems] = useState<JobRow[]>([]);
  const [status, setStatus] = useState<string>("");
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const qs = status ? `?status=${encodeURIComponent(status)}` : "";
      const data = await apiFetch(`/v1/admin/jobs${qs}`);
      setItems(data.items || []);
    } catch (e: any) {
      setErr(e?.message || "Failed");
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <Shell title="Jobs">
      <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
        <select value={status} onChange={(e)=>setStatus(e.target.value)}
                style={{ padding: 10, borderRadius: 8, border: "1px solid #24324a", background: "#121826", color: "white" }}>
          <option value="">all</option>
          <option value="processing">processing</option>
          <option value="done">done</option>
          <option value="failed">failed</option>
        </select>
        <button onClick={load} style={{ padding: "10px 12px", borderRadius: 8, border: "none", background: "#3b82f6", color: "white", fontWeight: 600 }}>Filter</button>
      </div>

      {err && <div style={{ color: "#fb7185", marginBottom: 12, whiteSpace: "pre-wrap" }}>{err}</div>}

      <div style={{ overflowX: "auto", border: "1px solid #1f2a3d", borderRadius: 12 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#121826" }}>
              {["Status", "Cost", "Provider", "Model", "Created", "Finished", "Job ID", "User ID"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #1f2a3d", fontWeight: 700 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((j) => (
              <tr key={j.id}>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{j.status}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{j.cost}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{j.provider}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{j.model}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{j.created_at}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{j.finished_at || "-"}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d", fontFamily: "monospace", fontSize: 12 }}>{j.id}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d", fontFamily: "monospace", fontSize: 12 }}>{j.user_id}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={8} style={{ padding: 12, opacity: 0.8 }}>No jobs</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Shell>
  );
}
