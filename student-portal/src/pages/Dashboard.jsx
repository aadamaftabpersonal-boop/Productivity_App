import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import RatingBadge from "../components/RatingBadge";
import { Link } from "react-router-dom";
import { Target, Sparkles, History, Trophy } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    client.get("/dashboard")
      .then((res) => setData(res.data))
      .catch(() => setError("Couldn't load dashboard."));
  }, []);

  if (error) return <Layout><div className="text-tier-red">{error}</div></Layout>;
  if (!data) return <Layout><div className="text-muted font-mono text-sm">Loading...</div></Layout>;

  return (
    <Layout>
      <h1 className="font-mono text-xl font-bold mb-6">
        Welcome{data.user.full_name ? `, ${data.user.full_name}` : ""}
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Active weaknesses */}
        <div className="bg-panel border border-border rounded-lg p-5">
          <h2 className="font-mono text-sm text-muted mb-3 uppercase tracking-wide flex items-center gap-2">
            <Target size={14} /> Active Weaknesses
            </h2>
          {data.active_weaknesses.length === 0 ? (
            <p className="text-sm text-muted">No recurring gaps flagged yet — keep submitting.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {data.active_weaknesses.map((w) => (
                <RatingBadge key={w.concept} label={w.concept} count={w.gap_count} />
              ))}
            </div>
          )}
        </div>

        {/* Resurface item */}
        <div className="bg-panel border border-border rounded-lg p-5">
          <h2 className="font-mono text-sm text-muted mb-3 uppercase tracking-wide">Next Up</h2>
          {data.resurface_item ? (
            <div>
              <p className="text-sm mb-2">{data.resurface_item.instruction}</p>
              {data.resurface_item.url && (
                <a
                  href={data.resurface_item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-tier-blue text-sm hover:underline font-mono"
                >
                  {data.resurface_item.problem_title} →
                </a>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted">Nothing to resurface right now. Check back later.</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Recent submissions */}
        <div className="bg-panel border border-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-mono text-sm text-muted uppercase tracking-wide">Recent Submissions</h2>
            <Link to="/reviewer" className="text-xs text-tier-blue hover:underline">View all</Link>
          </div>
          {data.recent_submissions.length === 0 ? (
            <p className="text-sm text-muted">No submissions yet.</p>
          ) : (
            <ul className="space-y-2">
              {data.recent_submissions.map((s) => (
                <li key={s.id} className="flex items-center justify-between text-sm">
                  <span className="truncate">{s.problem_title || "Untitled"}</span>
                  {s.review?.score != null && (
                    <RatingBadge label={`${s.review.score}/100`} count={s.review.score < 50 ? 8 : s.review.score < 80 ? 3 : 1} />
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Upcoming contests */}
        <div className="bg-panel border border-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-mono text-sm text-muted uppercase tracking-wide">Upcoming Contests</h2>
            <Link to="/contests" className="text-xs text-tier-blue hover:underline">View all</Link>
          </div>
          {data.upcoming_contests.length === 0 ? (
            <p className="text-sm text-muted">No contests synced yet.</p>
          ) : (
            <ul className="space-y-2">
              {data.upcoming_contests.slice(0, 5).map((c) => (
                <li key={c.id} className="flex items-center justify-between text-sm">
                  <span className="truncate">{c.name}</span>
                  <span className="text-xs text-muted font-mono">
                    {new Date(c.start_time).toLocaleDateString()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </Layout>
  );
}