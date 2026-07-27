import { useEffect, useState } from "react";
import client from "../api/client";
import Layout from "../components/Layout";
import { Trophy, Award, Target, Flame } from "lucide-react";

export default function Leaderboard() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/leaderboard")
      .then((res) => setMembers(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white font-heading flex items-center gap-3">
            <Trophy className="text-amber-400" size={32} /> Tech Club Hall of Fame
          </h1>
          <p className="text-slate-400 text-sm">Gamified leaderboards ranked by mastery velocity & decayed gaps</p>
        </div>
        <span className="badge badge-cyan">Club Competition Active</span>
      </div>

      {loading ? (
        <div className="text-slate-400 text-sm font-mono p-6">Loading Tech Club Rankings...</div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <th className="p-4">Rank</th>
                <th className="p-4">Member</th>
                <th className="p-4 text-center">Mastery Score</th>
                <th className="p-4 text-center">Submissions</th>
                <th className="p-4 text-center">Active Gaps</th>
                <th className="p-4">Badges & Titles</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-sm">
              {members.map((m, idx) => (
                <tr key={m.user_id} className="hover:bg-slate-800/30 transition">
                  <td className="p-4 font-mono font-bold">
                    {idx === 0 ? "🥇 #1" : idx === 1 ? "🥈 #2" : idx === 2 ? "🥉 #3" : `#${idx + 1}`}
                  </td>
                  <td className="p-4">
                    <div className="font-bold text-white">{m.full_name}</div>
                    <div className="text-xs text-slate-500 font-mono">{m.email}</div>
                  </td>
                  <td className="p-4 text-center font-mono font-bold text-cyan-400">
                    {m.mastery_score}%
                  </td>
                  <td className="p-4 text-center font-mono text-slate-300">
                    {m.total_submissions}
                  </td>
                  <td className="p-4 text-center font-mono">
                    <span className={`badge ${m.active_weaknesses === 0 ? 'badge-success' : 'badge-warning'}`}>
                      {m.active_weaknesses} Active
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1.5">
                      {m.badges.map((b, bIdx) => (
                        <span key={bIdx} className="badge badge-violet text-[10px]">
                          <Award size={12} /> {b}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Layout>
  );
}
