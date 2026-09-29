import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, VersionsPayload } from "../api";
import { Banner, Spinner, StateBadge } from "../components/ui";

export default function HistoryScreen() {
  const { id } = useParams();
  const [data, setData] = useState<VersionsPayload | null>(null);
  const [detailState, setDetailState] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = () => {
    if (!id) return;
    setError(null);
    Promise.all([
      api.get<VersionsPayload>(`/api/parcels/${id}/versions`),
      api.get<{ triage: { state: string } | null }>(`/api/parcels/${id}`),
    ])
      .then(([v, d]) => {
        setData(v);
        setDetailState(d.triage?.state ?? null);
      })
      .catch((e) => setError(String(e)));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const recompute = () => {
    setBusy(true);
    load();
    setTimeout(() => setBusy(false), 400);
  };

  const exportJson = async () => {
    if (!id) return;
    const payload = await api.get<Record<string, unknown>>(`/api/parcels/${id}/export`);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${id}-evidence-export.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  if (error) return <Banner kind="error">{error}</Banner>;
  if (!data) return <Spinner label="Loading version history…" />;

  const allOk = data.integrity.every((i) => i.hash_ok && i.chain_verified);
  const brokenAt = data.integrity.find((i) => !i.hash_ok || !i.chain_verified);

  return (
    <div className="flex flex-col gap-3" data-testid="history-screen">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-bold">Version history — {id}</h1>
        {detailState && <StateBadge state={detailState as never} />}
        <div className="ml-auto flex gap-2 text-xs">
          <button
            className="border border-slate-300 rounded px-3 py-1.5"
            onClick={recompute}
            disabled={busy}
            data-testid="recompute-integrity"
          >
            {busy ? "Recomputing…" : "Recompute integrity"}
          </button>
          <button
            className="bg-slate-800 text-white rounded px-3 py-1.5"
            onClick={() => void exportJson()}
            data-testid="export-json"
          >
            Export evidence JSON (US-5.2)
          </button>
          <Link className="text-sky-700 underline self-center" to={`/evidence/${id}`}>
            ← evidence
          </Link>
        </div>
      </div>

      {allOk ? (
        <Banner kind="success">
          Chain verified: every record hash matches its recomputation and links to its
          predecessor. Hash-chain method documented in the PRD (not a blockchain).
        </Banner>
      ) : (
        <Banner kind="error">
          Chain broken starting at version {brokenAt?.version_number} — a stored hash no
          longer matches its recomputation, or a predecessor link was altered (US-5.3).
        </Banner>
      )}

      <div className="bg-white border border-slate-200 rounded overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wide text-slate-500 border-b">
              <th className="px-3 py-2">v</th>
              <th className="px-3 py-2">Timestamp (UTC)</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Action</th>
              <th className="px-3 py-2 text-right">Area (ha)</th>
              <th className="px-3 py-2">Evidence link</th>
              <th className="px-3 py-2">prev hash</th>
              <th className="px-3 py-2">record hash</th>
              <th className="px-3 py-2">Integrity</th>
            </tr>
          </thead>
          <tbody>
            {data.versions.map((v, i) => {
              const ok = data.integrity[i];
              const verified = ok?.hash_ok && ok?.chain_verified;
              return (
                <tr key={v.id} className="border-b last:border-0">
                  <td className="px-3 py-2 font-mono font-bold">v{v.version_number}</td>
                  <td className="px-3 py-2 text-xs">
                    {v.timestamp.replace("T", " ").slice(0, 19)}
                  </td>
                  <td className="px-3 py-2 text-xs font-semibold">{v.verification_status}</td>
                  <td className="px-3 py-2 text-xs">{v.surveyor_action ?? "—"}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{v.area_ha.toFixed(4)}</td>
                  <td className="px-3 py-2 text-[11px] font-mono">
                    {v.evidence_report_id ?? "—"}
                  </td>
                  <td className="px-3 py-2 text-[10px] font-mono text-slate-400 max-w-[120px] truncate">
                    {v.previous_version_hash
                      ? `${v.previous_version_hash.slice(0, 16)}…`
                      : "(genesis)"}
                  </td>
                  <td
                    className="px-3 py-2 text-[10px] font-mono text-slate-600 max-w-[140px] truncate"
                    title={v.record_hash}
                  >
                    {v.record_hash.slice(0, 18)}…
                  </td>
                  <td className="px-3 py-2">
                    <span
                      className={`rounded px-2 py-0.5 text-[11px] font-bold ${
                        verified ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                      }`}
                    >
                      {verified ? "OK" : "BROKEN"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-slate-400">
        Rows are append-only: re-running the pipeline or verifying other parcels never
        rewrites this chain (US-6.1). “Export evidence JSON” downloads this parcel’s full
        evidence, verifications and history as one JSON document (US-5.2).
      </p>
    </div>
  );
}
