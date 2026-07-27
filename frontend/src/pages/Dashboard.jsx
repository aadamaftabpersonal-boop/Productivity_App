import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import WeaknessRadar from "../components/WeaknessRadar";
import CodeforcesImportModal from "../components/CodeforcesImportModal";
import { Link } from "react-router-dom";
import { Target, Sparkles, RefreshCw, Trophy, Clock, CheckCircle } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);
  const [activeDomain, setActiveDomain] = useState("cp");
  const [cfModalOpen, setCfModalOpen] = useState(false);

  // Practice Rep Timer State
  const [timerSeconds, setTimerSeconds] = useState(1800); // 30 minutes
  const [timerRunning, setTimerRunning] = useState(false);

  const loadData = () => {
    client.get("/dashboard")
      .then((res) => setData(res.data))
      .catch(() => setError("Couldn't load dashboard."));

    client.get("/weakness/analytics")
      .then((res) => setAnalytics(res.data))
      .catch(() => console.error("Analytics fetch failed"));
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    let interval = null;
    if (timerRunning && timerSeconds > 0) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timerRunning, timerSeconds]);

  if (error) return <Layout><div className="text-red-400 p-6">{error}</div></Layout>;
  if (!data) return <Layout><div className="text-slate-400 font-mono text-sm p-6">Loading CP Hub Engine...</div></Layout>;

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleCompleteResurface = async (conceptTagId, success) => {
    try {
      await client.post('/weakness/resurface/complete', {
        concept_tag_id: conceptTagId,
        success,
        time_taken_seconds: 1800 - timerSeconds,
      });
      setTimerRunning(false);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Layout>
      {/* Top Banner Header & Codeforces Sync */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-3xl font-extrabold text-white font-heading tracking-tight">
              CP Hub Dashboard
            </h1>
            <span className="badge badge-cyan">v2.0 10/10 Engine</span>
          </div>
          <p className="text-slate-400 text-sm">
            Longitudinal weakness tracking & empirical complexity diagnostics
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Domain Segmented Switcher */}
          <div className="bg-slate-900/80 p-1 rounded-xl border border-slate-800 flex gap-1">
            {['cp', 'ml', 'swe'].map((dom) => (
              <button
                key={dom}
                onClick={() => setActiveDomain(dom)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
                  activeDomain === dom
                    ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {dom}
              </button>
            ))}
          </div>

          <button
            onClick={() => setCfModalOpen(true)}
            className="btn-primary text-sm py-2 px-4"
          >
            <RefreshCw size={14} /> Import Codeforces
          </button>
        </div>
      </div>

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Left Column: Weakness Radar Chart */}
        <div className="lg:col-span-1">
          <WeaknessRadar masteryData={analytics?.mastery_radar || []} />
        </div>

        {/* Right Column: Virtual Contest Rep & Active Weaknesses */}
        <div className="lg:col-span-2 space-y-6">
          {/* Virtual Practice Contest Widget */}
          <div className="glass-card p-6 border-cyan-500/20 relative overflow-hidden">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
                <Trophy className="text-cyan-400" size={20} /> Virtual Contest Rep
              </h2>
              {data.resurface_item && (
                <div className="flex items-center gap-2 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
                  <Clock size={16} className="text-amber-400 animate-pulse" />
                  <span className="font-mono text-lg font-bold text-amber-400">
                    {formatTimer(timerSeconds)}
                  </span>
                </div>
              )}
            </div>

            {data.resurface_item ? (
              <div className="space-y-4">
                <p className="text-slate-300 text-sm">{data.resurface_item.instruction}</p>

                {data.resurface_item.url && (
                  <a
                    href={data.resurface_item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 text-cyan-400 font-semibold text-sm hover:underline"
                  >
                    Solve {data.resurface_item.problem_title} on LeetCode →
                  </a>
                )}

                <div className="flex items-center gap-3 pt-2">
                  {!timerRunning ? (
                    <button
                      onClick={() => setTimerRunning(true)}
                      className="btn-primary py-2 px-4 text-xs"
                    >
                      Start 30-Min Virtual Timer
                    </button>
                  ) : (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleCompleteResurface(data.resurface_item.concept_tag_id, true)}
                        className="btn-primary bg-emerald-600 hover:bg-emerald-500 text-xs py-2 px-4"
                      >
                        <CheckCircle size={14} /> Solved & Decay Weakness
                      </button>
                      <button
                        onClick={() => handleCompleteResurface(data.resurface_item.concept_tag_id, false)}
                        className="btn-secondary text-xs py-2 px-4 text-rose-400 hover:bg-rose-500/10"
                      >
                        Failed / Need Review
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-slate-400 text-sm">
                No weakness to resurface right now. All active gaps are in 24-hour cooldown.
              </p>
            )}
          </div>

          {/* Active Weaknesses List */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-white mb-4 font-heading flex items-center gap-2">
              <Target size={18} className="text-rose-400" /> Active Weakness Flags
            </h2>
            {data.active_weaknesses.length === 0 ? (
              <p className="text-slate-400 text-sm">No active weakness flags — keep submitting solutions.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.active_weaknesses.map((w) => (
                  <div
                    key={w.concept}
                    className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center"
                  >
                    <span className="font-semibold text-sm text-slate-200">{w.concept}</span>
                    <span className="badge badge-warning">{w.gap_count} Gaps</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Codeforces Import Modal */}
      <CodeforcesImportModal
        isOpen={cfModalOpen}
        onClose={() => setCfModalOpen(false)}
        onImportSuccess={loadData}
        api={client}
      />
    </Layout>
  );
}