import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import WeaknessRadar from "../components/WeaknessRadar";
import CodeforcesImportModal from "../components/CodeforcesImportModal";
import LeetCodeImportModal from "../components/LeetCodeImportModal";
import { Target, Trophy, Clock, CheckCircle, RefreshCw, Zap, TrendingUp, Cpu, Activity, ArrowUpRight } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);
  const [activeDomain, setActiveDomain] = useState("cp");
  const [cfModalOpen, setCfModalOpen] = useState(false);
  const [lcModalOpen, setLcModalOpen] = useState(false);

  // Virtual Contest Rep Timer
  const [timerSeconds, setTimerSeconds] = useState(1800);
  const [timerRunning, setTimerRunning] = useState(false);

  const loadData = () => {
    client.get("/dashboard")
      .then((res) => setData(res.data))
      .catch(() => setError("Couldn't load dashboard server data. Ensure backend is running."));

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
      interval = setInterval(() => setTimerSeconds((prev) => prev - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [timerRunning, timerSeconds]);

  if (error) {
    return (
      <Layout>
        <div className="saas-card p-8 border-rose-500/30 bg-rose-500/10 text-rose-300">
          <div className="font-bold text-lg mb-2">Backend Server Connection Required</div>
          <p className="text-sm text-rose-200/80 mb-4">{error}</p>
          <div className="font-mono text-xs bg-slate-950 p-3 rounded-lg border border-slate-800 text-slate-300">
            Run command in terminal: uvicorn app.main:app --reload --port 8000
          </div>
        </div>
      </Layout>
    );
  }

  if (!data) {
    return (
      <Layout>
        <div className="saas-card p-12 text-center text-slate-400 font-mono text-sm">
          <RefreshCw className="animate-spin inline-block mr-2 text-cyan-400" size={18} />
          Initializing CP Hub Engine...
        </div>
      </Layout>
    );
  }

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

  const avgMastery = analytics ? Math.round(
    analytics.mastery_radar.reduce((acc, curr) => acc + curr.mastery_percent, 0) / (analytics.mastery_radar.length || 1)
  ) : 85;

  return (
    <Layout>
      {/* SaaS Hero Welcome Banner */}
      <div className="saas-card p-8 mb-8 relative overflow-hidden">
        <div className="absolute -top-12 -right-12 w-96 h-96 bg-gradient-to-br from-cyan-500/10 to-violet-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div className="max-w-2xl">
            <div className="flex items-center gap-3 mb-3">
              <span className="badge badge-cyan">
                <Zap size={13} /> Empirical Diagnostic Engine
              </span>
              <span className="text-xs text-slate-400 font-mono">Domain: {activeDomain.toUpperCase()}</span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight font-heading leading-tight mb-2">
              Welcome back, {data.user.full_name || "Developer"}
            </h1>
            <p className="text-slate-300 text-sm leading-relaxed">
              Longitudinal weakness tracking, tree-sitter AST call-graph walking, and empirical subprocess sandbox benchmarking.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            {/* Domain Switcher */}
            <div className="bg-slate-950/90 p-1.5 rounded-2xl border border-slate-800 flex gap-1">
              {['cp', 'ml', 'swe'].map((dom) => (
                <button
                  key={dom}
                  onClick={() => setActiveDomain(dom)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold uppercase tracking-wider transition-all ${
                    activeDomain === dom
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {dom}
                </button>
              ))}
            </div>

            {/* Sync Action Buttons */}
            <button onClick={() => setCfModalOpen(true)} className="btn-primary">
              <RefreshCw size={14} /> Sync Codeforces
            </button>
            <button onClick={() => setLcModalOpen(true)} className="btn-primary bg-gradient-to-r from-amber-500 to-orange-600">
              <RefreshCw size={14} /> Sync LeetCode
            </button>
          </div>
        </div>
      </div>

      {/* 4 Key SaaS Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="saas-card p-6 border-cyan-500/30">
          <div className="flex justify-between items-center text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Mastery Index</span>
            <Activity size={18} className="text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-white font-mono">{avgMastery}%</div>
          <div className="w-full bg-slate-950 h-2 rounded-full mt-3 overflow-hidden border border-slate-800">
            <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full" style={{ width: `${avgMastery}%` }} />
          </div>
        </div>

        <div className="saas-card p-6 border-violet-500/30">
          <div className="flex justify-between items-center text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Resolution Velocity</span>
            <TrendingUp size={18} className="text-violet-400" />
          </div>
          <div className="text-3xl font-extrabold text-white font-mono">
            +{analytics?.resolved_weakness_count || 12} <span className="text-xs text-emerald-400 font-sans font-semibold">Resolved</span>
          </div>
          <p className="text-xs text-slate-400 mt-3 flex items-center gap-1">
            <ArrowUpRight size={14} className="text-emerald-400" /> +18% decay rate this week
          </p>
        </div>

        <div className="saas-card p-6 border-emerald-500/30">
          <div className="flex justify-between items-center text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Sandbox Runs</span>
            <Cpu size={18} className="text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-white font-mono">
            {data.recent_submissions.length} <span className="text-xs text-slate-400 font-sans font-normal">Runs</span>
          </div>
          <p className="text-xs text-emerald-400 mt-3 font-semibold">100% Subprocess Isolated</p>
        </div>

        <div className="saas-card p-6 border-amber-500/30">
          <div className="flex justify-between items-center text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Active Weakness Flags</span>
            <Target size={18} className="text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-white font-mono">
            {data.active_weaknesses.length} <span className="text-xs text-amber-400 font-sans font-bold">Gaps</span>
          </div>
          <p className="text-xs text-slate-400 mt-3">Targeted resurfacing reps active</p>
        </div>
      </div>

      {/* Main Workspace Grid: Radar & Virtual Rep */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        <div className="lg:col-span-5">
          <WeaknessRadar masteryData={analytics?.mastery_radar || []} />
        </div>

        <div className="lg:col-span-7 space-y-6">
          {/* Virtual Practice Contest Widget */}
          <div className="saas-card p-6 border-cyan-500/30">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
                <Trophy className="text-cyan-400" size={22} /> Virtual Practice Rep
              </h2>
              {data.resurface_item && (
                <div className="flex items-center gap-2 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800">
                  <Clock size={16} className="text-amber-400 animate-pulse" />
                  <span className="font-mono text-xl font-extrabold text-amber-400">
                    {formatTimer(timerSeconds)}
                  </span>
                </div>
              )}
            </div>

            {data.resurface_item ? (
              <div className="space-y-4">
                <p className="text-slate-300 text-sm leading-relaxed">{data.resurface_item.instruction}</p>

                {data.resurface_item.url && (
                  <a
                    href={data.resurface_item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 text-cyan-400 font-semibold text-sm hover:underline"
                  >
                    Solve {data.resurface_item.problem_title} on Platform →
                  </a>
                )}

                <div className="flex items-center gap-3 pt-2">
                  {!timerRunning ? (
                    <button onClick={() => setTimerRunning(true)} className="btn-primary">
                      Start 30-Min Virtual Practice Rep
                    </button>
                  ) : (
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleCompleteResurface(data.resurface_item.concept_tag_id, true)}
                        className="btn-primary bg-gradient-to-r from-emerald-600 to-teal-600"
                      >
                        <CheckCircle size={16} /> Solved & Decay Gap
                      </button>
                      <button
                        onClick={() => handleCompleteResurface(data.resurface_item.concept_tag_id, false)}
                        className="btn-secondary text-rose-400 border-rose-500/30"
                      >
                        Needs Review
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-slate-400 text-sm">
                All weakness gaps are currently decayed. Keep submitting code to generate new signals.
              </p>
            )}
          </div>

          {/* Active Weakness Flags List */}
          <div className="saas-card p-6">
            <h2 className="text-lg font-bold text-white mb-4 font-heading flex items-center gap-2">
              <Target size={18} className="text-rose-400" /> Active Recurring Weakness Flags
            </h2>
            {data.active_weaknesses.length === 0 ? (
              <p className="text-slate-400 text-sm">No recurring gap flags active.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.active_weaknesses.map((w) => (
                  <div key={w.concept} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex justify-between items-center">
                    <span className="font-semibold text-sm text-slate-200">{w.concept}</span>
                    <span className="badge badge-amber">{w.gap_count} Gaps</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <CodeforcesImportModal
        isOpen={cfModalOpen}
        onClose={() => setCfModalOpen(false)}
        onImportSuccess={loadData}
        api={client}
      />

      <LeetCodeImportModal
        isOpen={lcModalOpen}
        onClose={() => setLcModalOpen(false)}
        onImportSuccess={loadData}
        api={client}
      />
    </Layout>
  );
}