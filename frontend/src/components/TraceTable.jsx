import React, { useState } from 'react';
import { Play, SkipBack, SkipForward, RefreshCw, Cpu } from 'lucide-react';

export default function TraceTable({ code, language, api }) {
  const [tracing, setTracing] = useState(false);
  const [steps, setSteps] = useState([]);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [error, setError] = useState(null);

  const handleRunTrace = async () => {
    setTracing(true);
    setError(null);
    try {
      const res = await api.post('/reviewer/trace', { code, language });
      setSteps(res.data.steps || []);
      setCurrentStepIdx(0);
    } catch (err) {
      setError(err.response?.data?.detail || 'Tracing failed.');
    } finally {
      setTracing(false);
    }
  };

  const currStep = steps[currentStepIdx] || null;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-white font-heading flex items-center gap-2">
            <Cpu size={16} className="text-cyan-400" /> Visual Dry-Run Trace Table
          </h3>
          <p className="text-xs text-slate-400">Concrete-value line execution tracer (max 200 sandboxed steps)</p>
        </div>

        <button
          onClick={handleRunTrace}
          disabled={tracing || !code}
          className="btn-primary py-1.5 px-3 text-xs bg-gradient-to-r from-cyan-500 to-blue-600"
        >
          {tracing ? (
            <>
              <RefreshCw className="animate-spin" size={14} /> Tracing Subprocess...
            </>
          ) : (
            <>
              <Play size={14} /> Run Dry-Run Tracer
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold">
          {error}
        </div>
      )}

      {steps.length === 0 ? (
        <div className="p-12 text-center text-slate-500 font-mono text-xs">
          Click "Run Dry-Run Tracer" above to generate line-by-line variable state snapshots.
        </div>
      ) : (
        <div className="space-y-4">
          {/* Step Control Toolbar */}
          <div className="p-4 rounded-xl bg-slate-950/90 border border-cyan-500/30 flex flex-col sm:flex-row justify-between items-center gap-3">
            <div className="font-mono text-xs text-slate-300">
              Step <span className="text-cyan-400 font-bold">{currentStepIdx + 1}</span> / {steps.length}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentStepIdx(0)}
                disabled={currentStepIdx === 0}
                className="btn-secondary py-1 px-2.5 text-xs"
              >
                Start
              </button>
              <button
                onClick={() => setCurrentStepIdx((prev) => Math.max(0, prev - 1))}
                disabled={currentStepIdx === 0}
                className="btn-secondary py-1 px-2.5 text-xs flex items-center gap-1"
              >
                <SkipBack size={12} /> Prev
              </button>
              <button
                onClick={() => setCurrentStepIdx((prev) => Math.min(steps.length - 1, prev + 1))}
                disabled={currentStepIdx === steps.length - 1}
                className="btn-primary py-1 px-2.5 text-xs flex items-center gap-1"
              >
                Next <SkipForward size={12} />
              </button>
            </div>
          </div>

          {/* Current Step Line Highlight Card */}
          {currStep && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 font-mono text-xs">
              <div className="flex justify-between items-center">
                <span className="badge badge-cyan">Line #{currStep.line_no}</span>
                <span className="text-slate-500 text-[10px]">Step {currStep.step}</span>
              </div>
              <div className="p-2.5 rounded bg-slate-950 text-cyan-300 font-bold border border-slate-800">
                {currStep.code_line || "(empty line)"}
              </div>
            </div>
          )}

          {/* Variable State Snapshot Grid */}
          {currStep && currStep.variables && (
            <div>
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Local Variable State</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 font-mono text-xs">
                {Object.entries(currStep.variables).map(([key, val]) => (
                  <div key={key} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex justify-between items-center">
                    <span className="text-slate-400 font-semibold">{key}:</span>
                    <span className="text-emerald-400 font-bold truncate max-w-[150px]">{val}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
