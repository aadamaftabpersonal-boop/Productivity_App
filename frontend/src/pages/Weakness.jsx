import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import { Target, RefreshCw, Clock, ExternalLink, Zap } from "lucide-react";

export default function Weakness() {
  const [weaknesses, setWeaknesses] = useState([]);
  const [resurface, setResurface] = useState(null);
  const [resurfaceMsg, setResurfaceMsg] = useState(null);

  useEffect(() => {
    client.get("/weakness/active").then((res) => setWeaknesses(res.data)).catch(() => {});
  }, []);

  const handleResurface = async () => {
    setResurfaceMsg(null);
    try {
      const { data } = await client.get("/weakness/resurface");
      setResurface(data);
    } catch (err) {
      setResurfaceMsg("All active weakness gaps are in 24-hour cooldown.");
      setResurface(null);
    }
  };

  return (
    <Layout>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-heading flex items-center gap-3">
            <Target className="text-rose-400" size={30} /> Weakness Signal Engine
          </h1>
          <p className="text-slate-400 text-sm">Longitudinal gap recurrence tracking & decay-on-success practice reps</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Weakness Recurrence Card */}
        <div className="saas-card p-6 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <h2 className="text-lg font-bold text-white font-heading">Active Recurring Gap Flags</h2>
            <span className="badge badge-amber">{weaknesses.length} Active Gaps</span>
          </div>

          {weaknesses.length === 0 ? (
            <p className="text-slate-400 text-sm">No recurring gap flags active.</p>
          ) : (
            <div className="space-y-3">
              {weaknesses.map((w) => (
                <div key={w.concept} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex justify-between items-center">
                  <div>
                    <span className="font-bold text-white text-base">{w.concept}</span>
                    <div className="text-xs text-slate-500 font-mono mt-0.5">
                      Last Flagged: {w.last_flagged_at ? new Date(w.last_flagged_at).toLocaleDateString() : 'Recent'}
                    </div>
                  </div>
                  <span className="badge badge-rose">{w.gap_count} Gaps</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Resurface Practice Drawer */}
        <div className="saas-card p-6 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <h2 className="text-lg font-bold text-white font-heading">Targeted Practice Resurfacing</h2>
            <span className="badge badge-cyan">30-Min Virtual Rep</span>
          </div>

          <button onClick={handleResurface} className="btn-primary w-full justify-center">
            <Zap size={15} /> Fetch Next Targeted Practice Item
          </button>

          {resurfaceMsg && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-sm">
              {resurfaceMsg}
            </div>
          )}

          {resurface && (
            <div className="p-5 rounded-xl bg-slate-950/90 border border-cyan-500/30 space-y-3">
              <span className="badge badge-violet">{resurface.mode.replace("_", " ")}</span>
              <p className="text-slate-200 text-sm leading-relaxed">{resurface.instruction}</p>
              {resurface.url && (
                <a href={resurface.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-cyan-400 font-bold text-sm hover:underline">
                  {resurface.problem_title} <ExternalLink size={14} />
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}