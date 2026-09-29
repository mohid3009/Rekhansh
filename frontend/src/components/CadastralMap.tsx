import React, { useState, useMemo } from 'react';
import { DemoParcel } from '../demoData';

interface CadastralMapProps {
  parcels: DemoParcel[];
  selectedId: string | null;
  hoveredId: string | null;
  onSelectParcel: (parcel: DemoParcel) => void;
  onHoverParcel: (id: string | null) => void;
}

const MIN_LON = 78.0795455;
const MAX_LON = 78.0996230;
const MIN_LAT = 19.8783580;
const MAX_LAT = 19.8902507;

const SVG_WIDTH = 840;
const SVG_HEIGHT = 520;
const PAD_X = 35;
const PAD_Y = 35;

function project(lon: number, lat: number): [number, number] {
  const x = ((lon - MIN_LON) / (MAX_LON - MIN_LON)) * (SVG_WIDTH - 2 * PAD_X) + PAD_X;
  const y = ((MAX_LAT - lat) / (MAX_LAT - MIN_LAT)) * (SVG_HEIGHT - 2 * PAD_Y) + PAD_Y;
  return [x, y];
}

export default function CadastralMap({
  parcels,
  selectedId,
  hoveredId,
  onSelectParcel,
  onHoverParcel,
}: CadastralMapProps) {
  const [bgMode, setBgMode] = useState<'satellite' | 'paper' | 'blueprint'>('satellite');
  const [showLabels, setShowLabels] = useState(true);
  const [showDiscrepancy, setShowDiscrepancy] = useState(true);
  const [zoomLevel, setZoomLevel] = useState(1);

  // Compute SVG polygons and centroids
  const projectedParcels = useMemo(() => {
    return parcels.map((p) => {
      const ring = p.geometry.coordinates[0] || [];
      const points = ring.map(([lon, lat]) => project(lon, lat));
      const pointsString = points.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');

      // Simple centroid
      let sumX = 0;
      let sumY = 0;
      points.forEach(([x, y]) => {
        sumX += x;
        sumY += y;
      });
      const cx = points.length ? sumX / points.length : 0;
      const cy = points.length ? sumY / points.length : 0;

      // Perturbed points for discrepancy overlay
      const shiftedString = points
        .map(([x, y]) => {
          const shift = p.triage_state === 'FLAGGED' ? 4 : p.triage_state === 'INSUFFICIENT_EVIDENCE' ? 8 : 1.5;
          return `${(x + shift).toFixed(1)},${(y - shift).toFixed(1)}`;
        })
        .join(' ');

      return {
        ...p,
        pointsString,
        shiftedString,
        centroid: [cx, cy] as [number, number],
      };
    });
  }, [parcels]);

  const activeParcel = useMemo(() => {
    return projectedParcels.find((p) => p.id === (hoveredId || selectedId));
  }, [projectedParcels, hoveredId, selectedId]);

  const getFillColor = (state: string, isHover: boolean, isSelect: boolean) => {
    if (state === 'CLEARED') {
      return isSelect ? 'rgba(16, 185, 129, 0.7)' : isHover ? 'rgba(16, 185, 129, 0.55)' : 'rgba(16, 185, 129, 0.38)';
    }
    if (state === 'FLAGGED') {
      return isSelect ? 'rgba(245, 158, 11, 0.75)' : isHover ? 'rgba(245, 158, 11, 0.6)' : 'rgba(245, 158, 11, 0.42)';
    }
    return isSelect ? 'rgba(239, 68, 68, 0.75)' : isHover ? 'rgba(239, 68, 68, 0.6)' : 'rgba(239, 68, 68, 0.42)';
  };

  const getStrokeColor = (state: string, isHover: boolean, isSelect: boolean) => {
    if (isSelect) return '#ffffff';
    if (isHover) return '#38bdf8';
    if (state === 'CLEARED') return '#059669';
    if (state === 'FLAGGED') return '#d97706';
    return '#dc2626';
  };

  return (
    <div className="relative flex flex-col bg-slate-900 border border-slate-700/80 rounded-xl overflow-hidden shadow-2xl">
      {/* Map Header Toolbar */}
      <div className="px-4 py-2.5 bg-slate-950/80 backdrop-blur border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-semibold text-slate-200">Interactive Cadastral GIS Vector Layer</span>
          <span className="text-slate-500">· 30 Bhu-Naksha Parcels</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Layer Style Switcher */}
          <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg p-0.5">
            <button
              onClick={() => setBgMode('satellite')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                bgMode === 'satellite' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              🛰️ Satellite
            </button>
            <button
              onClick={() => setBgMode('paper')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                bgMode === 'paper' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              📜 Paper Scan
            </button>
            <button
              onClick={() => setBgMode('blueprint')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                bgMode === 'blueprint' ? 'bg-cyan-700 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              📐 Blueprint
            </button>
          </div>

          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`px-2.5 py-1 rounded border text-[11px] font-medium transition ${
              showLabels
                ? 'bg-slate-800 border-slate-600 text-slate-200'
                : 'bg-transparent border-slate-700 text-slate-500'
            }`}
          >
            Labels: {showLabels ? 'ON' : 'OFF'}
          </button>

          <button
            onClick={() => setShowDiscrepancy(!showDiscrepancy)}
            className={`px-2.5 py-1 rounded border text-[11px] font-medium transition ${
              showDiscrepancy
                ? 'bg-amber-950/60 border-amber-600 text-amber-300'
                : 'bg-transparent border-slate-700 text-slate-500'
            }`}
          >
            Discrepancy: {showDiscrepancy ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div
        className={`relative w-full aspect-[840/520] select-none cursor-crosshair overflow-hidden transition-colors ${
          bgMode === 'satellite'
            ? 'bg-[#0b1320]'
            : bgMode === 'paper'
            ? 'bg-[#f4efe4]'
            : 'bg-[#06182c]'
        }`}
      >
        {/* Simulated Satellite Terrain Texture Pattern */}
        {bgMode === 'satellite' && (
          <div
            className="absolute inset-0 opacity-40 pointer-events-none"
            style={{
              backgroundImage: `radial-gradient(#1e293b 1px, transparent 1px), linear-gradient(135deg, rgba(16,185,129,0.05) 0%, rgba(59,130,246,0.05) 100%)`,
              backgroundSize: '24px 24px, 100% 100%',
            }}
          />
        )}

        {/* Paper texture */}
        {bgMode === 'paper' && (
          <div
            className="absolute inset-0 opacity-25 pointer-events-none"
            style={{
              backgroundImage: `radial-gradient(#92400e 0.75px, transparent 0.75px)`,
              backgroundSize: '16px 16px',
            }}
          />
        )}

        <svg
          viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
          className="w-full h-full"
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center', transition: 'transform 0.2s' }}
        >
          <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid lines */}
          <g stroke={bgMode === 'paper' ? '#d6c8b0' : '#1e293b'} strokeWidth="0.5" strokeDasharray="4 4">
            {[100, 200, 300, 400, 500, 600, 700].map((x) => (
              <line key={`gx-${x}`} x1={x} y1={0} x2={x} y2={SVG_HEIGHT} />
            ))}
            {[100, 200, 300, 400].map((y) => (
              <line key={`gy-${y}`} x1={0} y1={y} x2={SVG_WIDTH} y2={y} />
            ))}
          </g>

          {/* Discrepancy Overlay (Simulated legacy paper boundary shift) */}
          {showDiscrepancy && (
            <g opacity="0.6">
              {projectedParcels.map((p) => {
                if (p.triage_state === 'CLEARED') return null;
                return (
                  <polygon
                    key={`disc-${p.id}`}
                    points={p.shiftedString}
                    fill="none"
                    stroke="#fbbf24"
                    strokeWidth="1.2"
                    strokeDasharray="4 3"
                  />
                );
              })}
            </g>
          )}

          {/* Base Polygons */}
          {projectedParcels.map((p) => {
            const isHover = hoveredId === p.id;
            const isSelect = selectedId === p.id;
            const strokeWidth = isSelect ? 3 : isHover ? 2.5 : 1.2;

            return (
              <g
                key={p.id}
                onClick={() => onSelectParcel(p)}
                onMouseEnter={() => onHoverParcel(p.id)}
                onMouseLeave={() => onHoverParcel(null)}
                className="transition-all duration-150"
              >
                <polygon
                  points={p.pointsString}
                  fill={getFillColor(p.triage_state, isHover, isSelect)}
                  stroke={getStrokeColor(p.triage_state, isHover, isSelect)}
                  strokeWidth={strokeWidth}
                  filter={isSelect ? 'url(#glow)' : undefined}
                />

                {/* Survey Number Label */}
                {showLabels && (
                  <text
                    x={p.centroid[0]}
                    y={p.centroid[1]}
                    textAnchor="middle"
                    dominantBaseline="central"
                    fill={bgMode === 'paper' ? '#1f2937' : '#ffffff'}
                    fontSize={isSelect ? '13' : '10'}
                    fontWeight={isSelect ? '800' : '600'}
                    className="pointer-events-none select-none drop-shadow"
                  >
                    #{p.survey_number}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Floating Tooltip */}
        {activeParcel && (
          <div className="absolute top-3 left-4 pointer-events-none bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-lg p-2.5 shadow-2xl text-xs flex flex-col gap-1 max-w-xs z-20 animate-fade-in">
            <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-1">
              <span className="font-bold text-white text-sm">Survey #{activeParcel.survey_number}</span>
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-extrabold ${
                  activeParcel.triage_state === 'CLEARED'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    : activeParcel.triage_state === 'FLAGGED'
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                }`}
              >
                {activeParcel.triage_state}
              </span>
            </div>
            <div className="text-[11px] text-slate-300 font-medium truncate">{activeParcel.ror_owner_name}</div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px] text-slate-400 pt-1">
              <div>
                Recorded: <span className="text-white font-mono">{activeParcel.recorded_area_ha} ha</span>
              </div>
              <div>
                AI Obs: <span className="text-white font-mono">{activeParcel.current_area_ha} ha</span>
              </div>
              <div>
                IoU Match: <span className="text-emerald-400 font-mono">{(activeParcel.match_confidence * 100).toFixed(0)}%</span>
              </div>
              <div>
                ASBD: <span className="text-amber-400 font-mono">{activeParcel.asbd_m} m</span>
              </div>
            </div>
            <div className="text-[10px] text-slate-500 pt-0.5 border-t border-slate-800">
              Reason: <span className="text-slate-300">{activeParcel.reason_codes[0]}</span>
            </div>
          </div>
        )}

        {/* Map Legend Overlay */}
        <div className="absolute bottom-3 right-4 pointer-events-none bg-slate-950/85 backdrop-blur border border-slate-800 rounded-lg px-3 py-2 text-[11px] flex items-center gap-4 text-slate-300 z-10 shadow-lg">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-emerald-500 border border-emerald-300" />
            <span>Cleared (20)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-amber-500 border border-amber-300" />
            <span>Flagged (6)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-rose-500 border border-rose-300" />
            <span>Insufficient (4)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
