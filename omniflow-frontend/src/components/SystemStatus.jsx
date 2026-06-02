import React from 'react';

export default function SystemStatus({ statuses = [] }) {
  return (
    <div className="rounded-lg border border-border bg-card p-2 flex flex-wrap gap-2">
      {statuses.map((s) => (
        <div key={s.key} className="flex items-center gap-2 rounded-md bg-[rgba(16,24,40,0.02)] px-3 py-1 border" style={{ borderColor: 'var(--border)' }}>
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ background: s.ok ? 'var(--success)' : 'var(--error)', boxShadow: s.ok ? '0 0 8px rgba(16,185,129,0.12)' : '0 0 8px rgba(239,68,68,0.12)' }}
          />
          <div className="text-xs text-text">{s.label}</div>
        </div>
      ))}
    </div>
  );
}
