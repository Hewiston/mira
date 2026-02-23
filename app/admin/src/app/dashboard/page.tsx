"use client";
import React from "react";
import Shell from "../lib/Shell";

export default function Dashboard() {
  return (
    <Shell title="Dashboard">
      <div style={{ opacity: 0.85 }}>
        MVP: подключим метрики (DAU/WAU/MAU, success/failed, avg latency, revenue) на следующей итерации.
      </div>
    </Shell>
  );
}
