import React from 'react';
import { Trophy, AlertTriangle, CheckCircle, X } from 'lucide-react';

export default function PostMortemModal({ isOpen, postMortem, onClose }) {
  if (!isOpen || !postMortem) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="saas-card max-w-xl w-full p-6 space-y-5 border-amber-500/30 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
        >
          <X size={18} />
        </button>

        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Trophy size={24} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white font-heading">Post-Contest Auto Post-Mortem</h3>
            <p className="text-xs text-slate-400">Empirical diagnostic breakdown of your tracked contest performance</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="p-4 rounded-xl bg-slate-950/90 border border-emerald-500/30">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1">
              <CheckCircle size={14} /> Solved Problems
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">{postMortem.solved_count}</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/90 border border-rose-500/30">
            <div className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-1 flex items-center gap-1">
              <AlertTriangle size={14} /> Time / Penalty Loss
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">{postMortem.failed_count}</div>
          </div>
        </div>

        {/* Concept Gaps Flagged */}
        <div>
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Key Concept Gaps Flagged Today</div>
          <div className="flex flex-wrap gap-2">
            {postMortem.concept_gaps?.map((gap, idx) => (
              <span key={idx} className="badge badge-amber text-xs py-1 px-3">
                {gap}
              </span>
            ))}
          </div>
        </div>

        {/* Rank Impact Narrative */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5 font-sans">
          <div className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle size={14} /> What Actually Cost You Rank Today
          </div>
          <p className="text-xs text-slate-200 leading-relaxed">{postMortem.rank_impact_narrative}</p>
        </div>

        <div className="pt-2">
          <button onClick={onClose} className="btn-primary w-full bg-gradient-to-r from-amber-500 to-orange-600">
            Acknowledge & Schedule Resurfacing Reps →
          </button>
        </div>
      </div>
    </div>
  );
}
