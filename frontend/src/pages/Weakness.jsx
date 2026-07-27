import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import CodeEditor from "../components/CodeEditor";
import { Target, Clock, ExternalLink, Zap, CheckCircle, RotateCcw, Play } from "lucide-react";

export default function Weakness() {
  const [weaknesses, setWeaknesses] = useState([]);
  const [resurface, setResurface] = useState(null);
  const [resurfaceMsg, setResurfaceMsg] = useState(null);
  const [userCode, setUserCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  // Virtual Contest Rep Timer
  const [timerSeconds, setTimerSeconds] = useState(1800);
  const [timerRunning, setTimerRunning] = useState(false);

  const loadWeaknesses = () => {
    client.get("/weakness/active").then((res) => setWeaknesses(res.data)).catch(() => {});
  };

  useEffect(() => { loadWeaknesses(); }, []);

  useEffect(() => {
    let interval = null;
    if (timerRunning && timerSeconds > 0) {
      interval = setInterval(() => setTimerSeconds((prev) => prev - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [timerRunning, timerSeconds]);

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleResurface = async () => {
    setResurfaceMsg(null);
    setFeedback(null);
    try {
      const { data } = await client.get("/weakness/resurface");
      setResurface(data);
      setTimerSeconds(1800);
      setTimerRunning(true);
      setUserCode("# Re-attempt solution here...\ndef solve():\n    pass\n");
    } catch (err) {
      setResurfaceMsg("All active weakness gaps are in 24-hour cooldown.");
      setResurface(null);
    }
  };

  const handleCompleteResurface = async (success) => {
    if (!resurface) return;
    setSubmitting(true);
    try {
      const { data } = await client.post('/weakness/resurface/complete', {
        concept_tag_id: resurface.concept_tag_id || "default",
        success,
        time_taken_seconds: 1800 - timerSeconds,
      });
      setFeedback(data);
      setTimerRunning(false);
      loadWeaknesses();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const [selectedWeakness, setSelectedWeakness] = useState(null);

  return (
    <Layout>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-heading flex items-center gap-3">
            <Target className="text-rose-400" size={30} /> Weakness Signal Engine Workspace
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">Longitudinal gap recurrence tracking & decay-on-success practice reps</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Active Weakness Recurrence List (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="saas-card p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white font-heading">Active Recurring Gap Flags</h2>
              <span className="badge badge-amber">{weaknesses.length} Active Gaps</span>
            </div>

            {weaknesses.length === 0 ? (
              <div className="p-6 text-center text-slate-500 font-mono text-sm">
                No recurring gap flags active — submit reviews to generate signals.
              </div>
            ) : (
              <div className="space-y-3">
                {weaknesses.map((w) => (
                  <div
                    key={w.concept}
                    onClick={() => setSelectedWeakness(selectedWeakness === w.concept ? null : w.concept)}
                    className={`p-4 rounded-xl border transition cursor-pointer space-y-3.5 ${
                      selectedWeakness === w.concept
                        ? "bg-slate-900 border-cyan-500/50 shadow-lg shadow-cyan-500/10"
                        : "bg-slate-950/80 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-white text-base">{w.concept}</span>
                      <div className="flex items-center gap-2">
                        <span className="badge badge-indigo text-[10px]">{w.peer_vulnerability_percent || 64}% of candidates share this gap</span>
                        <span className="badge badge-rose">{w.gap_count} Gaps</span>
                      </div>
                    </div>


                    <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="bg-gradient-to-r from-rose-500 to-amber-500 h-full rounded-full"
                        style={{ width: `${Math.min(100, w.gap_count * 25)}%` }}
                      />
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono">
                      <span>Threshold: 2+ flags active</span>
                      <span className="text-cyan-400 font-semibold">Click to view recommended problems ↓</span>
                    </div>

                    {/* Curated Recommended Problems Dropdown */}
                    {selectedWeakness === w.concept && w.recommended_problems?.length > 0 && (
                      <div className="pt-2 border-t border-slate-800 space-y-2">
                        <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                          Matched LeetCode / Codeforces Problems:
                        </div>
                        {w.recommended_problems.map((p, idx) => (
                          <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center text-xs font-mono">
                            <div>
                              <div className="font-bold text-white">{p.title}</div>
                              <div className="text-[10px] text-slate-400">{p.platform} • <span className="text-amber-400">{p.difficulty}</span></div>
                            </div>
                            <a
                              href={p.url}
                              target="_blank"
                              rel="noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="btn-secondary text-[11px] py-1 px-2.5 flex items-center gap-1 hover:border-cyan-500/50"
                            >
                              Solve <ExternalLink size={12} />
                            </a>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>


        {/* Right Column: Targeted Practice Reconstruction Workspace (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="saas-card p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-lg font-bold text-white font-heading">Targeted Problem Reconstruction</h2>
                <p className="text-xs text-slate-400">Re-attempt flagged concepts to decay gap counts</p>
              </div>
              <button onClick={handleResurface} className="btn-primary">
                <Zap size={14} /> Fetch Next Practice Item
              </button>
            </div>

            {resurfaceMsg && (
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-sm font-mono">
                {resurfaceMsg}
              </div>
            )}

            {!resurface ? (
              <div className="flex flex-col items-center justify-center py-20 text-slate-500 text-center">
                <RotateCcw size={40} className="mb-3 text-slate-600" />
                <div className="font-bold text-slate-300 text-base">No Item Selected</div>
                <p className="text-xs max-w-sm mt-1">Click "Fetch Next Practice Item" above to get a 30-minute virtual reconstruction rep.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Practice Header & Timer */}
                <div className="p-5 rounded-xl bg-slate-950/90 border border-cyan-500/30 flex justify-between items-center">
                  <div>
                    <span className="badge badge-violet mb-2">{resurface.concept || "Concept Reconstruction"}</span>
                    <h3 className="text-xl font-bold text-white font-heading">{resurface.problem_title || "Targeted Gap Problem"}</h3>
                  </div>

                  <div className="flex items-center gap-2 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800 font-mono text-xl font-extrabold text-amber-400">
                    <Clock size={18} className="animate-pulse" />
                    {formatTimer(timerSeconds)}
                  </div>
                </div>

                <p className="text-slate-300 text-sm leading-relaxed">{resurface.instruction}</p>

                {resurface.url && (
                  <a href={resurface.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-cyan-400 font-bold text-sm hover:underline">
                    Solve {resurface.problem_title} on Platform → <ExternalLink size={14} />
                  </a>
                )}

                {/* Embedded Reconstruction Code Editor */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Reconstruction Code</label>
                  <CodeEditor value={userCode} onChange={setUserCode} language="python" />
                </div>

                {feedback && (
                  <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs space-y-1 font-mono">
                    <div className="font-bold text-sm">Resurface Rep Complete!</div>
                    <div>New Gap Count: {feedback.new_gap_count}</div>
                    <div>CF Score Points Earned: +{feedback.cf_points_earned}</div>
                  </div>
                )}

                <div className="flex items-center gap-3 pt-2">
                  <button
                    onClick={() => handleCompleteResurface(true)}
                    disabled={submitting}
                    className="btn-primary bg-gradient-to-r from-emerald-600 to-teal-600"
                  >
                    <CheckCircle size={16} /> Mark Solved & Decay Gap
                  </button>
                  <button
                    onClick={() => handleCompleteResurface(false)}
                    disabled={submitting}
                    className="btn-secondary text-rose-400 border-rose-500/30"
                  >
                    Needs Review
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}