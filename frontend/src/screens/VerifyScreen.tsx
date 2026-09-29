import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { MapContainer, ImageOverlay, Marker, Polygon, Tooltip, useMapEvents } from "react-leaflet";
import L from "leaflet";
import { api, ComparisonPayload, ParcelDetail, Role } from "../api";
import { Banner, Spinner, StateBadge, VerifyBadge, fmtNum } from "../components/ui";

type Ring = [number, number][]; // closed GeoJSON-style ring (lon, lat)

const vertexIcon = L.divIcon({
  className: "",
  html: '<div style="width:12px;height:12px;background:#2563eb;border:2px solid white;border-radius:50%;box-shadow:0 0 3px #000"></div>',
  iconSize: [12, 12],
  iconAnchor: [6, 6],
});

/** local planar approximation good enough for a live area preview */
function areaHa(ring: Ring): number {
  if (ring.length < 4) return 0;
  const lat0 = ring.reduce((s, r) => s + r[1], 0) / ring.length;
  const mx = 111_320 * Math.cos((lat0 * Math.PI) / 180);
  const my = 110_540;
  const pts = ring.map((r) => [(r[0] - ring[0][0]) * mx, (r[1] - ring[0][1]) * my]);
  let s = 0;
  for (let i = 0; i < pts.length - 1; i++) {
    s += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1];
  }
  return Math.abs(s / 2) / 10_000;
}

