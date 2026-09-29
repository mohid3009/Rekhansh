import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  CircleMarker,
  ImageOverlay,
  MapContainer,
  Polygon,
  Tooltip,
  ZoomControl,
} from "react-leaflet";
import { api, ComparisonPayload } from "../api";
import { Banner, Spinner } from "../components/ui";

const C = { recorded: "#2563eb", ai: "#dc2626", neighbour: "#f59e0b", gcp: "#7c3aed" };

function centroidOf(ring: [number, number][]): [number, number] {
  const n = ring.length;
  return [
    ring.reduce((s, r) => s + r[1], 0) / n,
    ring.reduce((s, r) => s + r[0], 0) / n,
  ];
}

export default function MapCompareScreen() {
  const { id } = useParams();
  const [data, setData] = useState<ComparisonPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRecorded, setShowRecorded] = useState(true);
  const [showAi, setShowAi] = useState(true);
  const [showNeighbours, setShowNeighbours] = useState(true);
  const [showGcps, setShowGcps] = useState(false);
  const [resetKey, setResetKey] = useState(0);

  useEffect(() => {
    if (!id) return;
    setData(null);
    setError(null);
    api
      .get<ComparisonPayload>(`/api/parcels/${id}/comparison`)
      .then(setData)
      .catch((e) => setError(String(e)));
  }, [id]);

  const bounds = useMemo(() => {
    if (!data?.orthomosaic?.bounds) return null;
    const [[s, w], [n, e]] = data.orthomosaic.bounds;
    return [[s, w], [n, e]] as [[number, number], [number, number]];
  }, [data]);

  if (error) return <Banner kind="error">{error}</Banner>;
  if (!data || !bounds) return <Spinner label="Loading comparison map…" />;

  const rec = data.recorded_geometry.coordinates[0] as [number, number][];
  const centre = centroidOf(rec);

  return (
    <div className="flex flex-col gap-2" data-testid="compare-screen">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-bold">Comparison map — {data.parcel_id}</h1>
        <div className="ml-auto flex flex-wrap items-center gap-3 text-xs">
          <label className="flex items-center gap-1">
            <input type="checkbox" checked={showRecorded} onChange={(e) => setShowRecorded(e.target.checked)} />
            <span style={{ color: C.recorded }}>■</span> Recorded
          </label>
          <label className="flex items-center gap-1">
            <input type="checkbox" checked={showAi} onChange={(e) => setShowAi(e.target.checked)} />
            <span style={{ color: C.ai }}>■</span> AI-detected ({data.ai_polygons.length})
          </label>
          <label className="flex items-center gap-1">
            <input type="checkbox" checked={showNeighbours} onChange={(e) => setShowNeighbours(e.target.checked)} />
            <span style={{ color: C.neighbour }}>■</span> Neighbours
          </label>
          <label className="flex items-center gap-1" title="Ground control points of the legacy-map georeferencing fit">
            <input type="checkbox" checked={showGcps} onChange={(e) => setShowGcps(e.target.checked)} />
            <span style={{ color: C.gcp }}>●</span> GCPs
          </label>
          <button className="border border-slate-300 rounded px-2 py-1" onClick={() => setResetKey((k) => k + 1)}>
            Reset view
          </button>
          <Link className="text-sky-700 underline" to={`/evidence/${data.parcel_id}`}>evidence →</Link>
          <Link className="text-sky-700 underline" to="/">← parcels</Link>
        </div>
      </div>

      <Banner kind="info">
        Orthomosaic © Esri World Imagery (provider basemap — <b>not</b> surveyed by this
        project), {data.orthomosaic.resolution_cm_per_px?.toFixed(1)} cm/px. Purple GCPs come
        from the legacy-map georeferencing fit (RMSE {data.legacy_scan.rmse_m?.toFixed(2)} m).
      </Banner>

      <div className="border border-slate-300 rounded overflow-hidden" style={{ height: 520 }}>
        <MapContainer key={resetKey} bounds={bounds} zoomControl={false}
          style={{ height: "100%", width: "100%" }}>
          <ZoomControl position="bottomright" />
          <ImageOverlay url={api.staticUrl(data.orthomosaic.url)} bounds={bounds} opacity={0.95} />
          {showRecorded && (
            <Polygon positions={rec}
              pathOptions={{ color: C.recorded, weight: 3, fill: false, dashArray: "6 4" }}>
              <Tooltip permanent direction="center" className="!bg-slate-900 !text-white !border-0">
                recorded · {data.recorded_area_ha.toFixed(3)} ha
              </Tooltip>
            </Polygon>
          )}
          {showAi && data.ai_polygons.map((a) => (
            <Polygon key={a.id}
              positions={a.geometry.coordinates[0] as [number, number][]}
              pathOptions={{ color: C.ai, weight: 2, fillOpacity: 0.12 }}>
              <Tooltip direction="center" className="!bg-white !text-slate-900 !border-slate-300">
                {a.id} · conf {a.confidence.toFixed(2)} · {a.detected_features.join(", ")}
                {a.evidence_note ? ` — ${a.evidence_note}` : ""}
              </Tooltip>
            </Polygon>
          ))}
          {showNeighbours && data.neighbour_overlaps.map((n) => (
            <Polygon key={n.id}
              positions={n.geometry.coordinates[0] as [number, number][]}
              pathOptions={{ color: C.neighbour, weight: 2, fill: false, dashArray: "3 6" }}>
              <Tooltip direction="center">{n.survey_number} · overlap {n.overlap_pct}%</Tooltip>
            </Polygon>
          ))}
          {showGcps && data.control_points.map((cp, i) => (
            <CircleMarker key={i} center={[cp.lat, cp.lon]} radius={5}
              pathOptions={{ color: C.gcp, fillColor: C.gcp, fillOpacity: 0.9 }}>
              <Tooltip>
                GCP {i + 1} (pixel {cp.pixel_x.toFixed(0)}, {cp.pixel_y.toFixed(0)})
              </Tooltip>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="text-xs text-slate-500">
        Hover polygons for details; toggles switch layers without re-fetching (US-2.2).
        Match: {data.match?.match_type ?? "—"}
        {data.match ? ` (IoU ${data.match.match_confidence.toFixed(2)})` : ""} · centre{" "}
        {centre[0].toFixed(5)}, {centre[1].toFixed(5)}
      </div>
    </div>
  );
}
