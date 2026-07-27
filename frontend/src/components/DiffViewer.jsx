import React from 'react';

export default function DiffViewer({ diffText }) {
  if (!diffText) return null;

  const lines = diffText.split('\n');

  return (
    <div className="glass-card p-4 my-4 font-mono text-sm overflow-x-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-700/50 mb-3">
        <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
          AI Unified Refactoring Diff
        </span>
        <span className="badge badge-cyan">Optimal O(N) Patch</span>
      </div>

      <div className="space-y-1">
        {lines.map((line, idx) => {
          let styleClass = 'text-slate-300';
          let bgClass = '';

          if (line.startsWith('+') && !line.startswith('+++')) {
            styleClass = 'text-emerald-400 font-semibold';
            bgClass = 'bg-emerald-500/10 px-2 rounded';
          } else if (line.startsWith('-') && !line.startswith('---')) {
            styleClass = 'text-rose-400 font-semibold';
            bgClass = 'bg-rose-500/10 px-2 rounded';
          } else if (line.startsWith('@@')) {
            styleClass = 'text-violet-400 italic';
          }

          return (
            <div key={idx} className={`${styleClass} ${bgClass} whitespace-pre`}>
              {line}
            </div>
          );
        })}
      </div>
    </div>
  );
}
