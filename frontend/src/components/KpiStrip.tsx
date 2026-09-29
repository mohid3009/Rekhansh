import { Kpis } from "../api";
import { fmtNum, fmtPct } from "./ui";

const DEFS: { key: keyof Kpis; label: string; unit: string; def: string }[] = [
  {
    key: "false_clear_rate_pct",
    label: "False-clear rate",
    unit: "%",
    def: "Cleared parcels an RTK audit found wrong (non-ACCEPT, or error above the false-clear threshold) ÷ all audited-cleared parcels.",
  },
  {
    key: "cleared_without_full_rtk_pct",
    label: "Cleared without full RTK",
    unit: "%",
    def: "Parcels currently CLEARED and never audited on RTK ÷ all parcels.",
  },
  {
    key: "boundary_rmse_m",
    label: "Boundary RMSE",
    unit: "m",
    def: "Root-mean-square boundary displacement against RTK-corrected ground truth. — when nothing has been corrected yet.",
  },
  {
    key: "area_error_pct",
    label: "Area error",
    unit: "%",
    def: "Mean absolute area error against RTK-corrected ground truth. — when nothing has been corrected yet.",
  },
  {
    key: "false_flag_rate_pct",
    label: "False-flag rate",
    unit: "%",
    def: "Flagged parcels an RTK audit confirmed were already correct ÷ all audited-flagged parcels.",
  },
  {
    key: "processing_time_per_parcel_ms",
    label: "Pipeline time / parcel",
    unit: "ms",
    def: "Total time of the latest full pipeline run ÷ parcel count.",
  },
];

export default function KpiStrip({ kpis, onRefresh }: { kpis: Kpis | null; onRefresh?: () => void }) {
  return (
    <div className="bg-white border-b border-slate-200 px-4 py-2 flex items-stretch gap-3 overflow-x-auto">
      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 self-center shrink-0">
        KPIs
      </span>
      {DEFS.map((d) => {
        const raw = kpis ? (kpis[d.key] as number | null | undefined) : undefined;
        const has = raw !== null && raw !== undefined && !Number.isNaN(raw);
        return (
          <div
            key={d.key}
            title={d.def}
            className="min-w-[132px] px-3 py-1 rounded border border-slate-200 bg-slate-50 hover:border-slate-400 transition-colors"
          >
            <div className="text-[10px] uppercase tracking-wide text-slate-500">{d.label}</div>
            <div className={`text-sm font-bold ${has ? "text-slate-800" : "text-slate-400"}`}>
              {has ? `${fmtNum(raw as number, 1)}${d.unit === "%" ? "%" : ` ${d.unit}`}` : "—"}
            </div>
          </div>
        );
      })}
      {kpis?.sample_sizes && (
        <div className="text-[10px] text-slate-400 self-center ml-1 max-w-[150px]">
          n: {kpis.sample_sizes.audited_cleared} cleared-audits, {kpis.sample_sizes.audited_flagged}{" "}
          flagged-audits, {kpis.sample_sizes.corrected} corrections
        </div>
      )}
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="ml-auto self-center text-[11px] text-slate-500 hover:text-slate-800 border border-slate-200 rounded px-2 py-1"
          title="Re-fetch KPI values"
        >
          refresh
        </button>
      )}
      <span className="self-center text-[10px] text-slate-400 hidden md:inline" title={fmtPct(0)}>
        computed live from RTK audits &amp; pipeline runs
      </span>
    </div>
  );
}
