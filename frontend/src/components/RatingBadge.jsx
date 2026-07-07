const TIER_MAP = [
  { max: 1, color: "bg-tier-gray/20 text-tier-gray border-tier-gray/40" },
  { max: 3, color: "bg-tier-green/20 text-tier-green border-tier-green/40" },
  { max: 5, color: "bg-tier-cyan/20 text-tier-cyan border-tier-cyan/40" },
  { max: 8, color: "bg-tier-blue/20 text-tier-blue border-tier-blue/40" },
  { max: Infinity, color: "bg-tier-red/20 text-tier-red border-tier-red/40" },
];

// gap_count (or any severity int) maps to a tier color — reuses the CF rating-color
// vernacular so it reads instantly to this audience: higher count = hotter color.
export default function RatingBadge({ label, count }) {
  const tier = TIER_MAP.find((t) => count <= t.max) || TIER_MAP[TIER_MAP.length - 1];
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded border font-mono text-xs ${tier.color}`}>
      {label}
      {count != null && <span className="opacity-70">×{count}</span>}
    </span>
  );
}