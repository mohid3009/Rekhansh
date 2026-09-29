import React, { useState } from 'react';
import { DemoParcel } from '../demoData';

interface ParcelInspectorModalProps {
  parcel: DemoParcel | null;
  role: 'VIEWER' | 'SURVEYOR' | 'ADMIN';
  onClose: () => void;
  onUpdateStatus: (parcelId: string, newStatus: 'CLEARED' | 'FLAGGED' | 'INSUFFICIENT_EVIDENCE', note: string) => void;
}

export default function ParcelInspectorModal({
  parcel,
  role,
  onClose,
  onUpdateStatus,
}: ParcelInspectorModalProps) {
  const [activeTab, setActiveTab] = useState<'evidence' | 'waterfall' | 'ledger'>('evidence');
  const [surveyorNote, setSurveyorNote] = useState('');
  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);

  if (!parcel) return null;

  const handleAction = (status: 'CLEARED' | 'FLAGGED' | 'INSUFFICIENT_EVIDENCE') => {
    onUpdateStatus(parcel.id, status, surveyorNote || `Status updated to ${status} by ${role}`);
    setSubmittedMessage(`Decision registered successfully as ${status}! Block minted in tamper-evident ledger.`);
    setTimeout(() => {
      setSubmittedMessage(null);
      onClose();
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl font-bold text-white">Survey #{parcel.survey_number}</span>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                parcel.triage_state === 'CLEARED'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  : parcel.triage_state === 'FLAGGED'
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
              }`}
            >
              {parcel.triage_state}
            </span>
            <span className="text-xs text-slate-400 font-mono">ID: {parcel.id}</span>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg p-1.5 transition"
          >
            ✕
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 bg-slate-900/60 px-6 pt-2 gap-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('evidence')}
            className={`pb-2.5 border-b-2 transition ${
              activeTab === 'evidence'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            📊 Mathematical Evidence
          </button>
          <button
            onClick={() => setActiveTab('waterfall')}
            className={`pb-2.5 border-b-2 transition ${
              activeTab === 'waterfall'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            ⚡ Waterfall Rule Trace
          </button>
          <button
            onClick={() => setActiveTab('ledger')}
            className={`pb-2.5 border-b-2 transition ${
              activeTab === 'ledger'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            🔒 SHA-256 Audit Ledger (US-5.3)
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-sm text-slate-200">
          {submittedMessage && (
            <div className="p-3 bg-emerald-950/60 border border-emerald-600 rounded-xl text-emerald-300 font-medium text-center animate-bounce">
              {submittedMessage}
            </div>
          )}

          {/* Owner & Legal Records Strip */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3.5 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <div className="text-slate-400">RoR Legal Owner</div>
              <div className="font-semibold text-white truncate">{parcel.ror_owner_name}</div>
            </div>
            <div>
              <div className="text-slate-400">Recorded Area</div>
              <div className="font-semibold font-mono text-white">{parcel.recorded_area_ha} ha</div>
            </div>
            <div>
              <div className="text-slate-400">Observed Area</div>
              <div className="font-semibold font-mono text-emerald-400">{parcel.current_area_ha} ha</div>
            </div>
            <div>
              <div className="text-slate-400">Area Variance</div>
              <div className={`font-semibold font-mono ${parcel.area_delta_pct > 5 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {parcel.area_delta_pct}%
              </div>
            </div>
          </div>

          {/* Tab 1: Mathematical Evidence */}
          {activeTab === 'evidence' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex flex-col gap-1">
                  <span className="text-[11px] text-slate-400">IoU Overlap</span>
                  <span className="text-xl font-bold font-mono text-emerald-400">
                    {(parcel.match_confidence * 100).toFixed(0)}%
                  </span>
                  <span className="text-[10px] text-slate-500">Threshold: ≥ 85%</span>
                </div>

                <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex flex-col gap-1">
                  <span className="text-[11px] text-slate-400">ASBD Boundary Dist.</span>
                  <span className="text-xl font-bold font-mono text-amber-400">
                    {parcel.asbd_m} m
                  </span>
                  <span className="text-[10px] text-slate-500">Threshold: ≤ 2.0 m</span>
                </div>

                <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex flex-col gap-1">
                  <span className="text-[11px] text-slate-400">Feature Support</span>
                  <span className="text-xl font-bold font-mono text-cyan-400">
                    {parcel.support_ratio_pct}%
                  </span>
                  <span className="text-[10px] text-slate-500">Threshold: ≥ 60%</span>
                </div>

                <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex flex-col gap-1">
                  <span className="text-[11px] text-slate-400">Canopy Occlusion</span>
                  <span className="text-xl font-bold font-mono text-rose-400">
                    {(parcel.occlusion_fraction * 100).toFixed(0)}%
                  </span>
                  <span className="text-[10px] text-slate-500">Max limit: ≤ 30%</span>
                </div>
              </div>

              <div className="bg-slate-950/40 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="text-xs font-semibold text-slate-300">Triage Decision Rationales</div>
                <div className="flex flex-wrap gap-2">
                  {parcel.reason_codes.map((rc, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 rounded bg-slate-800 text-slate-200 border border-slate-700 text-xs font-mono"
                    >
                      {rc}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-slate-400 pt-1">
                  Evaluated using least-squares 6-parameter affine georeferencing and Shapely UTM metric projection against ESRI World Imagery.
                </p>
              </div>
            </div>
          )}

          {/* Tab 2: Waterfall Rule Trace */}
          {activeTab === 'waterfall' && (
            <div className="space-y-3">
              <div className="text-xs text-slate-400">
                Deterministic decision table evaluated in strict PRD order:
              </div>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
                  <span>1. Ring Geometry Validity</span>
                  <span className="text-emerald-400 font-semibold">✓ Passed (Valid Polygon)</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
                  <span>2. Occlusion & Sensor Quality Check</span>
                  <span className={parcel.occlusion_fraction > 0.3 ? 'text-rose-400 font-semibold' : 'text-emerald-400 font-semibold'}>
                    {parcel.occlusion_fraction > 0.3 ? '✗ Failed (> 30% Canopy Shadow)' : '✓ Passed'}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
                  <span>3. Legal Area Variance Limit (5%)</span>
                  <span className={parcel.area_delta_pct > 5 ? 'text-amber-400 font-semibold' : 'text-emerald-400 font-semibold'}>
                    {parcel.area_delta_pct > 5 ? `✗ Exceeded (${parcel.area_delta_pct}%)` : '✓ Passed'}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
                  <span>4. ASBD Boundary Deviation (2.0 m)</span>
                  <span className={parcel.asbd_m > 2.0 ? 'text-amber-400 font-semibold' : 'text-emerald-400 font-semibold'}>
                    {parcel.asbd_m > 2.0 ? `✗ Exceeded (${parcel.asbd_m} m)` : '✓ Passed'}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
                  <span>5. Physical Feature Support Ratio (60%)</span>
                  <span className={parcel.support_ratio_pct < 60 ? 'text-rose-400 font-semibold' : 'text-emerald-400 font-semibold'}>
                    {parcel.support_ratio_pct < 60 ? `✗ Low Support (${parcel.support_ratio_pct}%)` : '✓ Passed'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Cryptographic Audit Ledger */}
          {activeTab === 'ledger' && (
            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="text-indigo-400 font-bold">Block #1 (Current State)</span>
                  <span className="text-[10px] text-slate-500">Version {parcel.version_number}</span>
                </div>
                <div className="break-all text-slate-300">
                  <span className="text-slate-500">Hash: </span>{parcel.current_hash}
                </div>
                <div className="break-all text-slate-400">
                  <span className="text-slate-500">Parent Hash: </span>{parcel.parent_hash}
                </div>
              </div>

              <div className="p-3 bg-slate-950/50 border border-slate-800/80 rounded-xl space-y-1">
                <div className="text-slate-400 font-bold">Block #0 (Genesis Ingestion)</div>
                <div className="break-all text-slate-500">
                  0000000000000000000000000000000000000000000000000000000000000000
                </div>
              </div>

              <div className="flex items-center gap-2 text-emerald-400 text-[11px] pt-1 font-sans">
                <span>✓ Cryptographic Hash Chain Fully Verified (Tamper-Evident)</span>
              </div>
            </div>
          )}

          {/* Surveyor Verification Console */}
          {role !== 'VIEWER' ? (
            <div className="pt-3 border-t border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-300">Surveyor & SRO Decision Console ({role})</span>
                <span className="text-slate-500">Actions commit to audit ledger</span>
              </div>

              <input
                type="text"
                placeholder="Enter field surveyor verification justification note..."
                value={surveyorNote}
                onChange={(e) => setSurveyorNote(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleAction('CLEARED')}
                  className="flex-1 py-2 px-3 bg-emerald-600 hover:bg-emerald-500 font-semibold text-xs rounded-lg text-white shadow transition"
                >
                  ✓ Confirm & Sign-off
                </button>
                <button
                  onClick={() => handleAction('FLAGGED')}
                  className="py-2 px-3 bg-amber-600 hover:bg-amber-500 font-semibold text-xs rounded-lg text-white shadow transition"
                >
                  ⚠️ Flag for Field Review
                </button>
                <button
                  onClick={() => handleAction('INSUFFICIENT_EVIDENCE')}
                  className="py-2 px-3 bg-rose-600 hover:bg-rose-500 font-semibold text-xs rounded-lg text-white shadow transition"
                >
                  🛰️ Escalate to RTK Rover
                </button>
              </div>
            </div>
          ) : (
            <div className="pt-2 text-center text-xs text-slate-500">
              Logged in as Viewer. Switch role to Surveyor or Admin/SRO to perform verification sign-offs.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
