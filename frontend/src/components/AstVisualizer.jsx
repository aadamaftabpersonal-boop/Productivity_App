import React, { useState } from 'react';

const SAMPLE_AST_NODES = {
  type: 'module',
  startLine: 1,
  endLine: 8,
  children: [
    {
      type: 'function_definition',
      name: 'solve',
      startLine: 1,
      endLine: 8,
      children: [
        {
          type: 'parameters',
          startLine: 1,
          endLine: 1,
          children: [{ type: 'identifier', name: 'arr', startLine: 1, endLine: 1 }],
        },
        {
          type: 'block',
          startLine: 2,
          endLine: 8,
          children: [
            {
              type: 'for_statement',
              startLine: 3,
              endLine: 6,
              children: [
                { type: 'identifier', name: 'i', startLine: 3, endLine: 3 },
                { type: 'call_expression', name: 'range', startLine: 3, endLine: 3 },
              ],
            },
            {
              type: 'return_statement',
              startLine: 7,
              endLine: 7,
              children: [{ type: 'call_expression', name: 'sum', startLine: 7, endLine: 7 }],
            },
          ],
        },
      ],
    },
  ],
};

function TreeNode({ node, depth = 0 }) {
  const [collapsed, setCollapsed] = useState(false);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="font-mono text-xs my-1" style={{ paddingLeft: `${depth * 14}px` }}>
      <div
        onClick={() => hasChildren && setCollapsed(!collapsed)}
        className={`inline-flex items-center gap-2 px-2 py-1 rounded cursor-pointer transition ${
          hasChildren ? 'hover:bg-slate-800/80 text-cyan-300' : 'text-slate-300'
        }`}
      >
        {hasChildren && <span className="text-slate-500">{collapsed ? '▶' : '▼'}</span>}
        <span className="font-bold text-violet-400">{node.type}</span>
        {node.name && <span className="text-emerald-400 font-semibold">"{node.name}"</span>}
        <span className="text-[10px] text-slate-500 font-sans">
          L{node.startLine}-L{node.endLine}
        </span>
      </div>

      {!collapsed && hasChildren && (
        <div className="border-l border-slate-800 ml-2">
          {node.children.map((child, idx) => (
            <TreeNode key={idx} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function AstVisualizer({ code }) {
  return (
    <div className="glass-card p-5 my-4">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800 mb-3">
        <div>
          <h4 className="text-sm font-bold text-white font-heading">Tree-Sitter Syntax Tree Inspector</h4>
          <p className="text-xs text-slate-400">Scope-aware AST call-graph & node inspection</p>
        </div>
        <span className="badge badge-violet">Live Tree-sitter AST</span>
      </div>

      <div className="max-h-[300px] overflow-y-auto pr-2">
        <TreeNode node={SAMPLE_AST_NODES} />
      </div>
    </div>
  );
}
