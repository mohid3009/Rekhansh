import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  Bar,
  BarChart,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip as RTooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, EvidencePayload } from "../api";
import { Banner, CHECK_LABELS, PassFail, Spinner, StateBadge } from "../components/ui";

export default function EvidenceScreen() {
  const { id } = useParams();
  const [data, setData] = useState<EvidencePayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setData(null);
    setError(null);
    api
      .get<EvidencePayload>(`/api/parcels/${id}/evidence`)
      .then(setData)
      .catch((e) => setError(String(e)));
  }, [id]);

  if (error) return <Banner kind="error">{error}</Banner>;
  if (!data) return <Spinner label="Loading evidence…" />;

  const ev = data.evidence;
  const stateLabel = data.decision.state.replace(/_/g, " ");

  // chart 1: how far each clearance metric sits inside its tolerance (as % of
  // the allowed budget, 100 = exactly at the threshold)
  const tol = [
    { name: "area diff", pct: (ev.area_diff_pct / (data.thresholds.clear?.MAX_AREA_DIFF_PCT ?? 3)) * 100 },
    { name: "displacement", pct: (ev.boundary_displacement_m / (data.thresholds.clear?.MAX_BOUNDARY_DISPLACEMENT_M ?? 0.5)) * 100 },
    { name: "support*used", pct: (100 - ev.support_ratio_pct) / Math.max(1e-6, 100 - (data.thresholds.clear?.MIN_SUPPORT_RATIO_PCT ?? 90)) * 100 },
    { name: "occlusion", pct: (ev.occlusion_fraction / (data.thresholds.insufficient?.MAX_OCCLUSION_FRAC ?? 0.4)) * 100 },
    { name: "topology", pct: ev.topology_status === "FAIL" ? 150 : 20 },
  ];

  // chart 2: uncertainty score vs GOOD / MODERATE / POOR bands
  const q = data.thresholds.quality ?? { GOOD_MAX_UNCERTAINTY: 0.25, MODERATE_MAX_UNCERTAINTY: 0.5 };
  const qualityThresholds = [
    { name: "uncertainty", value: ev.uncertainty_score },
    { name: "GOOD limit", value: q.GOOD_MAX_UNCERTAINTY ?? 0.25 },
    { name: "MODERATE limit", value: q.MODERATE_MAX_UNCERTAINTY ?? 0.5 },
  ];
  const qualityColor =
    ev.evidence_quality === "GOOD" ? "#15803d" : ev.evidence_quality === "MODERATE" ? "#b45309" : "#b91c1c";

  return (
    <div className="flex flex-col gap-3" data-testid="evidence-screen">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-bold">Evidence — {id}</h1>
        <StateBadge state={data.decision.state} />
        <span className="text-xs text-slate-500">
          computed {new Date(data.decision.computed_at).toLocaleString()} · report{" "}
          {data.decision.evidence_report_id}
        </span>
        <div className="ml-auto flex items-center gap-2 text-xs">
          <Link className="text-sky-700 underline" to={`/compare/${id}`}>← map</Link>
          <Link className="text-sky-700 underline" to={`/history/${id}`}>history</Link>
          <Link
            className={`rounded px-3 py-1.5 font-semibold text-white ${
              data.decision.state === "CLEARED" ? "bg-emerald-600 hover:bg-emerald-500" : "bg-amber-600 hover:bg-amber-500"
            }`}
            to={`/verify/${id}`}
            data-testid="send-to-verification"
            title="Opens the field-verification screen pre-loaded with this parcel (US-3.2)"
          >
            {data.decision.state === "CLEARED"
              ? "Send to random audit"
              : "Send to field verification"}
          </Link>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-3">
        {/* ---- reason codes in plain language ---- */}
        <div className="bg-white border border-slate-200 rounded p-3">
          <h2 className="text-sm font-bold mb-2">Triage decision — {stateLabel}</h2>
          <ul className="flex flex-col gap-1.5 text-sm" data-testid="reason-list">
            {data.reasons.map((r) => (
              <li key={r.code} className="flex gap-2">
                <code className="text-[11px] bg-slate-100 rounded px-1 py-0.5 h-fit">{r.code}</code>
                <span className="text-slate-700">{r.copy}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* ---- checks ---- */}
        <div className="bg-white border border-slate-200 rounded p-3">
          <h2 className="text-sm font-bold mb-2">Clearance checks (config thresholds)</h2>
          <table className="w-full text-sm" data-testid="checks-table">
            <tbody>
              {data.checks.map((c) => (
                <tr key={c.name} className="border-b last:border-0">
                  <td className="py-1.5 pr-2 text-slate-600">{CHECK_LABELS[c.name] ?? c.name}</td>
                  <td className="py-1.5 pr-2 text-right tabular-nums font-semibold">
                    {typeof c.value === "number" ? c.value.toFixed(3) : c.value}
                  </td>
                  <td className="py-1.5 pr-2 text-xs text-slate-400">{c.rule}</td>
                  <td className="py-1.5 text-right"><PassFail pass={c.pass} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ---- charts ---- */}
      <div className="grid md:grid-cols-2 gap-3">
        <div className="bg-white border border-slate-200 rounded p-3">
          <h2 className="text-sm font-bold mb-1">Raw metrics vs tolerance</h2>
          <p className="text-[11px] text-slate-400 mb-2">
            % of the allowed budget consumed (100 = exactly at threshold, above = fail)
          </p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={tol} margin={{ top: 4, right: 8, left: -18, bottom: 4 }}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <RTooltip formatter={(v: number) => `${v.toFixed(0)}% of tolerance`} />
              <ReferenceLine y={100} stroke="#dc2626" strokeDasharray="4 3" />
              {tol.map((t, i) => (
                <Bar key={i} dataKey="pct" fill={t.pct > 100 ? "#dc2626" : "#2563eb"} radius={[3, 3, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-slate-200 rounded p-3">
          <h2 className="text-sm font-bold mb-1">
            Evidence quality vs uncertainty — <span style={{ color: qualityColor }}>{ev.evidence_quality}</span>
          </h2>
          <p className="text-[11px] text-slate-400 mb-2">
            uncertainty score 0 (best) … 1 (worst); dashed lines are configured band limits
          </p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={qualityThresholds} margin={{ top: 4, right: 8, left: -18, bottom: 4 }}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} domain={[0, 1]} />
              <RTooltip formatter={(v: number) => v.toFixed(3)} />
              <ReferenceLine y={q.GOOD_MAX_UNCERTAINTY ?? 0.25} stroke="#15803d" strokeDasharray="4 3" />
              <ReferenceLine y={q.MODERATE_MAX_UNCERTAINTY ?? 0.5} stroke="#b45309" strokeDasharray="4 3" />
              <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                {qualityThresholds.map((_, i) => (
                  <Cell key={i} fill={i === 0 ? qualityColor : "#cbd5e1"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ---- metrics detail ---- */}
      <div className="bg-white border border-slate-200 rounded p-3 grid md:grid-cols-3 gap-3 text-sm">
        <div>
          <div className="text-[11px] uppercase text-slate-500">Area deviation</div>
          <div className="font-semibold">
            {ev.area_diff_pct.toFixed(2)}% ({ev.area_diff_ha >= 0 ? "+" : ""}
            {ev.area_diff_ha.toFixed(4)} ha)
          </div>
        </div>
        <div>
          <div className="text-[11px] uppercase text-slate-500">Boundary displacement (ASBD)</div>
          <div className="font-semibold">{ev.boundary_displacement_m.toFixed(3)} m</div>
        </div>
        <div>
          <div className="text-[11px] uppercase text-slate-500">Support ratio</div>
          <div className="font-semibold">{ev.support_ratio_pct.toFixed(1)}%</div>
        </div>
        <div>
          <div className="text-[11px] uppercase text-slate-500">IoU with AI polygon</div>
          <div className="font-semibold">{ev.iou.toFixed(3)}</div>
        </div>
        <div>
          <div className="text-[11px] uppercase text-slate-500">Occlusion (imagery)</div>
          <div className="font-semibold">{ev.occlusion_fraction.toFixed(3)}</div>
        </div>
        <div>
          <div className="text-[11px] uppercase text-slate-500">AI confidence</div>
          <div className="font-semibold">{ev.ai_confidence.toFixed(3)}</div>
        </div>
        {ev.topology_issues.length > 0 && (
          <div className="md:col-span-3 text-red-700 text-xs">
            Topology issues: {ev.topology_issues.join("; ")}
          </div>
        )}
        <div className="md:col-span-3 text-[11px] text-slate-400">
          Match: {data.match?.match_type ?? "—"} · threshold set from{" "}
          <code>backend/config/triage.yaml</code> — edit the YAML and re-run the pipeline to
          see outcomes change (US-0.2).
        </div>
      </div>
    </div>
  );
}
