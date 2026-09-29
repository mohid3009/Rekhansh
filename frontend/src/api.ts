// Typed API client. VITE_API_BASE_URL is empty in local dev (Vite proxies
// /api and /static); set it to the deployed backend origin on Vercel.
const BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

async function j<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? body);
    } catch {
      /* keep statusText */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return (await res.json()) as T;
}

export const api = {
  get: <T,>(path: string) => j<T>(path),
  post: <T,>(path: string, body?: unknown) =>
    j<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }),
  staticUrl: (rel: string) => `${BASE}${rel}`,
};

export type TriageState = "CLEARED" | "FLAGGED" | "INSUFFICIENT_EVIDENCE";
export type Role = "VIEWER" | "SURVEYOR" | "ADMIN";

export const STATE_STYLE: Record<TriageState, { color: string; label: string }> = {
  CLEARED: { color: "#15803d", label: "CLEARED" },
  FLAGGED: { color: "#b45309", label: "FLAGGED" },
  INSUFFICIENT_EVIDENCE: { color: "#b91c1c", label: "INSUFFICIENT EVIDENCE" },
};

export interface Village {
  id: string;
  name: string;
  district: string;
  state: string;
  lat: number;
  lon: number;
  source: string;
  notes: string;
}

export interface ParcelRow {
  id: string;
  survey_number: string;
  ror_owner_name: string;
  source: string;
  recorded_area_ha: number;
  current_area_ha: number;
  geometry: GeoJSON.Polygon;
  triage_state: TriageState | null;
  reason_codes: string[];
  match_type: "ONE_TO_ONE" | "SPLIT" | "MERGE" | "NO_MATCH" | null;
  match_confidence: number | null;
  verification_status: "UNVERIFIED" | "CONFIRMED" | "CORRECTED" | "ESCALATED";
  version_number: number;
}

export interface Summary {
  village: Village;
  parcel_count: number;
  counts: Record<TriageState, number>;
  seed_examples: Partial<Record<TriageState, string>>;
  survey: {
    id?: string;
    orthomosaic_path?: string;
    dsm_path?: string | null;
    resolution_cm_per_px?: number;
    capture_date?: string;
    bounds?: number[][];
    provenance?: Record<string, unknown>;
  };
  legacy: {
    id?: string;
    raster_path?: string;
    rmse_m?: number;
    affine_transform?: number[];
    applied_distortion?: Record<string, unknown>;
  };
  latest_run: {
    run_id: string;
    tier: string;
    finished_at: string;
    steps: { name: string; ms: number; [k: string]: unknown }[];
    ok?: number;
  } | null;
}

export interface EvidencePayload {
  decision: {
    id: string;
    parcel_id: string;
    state: TriageState;
    reason_codes: string[];
    evidence_report_id: string;
    computed_at: string;
  };
  evidence: {
    id: string;
    area_diff_ha: number;
    area_diff_pct: number;
    boundary_displacement_m: number;
    iou: number;
    support_ratio_pct: number;
    occlusion_fraction: number;
    topology_status: "PASS" | "FAIL";
    topology_issues: string[];
    uncertainty_score: number;
    evidence_quality: "GOOD" | "MODERATE" | "POOR";
    ai_confidence: number;
    computed_at: string;
  };
  match: {
    id: string;
    field_polygon_ids: string[];
    match_type: "ONE_TO_ONE" | "SPLIT" | "MERGE" | "NO_MATCH";
    match_confidence: number;
  } | null;
  thresholds: Record<string, Record<string, number>>;
  reasons: { code: string; copy: string }[];
  checks: { name: string; value: number | string; rule: string; pass: boolean }[];
}

export interface ComparisonPayload {
  parcel_id: string;
  recorded_geometry: GeoJSON.Polygon;
  recorded_area_ha: number;
  ai_polygons: {
    id: string;
    geometry: GeoJSON.Polygon;
    confidence: number;
    detected_features: string[];
    source: string;
    evidence_note?: string | null;
  }[];
  neighbour_overlaps: {
    id: string;
    survey_number: string;
    overlap_pct: number;
    geometry: GeoJSON.Polygon;
  }[];
  match: { match_type: string; match_confidence: number } | null;
  orthomosaic: {
    url: string;
    bounds: number[][];
    resolution_cm_per_px?: number;
    provenance?: Record<string, unknown>;
  };
  legacy_scan: {
    url: string;
    rmse_m?: number;
    affine_transform?: number[];
    applied_distortion?: Record<string, unknown>;
  };
  control_points: { pixel_x: number; pixel_y: number; lat: number; lon: number }[];
}

export interface VersionRow {
  id: string;
  parcel_id: string;
  version_number: number;
  geometry: GeoJSON.Polygon;
  area_ha: number;
  verification_status: string;
  evidence_report_id: string | null;
  surveyor_action: string | null;
  timestamp: string;
  previous_version_id: string | null;
  previous_version_hash: string | null;
  record_hash: string;
}

export interface VersionsPayload {
  versions: VersionRow[];
  integrity: { version_number: number; hash_ok: boolean; chain_verified: boolean; recomputed_hash: string }[];
}

export interface ParcelDetail {
  parcel: {
    id: string;
    survey_number: string;
    ror_owner_name: string;
    source: string;
    recorded_area_ha: number;
    current_geometry: GeoJSON.Polygon;
    current_area_ha: number;
    verification_status: string;
    created_at: string;
  };
  triage: { state: TriageState; reason_codes: string[]; computed_at: string } | null;
  match: { match_type: string; match_confidence: number } | null;
  evidence: Record<string, number | string | string[]> | null;
  version_count: number;
  latest_version: VersionRow;
  verifications: {
    id: string;
    surveyor_decision: string;
    surveyor_notes: string;
    verified_by: string;
    verified_at: string;
    observed_error_m: number;
    triage_state_at_audit: string | null;
  }[];
}

export interface Kpis {
  false_clear_rate_pct: number | null;
  cleared_without_full_rtk_pct: number | null;
  boundary_rmse_m: number | null;
  area_error_pct: number | null;
  false_flag_rate_pct: number | null;
  processing_time_per_parcel_ms: number | null;
  sample_sizes?: { audited_cleared: number; audited_flagged: number; corrected: number };
}

export interface Meta {
  app: { name: string; mode: string; data_classification: string; reason_codes: Record<string, string> };
  site: Record<string, unknown> & { name: string; district: string; state: string };
  thresholds: Record<string, Record<string, number | string>> & { active_tier: string };
  config_files: { triage: string; site: string };
  village: Village | null;
  seed_examples: Partial<Record<TriageState, string>>;
  has_triage: boolean;
  latest_run: Summary["latest_run"];
}

export interface RunResult {
  run_id: string;
  tier: string;
  steps: { name: string; ms: number; [k: string]: unknown }[];
  parcel_count: number;
  total_ms: number;
  outcomes: Record<TriageState, number>;
  seed_examples: Partial<Record<TriageState, string>>;
  kpis?: Kpis;
}
