import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import { Trophy, RefreshCw, ExternalLink, Bookmark } from "lucide-react";

const PLATFORM_BADGE = {
  codeforces: "badge-cyan",
  leetcode: "badge-amber",
};

export default function Contests() {
  const [upcoming, setUpcoming] = useState([]);
  const [tracked, setTracked] = useState([]);
  const [syncing, setSyncing] = useState(false);

  const load = () => {
    client.get("/contests/upcoming").then((res) => setUpcoming(res.data)).catch(() => {});
    client.get("/contests/tracked").then((res) => setTracked(res.data)).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await client.post("/contests/sync");
      load();
    } finally {
      setSyncing(false);
    }
  };

  const track = async (id) => {
    await client.post("/contests/track", { contest_id: id });
    load();
  };

  const untrack = async (id) => {
    await client.delete(`/contests/track/${id}`);
    load();
  };

  const trackedIds = new Set(tracked.map((c) => c.id));

  return (
    <Layout>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-heading flex items-center gap-3">
            <Trophy className="text-amber-400" size={30} /> Competitive Contests Hub
          </h1>
          <p className="text-slate-400 text-sm">Real-time Codeforces & LeetCode contest tracking</p>
        </div>

        <button onClick={handleSync} disabled={syncing} className="btn-primary">
          <RefreshCw size={15} className={syncing ? "animate-spin" : ""} />
          {syncing ? "Syncing Platforms..." : "Sync Contest Schedule"}
        </button>
      </div>

      <div className="saas-card overflow-hidden">
        {upcoming.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No upcoming contests synced yet. Click "Sync Contest Schedule" above.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {upcoming.map((c) => (
              <div key={c.id} className="p-5 flex items-center justify-between hover:bg-slate-900/40 transition">
                <div className="flex items-center gap-4">
                  <span className={`badge ${PLATFORM_BADGE[c.platform] || "badge-violet"}`}>
                    {c.platform}
                  </span>
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-bold text-white text-base hover:text-cyan-400 transition flex items-center gap-1.5"
                  >
                    {c.name} <ExternalLink size={14} className="text-slate-500" />
                  </a>
                </div>

                <div className="flex items-center gap-6">
                  <span className="text-xs text-slate-400 font-mono">
                    {new Date(c.start_time).toLocaleString()}
                  </span>

                  <button
                    onClick={() => (trackedIds.has(c.id) ? untrack(c.id) : track(c.id))}
                    className={`btn-secondary text-xs py-1.5 px-3.5 ${
                      trackedIds.has(c.id) ? "border-emerald-500/40 text-emerald-400 bg-emerald-500/10" : ""
                    }`}
                  >
                    <Bookmark size={14} />
                    {trackedIds.has(c.id) ? "Tracked" : "Track"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}