import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ParcelRow, Role, Summary, TriageState, STATE_STYLE } from "../api";
import { Banner, StateBadge, VerifyBadge, fmtNum } from "../components/ui";

const FILTERS: { key: "ALL" | TriageState; label: string }[] = [
  { key: "ALL", label: "All" },
  { key: "CLEARED", label: "Cleared" },
  { key: "FLAGGED", label: "Flagged" },
  { key: "INSUFFICIENT_EVIDENCE", label: "Insufficient" },
];

export default function ParcelsScreen({
  parcels,
  summary,
  role,
  onOpenExample,
  onRefresh,
}: {
  parcels: ParcelRow[];
  summary: Summary | null;
  role: Role;
  onOpenExample: (s: TriageState) => void;
  onRefresh: () => void;
}) {
  const [filter, setFilter] = useState<"ALL" | TriageState>("ALL");
  const [q, setQ] = useState("");
  const navigate = useNavigate();

  const rows = useMemo(() => {
    let out = parcels;
    if (filter !== "ALL") out = out.filter((p) => p.triage_state === filter);
    if (q.trim()) {
      const s = q.trim().toLowerCase();
      out = out.filter(
        (p) =>
          p.survey_number.toLowerCase().includes(s) ||
          p.ror_owner_name.toLowerCase().includes(s) ||
          p.id.toLowerCase().includes(s)
      );
    }
    return out;
  }, [parcels, filter, q]);

  if (!summary) {
    return (
      <div className="text-center py-10 text-slate-600">
        No triage state yet — run the pipeline (Admin/Surveyor) to generate it.
      </div>
    );
  }

  const counts = summary.counts;
  const examples = summary.seed_examples;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-bold">
          {summary.village.name} — parcels ({summary.parcel_count})
        </h1>
        <div className="flex rounded border border-slate-300 overflow-hidden text-xs">
          {FILTERS.map((f) => {
            const active = filter === f.key;
            const color = f.key === "ALL" ? "#334155" : STATE_STYLE[f.key as TriageState].color;
            return (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                className={`px-3 py-1.5 font-semibold ${active ? "text-white" : "bg-white text-slate-600"}`}
                style={active ? { backgroundColor: color } : undefined}
                data-testid={`filter-${f.key}`}
              >
                {f.label}
                <span className="ml-1 opacity-80">
                  {f.key === "ALL" ? parcels.length : counts[f.key]}
                </span>
              </button>
            );
          })}
        </div>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search survey № / owner / id…"
          className="border border-slate-300 rounded px-3 py-1.5 text-sm w-64"
          data-testid="parcel-search"
        />
        <div className="ml-auto flex items-center gap-2 text-xs">
          <span className="text-slate-500">Seeded examples:</span>
          {(Object.keys(examples) as TriageState[])
            .filter((k) => examples[k])
            .map((k) => (
              <button
                key={k}
                onClick={() => onOpenExample(k)}
                className="rounded px-2 py-1 text-white font-bold text-[10px]"
                style={{ backgroundColor: STATE_STYLE[k].color }}
                data-testid={`example-${k}`}
              >
                {STATE_STYLE[k].label}
              </button>
            ))}
        </div>
      </div>

      <Banner kind="info">
        Rows are colour-coded by triage state. Click a row to open its evidence; use the
        links for comparison, verification and history. Records with{" "}
        <b>ESCALATED</b> verification must not be re-opened for edit.
      </Banner>

      {rows.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          No parcels match this filter/search.
        </div>
      )}

      {rows.length > 0 && (
        <div className="bg-white border border-slate-200 rounded overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wide text-slate-500 border-b">
                <th className="px-3 py-2">Survey №</th>
                <th className="px-3 py-2">Record holder (mock)</th>
                <th className="px-3 py-2 text-right">Area (ha)</th>
                <th className="px-3 py-2">Triage</th>
                <th className="px-3 py-2">Match</th>
                <th className="px-3 py-2">Verify</th>
                <th className="px-3 py-2">Reasons</th>
                <th className="px-3 py-2 text-right">Open</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((p) => (
                <tr
                  key={p.id}
                  className="border-b last:border-0 hover:bg-slate-50 cursor-pointer"
                  onClick={() => navigate(`/evidence/${p.id}`)}
                  data-testid={`row-${p.survey_number}`}
                >
                  <td className="px-3 py-2 font-mono font-semibold">{p.survey_number}</td>
                  <td className="px-3 py-2">
                    {p.ror_owner_name}
                    <span className="ml-1 text-[10px] text-slate-400">({p.source})</span>
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {fmtNum(p.current_area_ha, 3)}
                  </td>
                  <td className="px-3 py-2">
                    <StateBadge state={p.triage_state} />
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-600">
                    {p.match_type ?? "—"}
                    {p.match_confidence !== null && (
                      <span className="text-slate-400"> · IoU {p.match_confidence.toFixed(2)}</span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    <VerifyBadge status={p.verification_status} />
                  </td>
                  <td className="px-3 py-2 text-[11px] text-slate-500 max-w-[260px] truncate">
                    {p.reason_codes.join(", ")}
                  </td>
                  <td
                    className="px-3 py-2 text-right whitespace-nowrap"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Link className="text-sky-700 hover:underline mr-2" to={`/compare/${p.id}`}>
                      map
                    </Link>
                    <Link className="text-sky-700 hover:underline mr-2" to={`/evidence/${p.id}`}>
                      evidence
                    </Link>
                    {role !== "VIEWER" && p.verification_status !== "ESCALATED" && (
                      <Link className="text-emerald-700 hover:underline mr-2" to={`/verify/${p.id}`}>
                        verify
                      </Link>
                    )}
                    <Link className="text-sky-700 hover:underline" to={`/history/${p.id}`}>
                      history
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="text-xs text-slate-400">
        Last run:{" "}
        {summary.latest_run
          ? `${summary.latest_run.run_id} · ${summary.latest_run.tier} · ${summary.latest_run.finished_at}`
          : "none"}
        <button className="underline ml-2" onClick={onRefresh}>
          refresh
        </button>
      </div>
    </div>
  );
}
