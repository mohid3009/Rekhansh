import { ReactNode } from "react";
import { STATE_STYLE, TriageState } from "../api";

export function fmtNum(v: number | null | undefined, digits = 2, unit = ""): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return `${v.toFixed(digits)}${unit ? ` ${unit}` : ""}`;
}

export function fmtPct(v: number | null | undefined): string {
  return v === null || v === undefined ? "—" : `${v.toFixed(1)}%`;
}

export function StateBadge({ state }: { state: TriageState | null }) {
  if (!state) return <span className="text-slate-400 text-xs">n/a</span>;
  const s = STATE_STYLE[state];
  return (
    <span
      className="inline-block rounded px-2 py-0.5 text-[11px] font-bold tracking-wide text-white whitespace-nowrap"
      style={{ backgroundColor: s.color }}
      data-testid="state-badge"
    >
      {s.label}
    </span>
  );
}

export function VerifyBadge({ status }: { status: string }) {
  const style: Record<string, string> = {
    UNVERIFIED: "bg-slate-200 text-slate-600",
    CONFIRMED: "bg-emerald-100 text-emerald-700",
    CORRECTED: "bg-blue-100 text-blue-700",
    ESCALATED: "bg-purple-100 text-purple-700",
  };
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-[11px] font-semibold ${style[status] ?? "bg-slate-100 text-slate-600"}`}>
      {status}
    </span>
  );
}

export function Banner({ kind, children }: { kind: "prototype" | "info" | "error" | "success"; children: ReactNode }) {
  const cls = {
    prototype: "prototype-banner text-amber-900 border-amber-400",
    info: "bg-sky-50 text-sky-800 border-sky-200",
    error: "bg-red-50 text-red-800 border-red-300",
    success: "bg-emerald-50 text-emerald-800 border-emerald-300",
  }[kind];
  return <div className={`border rounded px-3 py-2 text-sm ${cls}`}>{children}</div>;
}

export function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-slate-500 text-sm py-8 justify-center">
      <span className="inline-block w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
      {label}
    </div>
  );
}

export function Metric({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <div className="bg-white border border-slate-200 rounded p-3" title={hint}>
      <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className="text-lg font-semibold text-slate-800">{value}</div>
    </div>
  );
}

export function PassFail({ pass }: { pass: boolean }) {
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-[11px] font-bold ${pass ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}
    >
      {pass ? "PASS" : "FAIL"}
    </span>
  );
}

export const CHECK_LABELS: Record<string, string> = {
  area_diff_pct: "Area deviation vs observed (%)",
  boundary_displacement_m: "Boundary displacement ASBD (m)",
  support_ratio_pct: "Support ratio (% of perimeter)",
  occlusion_fraction: "Occlusion fraction (imagery)",
  ai_confidence: "AI confidence",
  uncertainty_score: "Uncertainty score",
  topology_status: "Topology (neighbour overlap)",
};
