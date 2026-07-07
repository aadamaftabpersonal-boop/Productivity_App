import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import RatingBadge from "../components/RatingBadge";

export default function Weakness() {
  const [weaknesses, setWeaknesses] = useState([]);
  const [resurface, setResurface] = useState(null);
  const [resurfaceMsg, setResurfaceMsg] = useState(null);

  useEffect(() => {
    client.get("/weakness/active").then((res) => setWeaknesses(res.data));
  }, []);

  const handleResurface = async () => {
    setResurfaceMsg(null);
    try {
      const { data } = await client.get("/weakness/resurface");
      setResurface(data);
    } catch (err) {
      setResurfaceMsg("Nothing to resurface right now — no active weaknesses, or all in cooldown.");
      setResurface(null);
    }
  };

  return (
    <Layout>
      <h1 className="font-mono text-xl font-bold mb-6">Weakness Tracker</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-panel border border-border rounded-lg p-5">
          <h2 className="font-mono text-sm text-muted uppercase tracking-wide mb-3">Active Weaknesses</h2>
          {weaknesses.length === 0 ? (
            <p className="text-sm text-muted">None flagged yet — keep submitting reviews.</p>
          ) : (
            <div className="space-y-2">
              {weaknesses.map((w) => (
                <div key={w.concept} className="flex items-center justify-between">
                  <RatingBadge label={w.concept} count={w.gap_count} />
                  <span className="text-xs text-muted font-mono">
                    {w.last_flagged_at && new Date(w.last_flagged_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-panel border border-border rounded-lg p-5">
          <h2 className="font-mono text-sm text-muted uppercase tracking-wide mb-3">Resurface</h2>
          <button
            onClick={handleResurface}
            className="text-sm bg-tier-blue text-white rounded px-3 py-2 font-medium hover:opacity-90 transition mb-4"
          >
            Get next item
          </button>
          {resurfaceMsg && <p className="text-sm text-muted">{resurfaceMsg}</p>}
          {resurface && (
            <div className="text-sm space-y-2">
              <div className="text-xs text-muted uppercase font-mono">{resurface.mode.replace("_", " ")}</div>
              <p>{resurface.instruction}</p>
              {resurface.url && (
                <a href={resurface.url} target="_blank" rel="noreferrer" className="text-tier-blue hover:underline font-mono">
                  {resurface.problem_title} →
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}