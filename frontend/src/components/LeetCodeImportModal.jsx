import React, { useState } from 'react';
import { CheckCircle, Award, Trophy, User } from 'lucide-react';

export default function LeetCodeImportModal({ isOpen, onClose, onImportSuccess, api, initialHandle = '' }) {
  const [handle, setHandle] = React.useState(initialHandle || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

  React.useEffect(() => {
    if (initialHandle) setHandle(initialHandle);
  }, [initialHandle]);

  if (!isOpen) return null;


  const handleImport = async (e) => {
    e.preventDefault();
    if (!handle.trim()) return;

    setLoading(true);
    setError(null);
    setSuccessResult(null);

    try {
      const res = await api.post('/contests/import/leetcode', { handle: handle.trim(), count: 50 });
      setSuccessResult(res.data);
      if (onImportSuccess) onImportSuccess(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import LeetCode submission history');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="saas-card max-w-xl w-full p-6 relative border-amber-500/30">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white font-bold text-lg"
        >
          ✕
        </button>

        <div className="flex items-center gap-2 mb-2">
          <span className="badge badge-amber">LeetCode GraphQL API</span>
        </div>

        <h3 className="text-2xl font-bold text-white mb-2 font-heading">
          Import LeetCode Profile & Submissions
        </h3>
        <p className="text-slate-400 text-sm mb-6">
          Enter your LeetCode username to pull accepted submissions, contest rating, solved stats, and backfill weakness signals.
        </p>

        <form onSubmit={handleImport} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              LeetCode Username / Display Name
            </label>
            <input
              type="text"
              placeholder="e.g. HumVelleHain, 1F4ngx0MHe, neetcode"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              className="code-editor h-12 text-sm"
              required
            />
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold">
              {error}
            </div>
          )}

          {successResult && (
            <div className="p-5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs space-y-4">
              <div className="flex items-center justify-between border-b border-amber-500/20 pb-3">
                <div className="flex items-center gap-3">
                  {successResult.avatar ? (
                    <img src={successResult.avatar} alt="Avatar" className="w-10 h-10 rounded-full border border-amber-400" />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 font-bold">
                      <User size={20} />
                    </div>
                  )}
                  <div>
                    <div className="font-bold text-base text-white">{successResult.real_name}</div>
                    <div className="text-xs text-amber-400 font-mono">@{successResult.resolved_username} • Global Rank #{successResult.ranking}</div>
                  </div>
                </div>
                <span className="badge badge-amber">{successResult.total_solved} Solved</span>
              </div>

              {/* 3 Difficulty Metric Pills */}
              <div className="grid grid-cols-3 gap-2 text-center font-mono">
                <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                  <div className="font-bold text-sm">{successResult.easy_solved}</div>
                  <div className="text-[10px] text-slate-400">Easy</div>
                </div>
                <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
                  <div className="font-bold text-sm">{successResult.medium_solved}</div>
                  <div className="text-[10px] text-slate-400">Medium</div>
                </div>
                <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400">
                  <div className="font-bold text-sm">{successResult.hard_solved}</div>
                  <div className="text-[10px] text-slate-400">Hard</div>
                </div>
              </div>

              {/* Badges Earned */}
              {successResult.badges?.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap">
                  <Award size={14} className="text-amber-400" />
                  {successResult.badges.map((b, i) => (
                    <span key={i} className="badge badge-violet">{b}</span>
                  ))}
                </div>
              )}

              {/* Backfilled Concept Tags */}
              <div>
                <div className="font-semibold text-slate-300 mb-2">Backfilled Concept Weakness Signals:</div>
                <div className="grid grid-cols-2 gap-2">
                  {successResult.flagged_concepts?.map((concept, idx) => (
                    <div key={idx} className="p-2 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between items-center text-xs">
                      <span className="font-mono text-slate-200 font-semibold">{concept.toUpperCase().replace('_', ' ')}</span>
                      <span className="badge badge-emerald">Active</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Close
            </button>
            <button type="submit" disabled={loading} className="btn-primary bg-gradient-to-r from-amber-500 to-orange-600">
              {loading ? 'Querying GraphQL...' : 'Sync LeetCode'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
