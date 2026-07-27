import React, { useState } from 'react';
import { Award, Copy, Check, X, Share2, TrendingUp, Cpu, Target } from 'lucide-react';

export default function ShareableReportModal({ isOpen, report, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !report) return null;

  const handleCopyText = () => {
    navigator.clipboard.writeText(report.linkedin_share_text || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="saas-card max-w-lg w-full p-6 space-y-6 border-cyan-500/30 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
        >
          <X size={18} />
        </button>

        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white">
            <Award size={24} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white font-heading">3-Month OA Mastery Report Card</h3>
            <p className="text-xs text-slate-400">Shareable progress artifact for LinkedIn & Resume</p>
          </div>
        </div>

        {/* High-Aesthetic Glassmorphism Badge Card */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 border border-cyan-500/40 relative overflow-hidden space-y-4 shadow-2xl">
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <div>
              <div className="text-lg font-bold text-white">{report.user_name}</div>
              <div className="text-xs text-cyan-400 font-mono">CP Hub • Verified Developer Profile</div>
            </div>
            <span className="badge badge-emerald">Verified Mastery</span>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono uppercase">Rating Delta</div>
              <div className="text-base font-extrabold text-emerald-400 font-mono mt-0.5">{report.rating_delta}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono uppercase">Gaps Fixed</div>
              <div className="text-base font-extrabold text-cyan-400 font-mono mt-0.5">+{report.resolved_weakness_count}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div className="text-[10px] text-slate-400 font-mono uppercase">Submissions</div>
              <div className="text-base font-extrabold text-violet-400 font-mono mt-0.5">{report.total_submissions}</div>
            </div>
          </div>

          <div>
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Mastered Canonical Patterns</div>
            <div className="flex flex-wrap gap-1.5">
              {report.mastered_concepts?.map((c, i) => (
                <span key={i} className="badge badge-cyan text-xs">
                  {c}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Copy Share Text Block */}
        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">LinkedIn / Resume Share Post Text</label>
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 max-h-32 overflow-y-auto whitespace-pre-wrap">
            {report.linkedin_share_text}
          </div>
        </div>

        <div className="flex gap-3">
          <button onClick={handleCopyText} className="btn-primary w-full bg-gradient-to-r from-cyan-500 to-blue-600">
            {copied ? <Check size={16} /> : <Copy size={16} />}
            {copied ? "Copied to Clipboard!" : "Copy LinkedIn Share Post"}
          </button>
        </div>
      </div>
    </div>
  );
}
