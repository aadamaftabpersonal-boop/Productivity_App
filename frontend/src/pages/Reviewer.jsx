import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import RatingBadge from "../components/RatingBadge";
import CodeEditor from "../components/CodeEditor";

export default function Reviewer() {
  const [form, setForm] = useState({ language: "python", code: "", problem_title: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState(null);

  const loadHistory = () => {
    client.get("/reviewer/history").then((res) => setHistory(res.data));
  };

  useEffect(() => { loadHistory(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const { data } = await client.post("/reviewer/submit", form);
      setSelected(data);
      loadHistory();
    } catch (err) {
      setError(err.response?.data?.detail || "Review failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <h1 className="font-mono text-xl font-bold mb-6">Code Reviewer</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Submit form */}
        <div>
          <form onSubmit={handleSubmit} className="bg-panel border border-border rounded-lg p-5 space-y-4">
            {error && (
              <div className="text-tier-red text-sm bg-tier-red/10 border border-tier-red/30 rounded px-3 py-2">
                {error}
              </div>
            )}
            <div className="flex gap-3">
              <select
                value={form.language}
                onChange={(e) => setForm({ ...form, language: e.target.value })}
                className="bg-base border border-border rounded px-3 py-2 text-sm"
              >
                <option value="python">Python</option>
                <option value="cpp">C++</option>
                <option value="java">Java</option>
              </select>
              <input
                type="text"
                placeholder="Problem title (optional)"
                value={form.problem_title}
                onChange={(e) => setForm({ ...form, problem_title: e.target.value })}
                className="flex-1 bg-base border border-border rounded px-3 py-2 text-sm"
              />
            </div>
            <CodeEditor
            value={form.code}
            onChange={(val) => setForm({ ...form, code: val })}
            language={form.language}
            />
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-tier-blue text-white font-medium rounded px-4 py-2.5 hover:opacity-90 disabled:opacity-50 transition"
            >
              {submitting ? "Reviewing..." : "Submit for review"}
            </button>
          </form>

          {/* History */}
          <div className="mt-6">
            <h2 className="font-mono text-sm text-muted uppercase tracking-wide mb-2">History</h2>
            <ul className="space-y-1.5">
              {history.map((s) => (
                <li key={s.id}>
                  <button
                    onClick={() => setSelected(s)}
                    className="w-full text-left text-sm px-3 py-2 rounded hover:bg-panel border border-border truncate"
                  >
                    {s.problem_title || "Untitled"} — <span className="text-muted text-xs">{new Date(s.created_at).toLocaleDateString()}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Review output */}
        <div className="bg-panel border border-border rounded-lg p-5">
          <h2 className="font-mono text-sm text-muted uppercase tracking-wide mb-3">Review</h2>
          {!selected ? (
            <p className="text-sm text-muted">Submit code or select a past submission to see its review.</p>
          ) : !selected.review ? (
            <p className="text-sm text-muted">No review data for this submission.</p>
          ) : (
            <div className="space-y-4">
              <div className="flex gap-2 flex-wrap">
                <RatingBadge label={`Time: ${selected.review.time_complexity || "N/A"}`} />
                <RatingBadge label={`Space: ${selected.review.space_complexity || "N/A"}`} />
                {selected.review.score != null && <RatingBadge label={`Score: ${selected.review.score}/100`} />}
              </div>

              {selected.review.concepts?.length > 0 && (
                <div>
                  <h3 className="text-xs text-muted uppercase mb-1.5">Concepts</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {selected.review.concepts.map((c, i) => (
                      <span key={i} className="text-xs bg-base border border-border rounded px-2 py-1 font-mono">{c}</span>
                    ))}
                  </div>
                </div>
              )}

              {selected.review.suggestions?.length > 0 && (
                <div>
                  <h3 className="text-xs text-muted uppercase mb-1.5">Suggestions</h3>
                  <div className="space-y-2">
                    {selected.review.suggestions.map((s, i) => (
                      <div key={i} className="bg-base border border-border rounded p-3 text-sm">
                        <div className="font-medium text-tier-orange">{s.issue}</div>
                        <div className="text-muted mt-1">{s.why}</div>
                        <div className="mt-1">{s.fix}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selected.review.better_approach && (
                <div>
                  <h3 className="text-xs text-muted uppercase mb-1.5">Better Approach</h3>
                  <p className="text-sm leading-relaxed">{selected.review.better_approach}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}