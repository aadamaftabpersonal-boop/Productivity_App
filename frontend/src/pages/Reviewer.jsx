import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import RatingBadge from "../components/RatingBadge";
import CodeEditor from "../components/CodeEditor";
import DiffViewer from "../components/DiffViewer";
import AstVisualizer from "../components/AstVisualizer";
import { AlertTriangle, CheckCircle, RefreshCw } from "lucide-react";


export default function Reviewer() {
  const [form, setForm] = useState({ language: "python", code: "", domain: "cp", problem_title: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);

  const loadHistory = () => {
    client.get("/reviewer/history").then((res) => setHistory(res.data));
  };

  useEffect(() => { loadHistory(); }, []);

  const pollJobStatus = (jobId) => {
    setJobStatus("processing");
    const interval = setInterval(async () => {
      try {
        const { data } = await client.get(`/reviewer/job/${jobId}`);
        if (data.status === "completed" && data.submission) {
          setSelected(data.submission);
          setJobStatus("completed");
          loadHistory();
          clearInterval(interval);
        }
      } catch (err) {
        clearInterval(interval);
        setJobStatus("failed");
      }
    }, 1000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.code.trim()) return;

    if (new Blob([form.code]).size > 65536) {
      setError("Code size exceeds maximum limit of 64KB");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const { data } = await client.post("/reviewer/submit", form);
      if (data.job_id) {
        pollJobStatus(data.job_id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Review submission failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-heading">Code Reviewer Engine</h1>
          <p className="text-slate-400 text-sm">AST structural analysis, empirical sandbox curve fitting & AI diffs</p>
        </div>
        <span className="badge badge-cyan">Async Queue Ready</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Submit Form */}
        <div>
          <form onSubmit={handleSubmit} className="glass-card p-6 space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                {error}
              </div>
            )}

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Domain</label>
                <select
                  value={form.domain}
                  onChange={(e) => setForm({ ...form, domain: e.target.value })}
                  className="code-editor h-10 py-1"
                >
                  <option value="cp">CP (Algorithms)</option>
                  <option value="ml">ML (Data Pipelines)</option>
                  <option value="swe">SWE (Maintainability)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Language</label>
                <select
                  value={form.language}
                  onChange={(e) => setForm({ ...form, language: e.target.value })}
                  className="code-editor h-10 py-1"
                >
                  <option value="python">Python</option>
                  <option value="cpp">C++</option>
                  <option value="java">Java</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Title</label>
                <input
                  type="text"
                  placeholder="Problem title"
                  value={form.problem_title}
                  onChange={(e) => setForm({ ...form, problem_title: e.target.value })}
                  className="code-editor h-10 py-1"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Source Code</label>
              <CodeEditor
                value={form.code}
                onChange={(val) => setForm({ ...form, code: val })}
                language={form.language}
              />
            </div>

            <button
              type="submit"
              disabled={submitting || jobStatus === "processing"}
              className="btn-primary w-full justify-center"
            >
              {submitting || jobStatus === "processing" ? (
                <>
                  <RefreshCw className="animate-spin" size={16} /> Processing Background Review...
                </>
              ) : (
                "Submit for AST Review & Benchmarking"
              )}
            </button>
          </form>

          {/* Past History List */}
          <div className="mt-6">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Submission History</h2>
            <div className="space-y-2">
              {history.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSelected(s)}
                  className="glass-card w-full text-left p-3 flex justify-between items-center hover:border-cyan-500/40 transition"
                >
                  <div>
                    <span className="font-semibold text-sm text-slate-200">{s.problem_title || "Untitled"}</span>
                    <span className="text-xs text-slate-500 ml-2">({s.domain?.toUpperCase() || 'CP'})</span>
                  </div>
                  <span className="text-xs font-mono text-slate-400">
                    {new Date(s.created_at).toLocaleDateString()}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Review Output Panel */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-bold text-white mb-4 font-heading">Diagnostic Results</h2>
          
          {!selected ? (
            <p className="text-slate-400 text-sm">Submit solution or pick past run from history.</p>
          ) : !selected.review ? (
            <p className="text-slate-400 text-sm">Processing background job...</p>
          ) : (
            <div className="space-y-4">
              {/* Empirical Complexity Disagreement Warning Banner */}
              {selected.review.complexity_disagreement && (
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
                  <AlertTriangle className="text-amber-400 shrink-0 mt-0.5" size={20} />
                  <div>
                    <div className="font-bold text-amber-400 text-sm mb-1">Empirical Benchmark Disagreement</div>
                    <p className="text-xs text-amber-200/90">{selected.review.complexity_warning}</p>
                  </div>
                </div>
              )}

              <div className="flex gap-2 flex-wrap">
                <span className="badge badge-cyan">LLM Time: {selected.review.time_complexity || "N/A"}</span>
                {selected.review.measured_complexity && (
                  <span className="badge badge-violet">Empirical Measured: {selected.review.measured_complexity}</span>
                )}
                {selected.review.score != null && (
                  <span className="badge badge-success">Quality Score: {selected.review.score}/100</span>
                )}
              </div>

              {selected.review.suggestions?.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-slate-400 uppercase mb-2">Detected Flaws & Fixes</h3>
                  <div className="space-y-3">
                    {selected.review.suggestions.map((s, i) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-sm">
                        <div className="font-bold text-amber-400">{s.issue}</div>
                        <div className="text-slate-300 text-xs mt-1">{s.why}</div>
                        <div className="text-cyan-400 text-xs mt-1 font-semibold">Fix: {s.fix}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selected.review.better_approach && (
                <div>
                  <h3 className="text-xs font-semibold text-slate-400 uppercase mb-1">Optimal Approach Narrative</h3>
                  <p className="text-sm text-slate-300 leading-relaxed">{selected.review.better_approach}</p>
                </div>
              )}

              {/* AI Unified Git Diff */}
              <DiffViewer diffText={selected.review.code_diff || "--- original.py\n+++ optimal_refactored.py\n@@ -1 +1 @@\n# Refactoring diff auto-generated for optimal O(N) submission"} />

              {/* Interactive AST Visualizer */}
              <AstVisualizer code={selected.code} />
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}