function ClickToAdd({ onAdd }: { onAdd: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onAdd(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function VerifyScreen({ role, onDone }: { role: Role; onDone: () => void }) {
  const { id } = useParams();
  const [detail, setDetail] = useState<ParcelDetail | null>(null);
  const [comp, setComp] = useState<ComparisonPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ring, setRing] = useState<Ring>([]);
  const [dirty, setDirty] = useState(false);
  const [notes, setNotes] = useState("");
  const [verifiedBy, setVerifiedBy] = useState(
    localStorage.getItem("verified_by") || "field-surveyor-1"
  );
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setError(null);
    Promise.all([
      api.get<ParcelDetail>(`/api/parcels/${id}`),
      api.get<ComparisonPayload>(`/api/parcels/${id}/comparison`),
    ])
      .then(([d, c]) => {
        setDetail(d);
        setComp(c);
        setRing(
          (d.parcel.current_geometry.coordinates[0] as Ring).map(
            (p) => [p[0], p[1]] as [number, number]
          )
        );
      })
      .catch((e) => setError(String(e)));
  }, [id, success]);

  const bounds = useMemo(() => {
    if (!comp?.orthomosaic?.bounds) return null;
    const [[s, w], [n, e]] = comp.orthomosaic.bounds;
    return [[s, w], [n, e]] as [[number, number], [number, number]];
  }, [comp]);

  if (error) return <Banner kind="error">{error}</Banner>;
  if (!detail || !comp || !bounds) return <Spinner label="Loading parcel for verification…" />;

  const status = detail.parcel.verification_status;
  const editable =
    role !== "VIEWER" &&
    status === "UNVERIFIED" &&
    detail.triage?.state !== undefined;
  const distinct = new Set(ring.map((p) => `${p[0]},${p[1]}`)).size;
  const canCorrect = dirty && distinct >= 3 && editable;

  const patchRing = (i: number, lat: number, lon: number) => {
    setRing((r) => r.map((p, k) => (k === i ? ([lon, lat] as [number, number]) : p)));
    setDirty(true);
  };
  const addVertex = (lat: number, lon: number) => {
    if (!editable) return;
    setRing((r) => [...r.slice(0, -1), [lon, lat] as [number, number], r[r.length - 1]]);
    setDirty(true);
  };
  const resetRing = () => {
    setRing((detail.parcel.current_geometry.coordinates[0] as Ring).map((p) => [p[0], p[1]] as [number, number]));
    setDirty(false);
  };

  const submit = async (decision: "ACCEPT" | "CORRECT" | "REJECT") => {
    if (!id) return;
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      localStorage.setItem("verified_by", verifiedBy);
      const body: Record<string, unknown> = { decision, notes, verified_by: verifiedBy };
      if (decision === "CORRECT") {
        body.corrected_geometry = { type: "Polygon", coordinates: [ring] };
      }
      const res = await api.post<{ versions: { version_number: number; verification_status: string }[] }>(
        `/api/parcels/${id}/rtk-verification`,
        body
      );
      const v = res.versions[res.versions.length - 1];
      setSuccess(
        `Verification ${decision} recorded — new version v${v.version_number} ` +
          `(${v.verification_status}) appended with a new hash.`
      );
      onDone();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const [[s0, w0], [n0, e0]] = bounds;

  return (
    <div className="flex flex-col gap-3" data-testid="verify-screen">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-bold">Field verification — {detail.parcel.survey_number}</h1>
        <StateBadge state={detail.triage?.state ?? null} />
        <VerifyBadge status={status} />
        <span className="text-xs text-slate-500">
          record holder (mock): {detail.parcel.ror_owner_name} · v
          {detail.latest_version.version_number}
        </span>
        <div className="ml-auto flex gap-2 text-xs">
          <Link className="text-sky-700 underline" to={`/evidence/${id}`}>← evidence</Link>
          <Link className="text-sky-700 underline" to={`/history/${id}`}>history</Link>
        </div>
      </div>

      <Banner kind="prototype">
        <b>PROTOTYPE</b> — verification is simulated: RTK checkpoints are generated for demo
        purposes and no sub-metre receiver is involved. Your decision still creates a real,
        hash-chained version.
      </Banner>

      {role === "VIEWER" && (
        <Banner kind="info">
          VIEWER role — verification actions are hidden (US-7.4). Switch role to SURVEYOR to verify.
        </Banner>
      )}
      {!editable && role !== "VIEWER" && (
        <Banner kind="info">
          Parcel status is <b>{status}</b>
          {status === "ESCALATED"
            ? " — escalated records are locked and require the senior-review path (US-4.3)."
            : " — this record has already been verified and is read-only."}
        </Banner>
      )}
      {success && <Banner kind="success">{success}</Banner>}
      {error && <Banner kind="error">{error}</Banner>}

      <div className="grid lg:grid-cols-3 gap-3">
        <div
          className="lg:col-span-2 border border-slate-300 rounded overflow-hidden"
          style={{ height: 480 }}
        >
          <MapContainer bounds={bounds} style={{ height: "100%", width: "100%" }}>
            <ImageOverlay url={api.staticUrl(comp.orthomosaic.url)} bounds={bounds} opacity={0.9} />
            <Polygon
              positions={ring.map((p) => [p[1], p[0]] as [number, number])}
              pathOptions={{ color: "#2563eb", weight: 3, fill: false }}
            />
            {comp.ai_polygons.map((a) => (
              <Polygon
                key={a.id}
                positions={a.geometry.coordinates[0] as [number, number][]}
                pathOptions={{ color: "#dc2626", weight: 1, fillOpacity: 0.08, dashArray: "4 4" }}
              />
            ))}
            {editable &&
              ring.map((p, i) =>
                i === ring.length - 1 ? null : (
                  <Marker
                    key={i}
                    position={[p[1], p[0]]}
                    icon={vertexIcon}
                    draggable
                    eventHandlers={{
                      dragend: (e) => {
                        const ll = (e.target as L.Marker).getLatLng();
                        patchRing(i, ll.lat, ll.lng);
                      },
                    }}
                  >
                    <Tooltip>vertex {i} — drag to correct</Tooltip>
                  </Marker>
                )
              )}
            {editable && <ClickToAdd onAdd={addVertex} />}
          </MapContainer>
        </div>

        <div className="flex flex-col gap-3">
          <div className="bg-white border border-slate-200 rounded p-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Stored area</span>
              <b>{fmtNum(detail.parcel.current_area_ha, 3)} ha</b>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Edited area (live)</span>
              <b className={dirty ? "text-amber-600" : ""}>{fmtNum(areaHa(ring), 3)} ha</b>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Vertices</span>
              <b>{distinct}</b>
            </div>
            {dirty && (
              <button className="mt-2 text-xs underline text-slate-500" onClick={resetRing}>
                discard edits
              </button>
            )}
            <p className="text-[11px] text-slate-400 mt-2">
              Drag blue vertices to move a corner; click the map to add one (US-4.2).
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded p-3 flex flex-col gap-2 text-sm">
            <label className="text-xs text-slate-500">
              Surveyor id
              <input
                className="mt-1 w-full border border-slate-300 rounded px-2 py-1"
                value={verifiedBy}
                onChange={(e) => setVerifiedBy(e.target.value)}
                disabled={!editable}
              />
            </label>
            <label className="text-xs text-slate-500">
              Notes
              <textarea
                className="mt-1 w-full border border-slate-300 rounded px-2 py-1"
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="What did you find on the ground?"
                disabled={!editable}
              />
            </label>
            <div className="flex gap-2">
              <button
                className="flex-1 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded py-2 font-semibold"
                disabled={!editable || busy}
                onClick={() => void submit("ACCEPT")}
                data-testid="accept-btn"
                title="Accept as correct — keeps the geometry (US-4.1)"
              >
                Accept
              </button>
              <button
                className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded py-2 font-semibold"
                disabled={!canCorrect || busy}
                onClick={() => void submit("CORRECT")}
                data-testid="correct-btn"
                title={
                  canCorrect
                    ? "Submit the edited geometry (US-4.1)"
                    : "Requires at least 3 distinct vertices and some edit (US-4.1)"
                }
              >
                Submit correction
              </button>
            </div>
            <button
              className="bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white rounded py-2 font-semibold"
              disabled={!editable || busy}
              onClick={() => void submit("REJECT")}
              data-testid="reject-btn"
              title="Reject evidence — parcel becomes ESCALATED (US-4.3)"
            >
              Reject / escalate
            </button>
            {busy && <Spinner label="Submitting…" />}
          </div>
        </div>
      </div>
    </div>
  );
}
