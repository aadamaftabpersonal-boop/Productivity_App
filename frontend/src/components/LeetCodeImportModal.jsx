import React, { useState } from 'react';

export default function LeetCodeImportModal({ isOpen, onClose, onImportSuccess, api }) {
  const [handle, setHandle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4">
      <div className="saas-card max-w-md w-full p-6 relative border-amber-500/30">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white font-bold"
        >
          ✕
        </button>

        <div className="flex items-center gap-2 mb-2">
          <span className="badge badge-amber">LeetCode GraphQL API</span>
        </div>

        <h3 className="text-2xl font-bold text-white mb-2 font-heading">
          Import LeetCode Submissions
        </h3>
        <p className="text-slate-400 text-sm mb-6">
          Enter your LeetCode username to pull recent accepted submissions and backfill your weakness profile.
        </p>

        <form onSubmit={handleImport} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              LeetCode Username
            </label>
            <input
              type="text"
              placeholder="e.g. neetcode, alex_dev"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              className="code-editor h-12 text-sm"
              required
            />
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
              {error}
            </div>
          )}

          {successResult && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs space-y-1">
              <div className="font-bold text-sm">LeetCode Sync Complete!</div>
              <div>Submissions Processed: {successResult.submissions_imported}</div>
              <div>Weakness Tags Backfilled: {successResult.weaknesses_backfilled}</div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
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
