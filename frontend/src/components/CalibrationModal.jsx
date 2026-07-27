import React, { useState } from 'react';
import { Target, HelpCircle, CheckCircle2 } from 'lucide-react';

export default function CalibrationModal({ isOpen, onSubmitCalibration, onClose }) {
  const [predictedComplexity, setPredictedComplexity] = useState("O(N)");
  const [confidenceLevel, setConfidenceLevel] = useState("medium");

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitCalibration({
      user_predicted_complexity: predictedComplexity,
      confidence_level: confidenceLevel,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="saas-card max-w-md w-full p-6 space-y-5 border-cyan-500/30">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Target size={22} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white font-heading">Metacognitive Calibration Check</h3>
            <p className="text-xs text-slate-400">Self-rate your solution before AST & LLM ground-truth reveal</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 font-sans text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1.5 flex items-center gap-1">
              <HelpCircle size={14} className="text-cyan-400" /> What do you think your Time Complexity is?
            </label>
            <select
              value={predictedComplexity}
              onChange={(e) => setPredictedComplexity(e.target.value)}
              className="code-editor h-11 py-2 px-3 text-xs bg-slate-950 text-slate-200 border-slate-700 w-full"
            >
              <option value="O(1)">O(1) Constant</option>
              <option value="O(log N)">O(log N) Logarithmic</option>
              <option value="O(N)">O(N) Linear</option>
              <option value="O(N log N)">O(N log N) Linearithmic</option>
              <option value="O(N^2)">O(N^2) Quadratic</option>
              <option value="O(2^N)">O(2^N) Exponential</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1.5">How confident are you in this verdict?</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: "high", label: "High", desc: "100% Sure" },
                { id: "medium", label: "Medium", desc: "Fairly Sure" },
                { id: "low", label: "Low", desc: "Uncertain" },
              ].map((c) => (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => setConfidenceLevel(c.id)}
                  className={`p-3 rounded-xl border text-center transition ${
                    confidenceLevel === c.id
                      ? "bg-cyan-500/20 border-cyan-500 text-cyan-300 font-bold"
                      : "bg-slate-950/80 border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  <div className="text-xs">{c.label}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{c.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button type="submit" className="btn-primary w-full bg-gradient-to-r from-cyan-500 to-blue-600">
              <CheckCircle2 size={16} /> Reveal Ground-Truth Review
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
