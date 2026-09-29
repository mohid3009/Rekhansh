import { useCallback, useEffect, useState } from "react";
import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { api, Kpis, Meta, ParcelRow, Role, RunResult, Summary, TriageState } from "./api";
import KpiStrip from "./components/KpiStrip";
import { Banner, Spinner } from "./components/ui";
import ParcelsScreen from "./screens/ParcelsScreen";
import MapCompareScreen from "./screens/MapCompareScreen";
import EvidenceScreen from "./screens/EvidenceScreen";
import VerifyScreen from "./screens/VerifyScreen";
import HistoryScreen from "./screens/HistoryScreen";

const NAV: { to: string; label: string }[] = [{ to: "/", label: "1 · Parcels" }];

export default function App() {
  const [role, setRole] = useState<Role>(
    () => (localStorage.getItem("role") as Role) || "SURVEYOR"
  );
  const [meta, setMeta] = useState<Meta | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [parcels, setParcels] = useState<ParcelRow[]>([]);
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const navigate = useNavigate();

  const setRoleAndPersist = (r: Role) => {
    setRole(r);
    localStorage.setItem("role", r);
  };

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const m = await api.get<Meta>("/api/meta");
      setMeta(m);
      if (m.has_triage && m.village) {
        const [s, p, k] = await Promise.all([
          api.get<Summary>(`/api/villages/${m.village.id}/summary`),
          api.get<ParcelRow[]>(`/api/villages/${m.village.id}/parcels`),
          api.get<Kpis>("/api/kpis"),
        ]);
        setSummary(s);
        setParcels(p);
        setKpis(k);
      } else {
        setSummary(null);
        setParcels([]);
        setKpis(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runPipeline = async () => {
    setRunning(true);
    setNotice(null);
    setError(null);
    try {
      const r = await api.post<RunResult>("/api/pipeline/run-full");
      setNotice(
        `Pipeline run ${r.run_id} finished in ${r.total_ms.toFixed(0)} ms — ` +
          `${r.outcomes.CLEARED} cleared, ${r.outcomes.FLAGGED} flagged, ` +
          `${r.outcomes.INSUFFICIENT_EVIDENCE} insufficient (tier: ${r.tier}).`
      );
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  };

  const openExample = (state: TriageState) => {
    const id = summary?.seed_examples?.[state];
    if (id) navigate(`/evidence/${id}`);
  };

  return (
    <div className="min-h-full flex flex-col">
      <header className="bg-slate-900 text-white">
        <div className="px-4 py-2.5 flex flex-wrap items-center gap-3">
          <div className="font-bold tracking-tight">
            Rural Land Resurvey Triage
            <span className="ml-2 text-[10px] bg-amber-400 text-amber-950 rounded px-1.5 py-0.5 align-middle font-extrabold">
              PROTOTYPE
            </span>
          </div>
          <nav className="flex gap-2 text-sm">
            {NAV.map((n) => (
              <Link key={n.to} to={n.to} className="px-2 py-1 rounded hover:bg-slate-700 text-slate-200">
                {n.label}
              </Link>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-2 text-xs">
            <span className="text-slate-400">Role</span>
            <select
              value={role}
              onChange={(e) => setRoleAndPersist(e.target.value as Role)}
              className="bg-slate-800 border border-slate-600 rounded px-2 py-1 text-white"
              data-testid="role-select"
            >
              <option value="VIEWER">VIEWER</option>
              <option value="SURVEYOR">SURVEYOR</option>
              <option value="ADMIN">ADMIN</option>
            </select>
            {(role === "ADMIN" || role === "SURVEYOR") && (
              <button
                onClick={() => void runPipeline()}
                disabled={running}
                className="bg-sky-600 hover:bg-sky-500 disabled:opacity-50 rounded px-3 py-1 font-semibold"
                data-testid="run-pipeline"
              >
                {running ? "Running…" : "Run full pipeline"}
              </button>
            )}
          </div>
        </div>
        <div className="prototype-banner text-amber-950 text-[11px] font-semibold px-4 py-1 border-t border-amber-300">
          PROTOTYPE DATA — real Bhu-Naksha cadastral parcels (Bond Gavhan, Nanded)
          over real Esri/Maxar basemap imagery (not surveyed by this project); owner
          names, the legacy scan and RTK traces are simulated. Not a legal record.
        </div>
      </header>

      <KpiStrip kpis={kpis} onRefresh={() => void refresh()} />

      <div className="px-4 pt-3 flex flex-col gap-2">
        {error && (
          <Banner kind="error">
            <div className="flex items-center justify-between gap-4">
              <span data-testid="error-banner">{error}</span>
              <button className="underline" onClick={() => void refresh()}>
                Retry
              </button>
            </div>
          </Banner>
        )}
        {notice && (
          <Banner kind="success">
            <span data-testid="run-notice">{notice}</span>
            <button className="ml-3 underline" onClick={() => setNotice(null)}>
              dismiss
            </button>
          </Banner>
        )}
        {role === "VIEWER" && (
          <Banner kind="info">
            You are a <b>VIEWER</b> — verification and pipeline actions are hidden (US-7.4).
          </Banner>
        )}
      </div>

      <main className="px-4 py-3 flex-1">
        {loading ? (
          <Spinner label="Loading village data…" />
        ) : error && !summary ? (
          <div className="text-center py-10">
            <p className="text-slate-600 mb-3">
              The API is unreachable or the pipeline has not produced triage state yet.
            </p>
            <button onClick={() => void refresh()} className="bg-slate-800 text-white rounded px-4 py-2">
              Retry
            </button>
          </div>
        ) : (
          <Routes>
            <Route
              path="/"
              element={
                <ParcelsScreen
                  parcels={parcels}
                  summary={summary}
                  role={role}
                  onOpenExample={openExample}
                  onRefresh={() => void refresh()}
                />
              }
            />
            <Route path="/compare/:id" element={<MapCompareScreen />} />
            <Route path="/evidence/:id" element={<EvidenceScreen />} />
            <Route
              path="/verify/:id"
              element={<VerifyScreen role={role} onDone={() => void refresh()} />}
            />
            <Route path="/history/:id" element={<HistoryScreen />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        )}
      </main>

      <footer className="bg-white border-t border-slate-200 px-4 py-2 text-[11px] text-slate-500 flex flex-wrap gap-4">
        <span>
          {meta?.village
            ? `${meta.village.name}, ${meta.village.district} District, ${meta.village.state}`
            : "no village"}
        </span>
        <span>tier: {meta?.thresholds.active_tier ?? "—"}</span>
        <span>triage config: {meta?.config_files.triage ?? "—"}</span>
        <span className="ml-auto">{meta?.app.data_classification ?? "PROTOTYPE DATA"}</span>
      </footer>
    </div>
  );
}
