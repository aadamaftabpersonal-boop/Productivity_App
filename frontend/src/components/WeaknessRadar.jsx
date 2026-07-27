import React from 'react';

export default function WeaknessRadar({ masteryData }) {
  if (!masteryData || masteryData.length === 0) {
    return (
      <div className="saas-card p-6 text-center text-slate-400 font-mono text-sm">
        No concept mastery data recorded yet.
      </div>
    );
  }

  const radarPoints = masteryData.slice(0, 7);
  const total = radarPoints.length;

  const center = 175;
  const radius = 105;

  const getCoordinates = (index, valuePct) => {
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2;
    const currentRadius = (valuePct / 100) * radius;
    const x = center + currentRadius * Math.cos(angle);
    const y = center + currentRadius * Math.sin(angle);
    return { x, y };
  };

  const userPolygonPoints = radarPoints
    .map((item, idx) => {
      const { x, y } = getCoordinates(idx, item.mastery_percent);
      return `${x},${y}`;
    })
    .join(' ');

  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className="saas-card p-6 flex flex-col items-center border-cyan-500/20">
      <div className="w-full border-b border-slate-800 pb-4 mb-4">
        <div className="flex justify-between items-center mb-1">
          <h3 className="text-lg font-bold text-white font-heading">Weakness Mastery Radar</h3>
          <span className="badge badge-cyan">AST Grounded</span>
        </div>
        <p className="text-xs text-slate-400">Longitudinal Concept Strength (0-100%)</p>
      </div>

      <div className="relative w-full max-w-[350px] aspect-square flex justify-center items-center py-2">
        <svg viewBox="0 0 350 350" className="w-full h-full overflow-visible">
          {gridLevels.map((lvl, lIdx) => {
            const levelPoints = radarPoints
              .map((_, idx) => {
                const { x, y } = getCoordinates(idx, lvl * 100);
                return `${x},${y}`;
              })
              .join(' ');
            return (
              <polygon
                key={lIdx}
                points={levelPoints}
                fill="none"
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="1.5"
              />
            );
          })}

          {radarPoints.map((_, idx) => {
            const { x, y } = getCoordinates(idx, 100);
            return (
              <line
                key={idx}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="1"
              />
            );
          })}

          <polygon
            points={userPolygonPoints}
            fill="rgba(6, 182, 212, 0.2)"
            stroke="#06B6D4"
            strokeWidth="2.5"
          />

          {radarPoints.map((item, idx) => {
            const { x, y } = getCoordinates(idx, item.mastery_percent);
            const labelPos = getCoordinates(idx, 132);

            return (
              <g key={idx}>
                <circle
                  cx={x}
                  cy={y}
                  r="4"
                  fill="#06B6D4"
                />
                <text
                  x={labelPos.x}
                  y={labelPos.y}
                  fill="#cbd5e1"
                  fontSize="10"
                  fontFamily="Inter, sans-serif"
                  fontWeight="600"
                  textAnchor="middle"
                  dominantBaseline="middle"
                >
                  {item.canonical_name.replace('_', ' ').toUpperCase()} ({item.mastery_percent}%)
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
