import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";

const PLATFORM_COLOR = {
  codeforces: "text-tier-blue border-tier-blue/40 bg-tier-blue/10",
  leetcode: "text-tier-orange border-tier-orange/40 bg-tier-orange/10",
};

export default function Contests() {
  const [upcoming, setUpcoming] = useState([]);
  const [tracked, setTracked] = useState([]);
  const [syncing, setSyncing] = useState(false);

  const load = () => {
    client.get("/contests/upcoming").then((res) => setUpcoming(res.data));
    client.get("/contests/tracked").then((res) => setTracked(res.data));
  };

  useEffect(() => { load(); }, []);

  const handleSync = async () => {
    setSyncing(true);
    await client.post("/contests/sync");
    load();
    setSyncing(false);
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
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-mono text-xl font-bold">Contests</h1>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="text-sm bg-panel border border-border rounded px-3 py-1.5 hover:bg-border/30 transition font-mono disabled:opacity-50"
        >
          {syncing ? "Syncing..." : "↻ Sync"}
        </button>
      </div>

      <div className="bg-panel border border-border rounded-lg divide-y divide-border">
        {upcoming.length === 0 ? (
          <p className="text-sm text-muted p-5">No contests found. Try syncing.</p>
        ) : (
          upcoming.map((c) => (
            <div key={c.id} className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <span className={`text-xs px-2 py-1 rounded border font-mono ${PLATFORM_COLOR[c.platform] || ""}`}>
                  {c.platform}
                </span>
                <a href={c.url} target="_blank" rel="noreferrer" className="text-sm hover:underline">
                  {c.name}
                </a>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-xs text-muted font-mono">
                  {new Date(c.start_time).toLocaleString()}
                </span>
                <button
                  onClick={() => (trackedIds.has(c.id) ? untrack(c.id) : track(c.id))}
                  className={`text-xs px-2.5 py-1 rounded border font-mono transition ${
                    trackedIds.has(c.id)
                      ? "border-tier-green/40 text-tier-green bg-tier-green/10"
                      : "border-border text-muted hover:text-text"
                  }`}
                >
                  {trackedIds.has(c.id) ? "Tracked" : "Track"}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </Layout>
  );
}