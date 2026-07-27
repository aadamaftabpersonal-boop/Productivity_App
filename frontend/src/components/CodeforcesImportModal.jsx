import React, { useState } from 'react';

export default function CodeforcesImportModal({ isOpen, onClose, onImportSuccess, api }) {
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

    try:
      const res = await api.post('/contests/import/codeforces', { handle: handle.trim(), count: 50 });
      setSuccessResult(res.data);
      if (onImportSuccess) onImportSuccess(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import Codeforces history');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md p-4">
      <div className="glass-card max-w-md w-full p-6 relative border-cyan-500/30">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white font-bold"
        >
          ✕
        </button>

        <h3 className="text-2xl font-bold text-white mb-2 font-heading">
          Import Codeforces History
        </h3>
        <p className="text-slate-400 text-sm mb-6">
          Enter your Codeforces handle to pull submission history and backfill your weakness profile retroactively.
        </p>

        <form onSubmit={handleImport} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Codeforces Handle
            </label>
            <input
              type="text"
              placeholder="e.g. tourist, Benq"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              className="code-editor h-11 text-base"
              required
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          {successResult && (
            <div className="p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-sm space-y-1">
              <div className="font-semibold">Import Complete!</div>
              <div>Submissions Imported: {successResult.submissions_imported}</div>
              <div>Weaknesses Backfilled: {successResult.weaknesses_backfilled}</div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Close
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Importing...' : 'Sync History'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
