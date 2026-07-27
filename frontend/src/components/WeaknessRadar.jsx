import React from 'react';

export default function WeaknessRadar({ masteryData }) {
  if (!masteryData || masteryData.length === 0) {
    return (
      <div className="glass-card p-6 text-center text-slate-400">
        No concept mastery data recorded yet.
      </div>
    );
  }

  // Pick top 6-8 concepts for clean radar representation
  const radarPoints = masteryData.slice(0, 7);
  const total = radarPoints.length;

  const center = 150;
  const radius = 100;

  // Calculate polygon vertex coordinates for radar grid
  const getCoordinates = (index, valuePct) => {
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2;
    const currentRadius = (valuePct / 100) * radius;
    const x = center + currentRadius * Math.cos(angle);
    const y = center + currentRadius * Math.sin(angle);
    return { x, y };
  };

  // Build SVG polygon points string for user mastery
  const userPolygonPoints = radarPoints
    .map((item, idx) => {
      const { x, y } = getCoordinates(idx, item.mastery_percent);
      return `${x},${y}`;
    })
    .join(' ');

  // Grid levels (25%, 50%, 75%, 100%)
  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className="glass-card p-6 flex flex-col items-center">
      <div className="flex justify-between items-center w-full mb-4">
        <div>
          <h3 className="text-xl font-bold text-white tracking-wide">Weakness Mastery Radar</h3>
          <p className="text-sm text-slate-400">Longitudinal Concept Strength (0-100%)</p>
        </div>
        <span className="badge badge-cyan">AST & Performance Grounded</span>
      </div>

      <div className="relative w-[300px] h-[300px] flex justify-center items-center">
        <svg width="300" height="300" className="overflow-visible">
          {/* Background Grid Hexagons */}
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

          {/* Axis Spoke Lines */}
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

          {/* User Mastery Polygon Area */}
          <polygon
            points={userPolygonPoints}
            fill="rgba(6, 182, 212, 0.25)"
            stroke="#06B6D4"
            strokeWidth="2.5"
            className="transition-all duration-500 ease-out"
          />

          {/* Radar Category Labels and Vertex Dots */}
          {radarPoints.map((item, idx) => {
            const { x, y } = getCoordinates(idx, item.mastery_percent);
            const labelPos = getCoordinates(idx, 118);

            return (
              <g key={idx}>
                {/* Glowing Vertex Point */}
                <circle
                  cx={x}
                  cy={y}
                  r="4"
                  fill="#06B6D4"
                  className="filter drop-shadow-[0_0_8px_#06B6D4]"
                />
                {/* Concept Label */}
                <text
                  x={labelPos.x}
                  y={labelPos.y}
                  fill="#94A3B8"
                  fontSize="11"
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
