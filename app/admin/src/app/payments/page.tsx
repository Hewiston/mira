"use client";

import React, { useEffect, useState } from "react";
import Shell from "../lib/Shell";
import { apiFetch } from "../lib/api";

type PaymentRow = {
  id: string;
  user_id: string;
  provider: string;
  status: string;
  currency: string;
  stars_amount: number;
  coins_amount: number;
  charge_id?: string | null;
  created_at: string;
  paid_at?: string | null;
};

export default function PaymentsPage() {
  const [items, setItems] = useState<PaymentRow[]>([]);
  const [status, setStatus] = useState<string>("");
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const qs = status ? `?status=${encodeURIComponent(status)}` : "";
      const data = await apiFetch(`/v1/admin/payments${qs}`);
      setItems(data.items || []);
    } catch (e: any) {
      setErr(e?.message || "Failed");
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <Shell title="Payments">
      <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
        <input value={status} onChange={(e)=>setStatus(e.target.value)} placeholder="status (paid/pending/failed)"
               style={{ flex: 1, padding: 10, borderRadius: 8, border: "1px solid #24324a", background: "#121826", color: "white" }} />
        <button onClick={load} style={{ padding: "10px 12px", borderRadius: 8, border: "none", background: "#3b82f6", color: "white", fontWeight: 600 }}>Filter</button>
      </div>

      {err && <div style={{ color: "#fb7185", marginBottom: 12, whiteSpace: "pre-wrap" }}>{err}</div>}

      <div style={{ overflowX: "auto", border: "1px solid #1f2a3d", borderRadius: 12 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#121826" }}>
              {["Status", "Stars", "Coins", "Currency", "Provider", "Charge ID", "Created", "Paid", "Payment ID", "User ID"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #1f2a3d", fontWeight: 700 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id}>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{p.status}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{p.stars_amount}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{p.coins_amount}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{p.currency}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{p.provider}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d", fontFamily: "monospace", fontSize: 12 }}>{p.charge_id || "-"}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{p.created_at}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d" }}>{p.paid_at || "-"}</td>
                <td style={{ padding: 10, borderBottom: "1f2a3d", fontFamily: "monospace", fontSize: 12 }}>{p.id}</td>
                <td style={{ padding: 10, borderBottom: "1px solid #1f2a3d", fontFamily: "monospace", fontSize: 12 }}>{p.user_id}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={10} style={{ padding: 12, opacity: 0.8 }}>No payments</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Shell>
  );
}
