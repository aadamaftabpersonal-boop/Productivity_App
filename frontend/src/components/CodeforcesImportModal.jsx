import React, { useState } from 'react';
import { CheckCircle } from 'lucide-react';

export default function CodeforcesImportModal({ isOpen, onClose, onImportSuccess, api, initialHandle = '' }) {
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
      const res = await api.post('/contests/import/codeforces', { handle: handle.trim(), count: 50 });
      setSuccessResult(res.data);
      if (onImportSuccess) onImportSuccess(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import Codeforces submission history');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="saas-card max-w-xl w-full p-6 relative border-cyan-500/30">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white font-bold text-lg"
        >
          ✕
        </button>

        <div className="flex items-center gap-2 mb-2">
          <span className="badge badge-cyan">Codeforces Official API</span>
        </div>

        <h3 className="text-2xl font-bold text-white mb-2 font-heading">
          Import Codeforces Submissions
        </h3>
        <p className="text-slate-400 text-sm mb-6">
          Enter your Codeforces handle to pull public submission history and backfill concept weaknesses into your profile.
        </p>

        <form onSubmit={handleImport} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Codeforces Handle
            </label>
            <input
              type="text"
              placeholder="e.g. tourist, Benq, Geothermal"
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
            <div className="p-5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-200 text-xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="font-bold text-sm text-cyan-400 flex items-center gap-1.5">
                  <CheckCircle size={16} /> Codeforces Sync Complete for "{successResult.handle}"
                </div>
                <span className="badge badge-cyan">{successResult.submissions_imported} Submissions Processed</span>
              </div>

              <div className="font-semibold text-slate-300">Fetched Submissions & Backfilled Concepts:</div>

              <div className="space-y-1.5 max-h-[160px] overflow-y-auto pr-1">
                {successResult.flagged_concepts?.length > 0 ? (
                  successResult.flagged_concepts.map((concept, idx) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between items-center text-xs">
                      <span className="font-mono text-slate-200 font-semibold">{concept.toUpperCase().replace('_', ' ')}</span>
                      <span className="badge badge-emerald">Weakness Signal Backfilled</span>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-400">All submissions analyzed — zero gap flags detected.</div>
                )}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Close
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Querying Codeforces API...' : 'Sync Codeforces'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
