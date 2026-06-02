import React, { useEffect, useState } from 'react';

export default function MemoryPanel({ memory = {} }) {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    setPulse(true);
    const t = setTimeout(() => setPulse(false), 900);
    return () => clearTimeout(t);
  }, [memory]);

  const items = [
    { label: 'Interested Product', value: memory.interested_product || '—' },
    { label: 'Company Size', value: memory.company_size || '—' },
    { label: 'Budget', value: memory.budget || '—' },
    { label: 'Preferred Platform', value: memory.preferred_platform || '—' },
    { label: 'Previous Issues', value: memory.previous_issues || '—' },
    { label: 'Sentiment Trend', value: memory.sentiment_trend || '—' },
    { label: 'Last Agent Used', value: memory.last_agent || '—' },
    { label: 'Escalation Status', value: memory.escalated ? 'Escalated' : 'Normal' },
  ];

  return (
    <div className={`rounded-lg border bg-card p-4 transition-transform ${pulse ? 'scale-[1.01] shadow-soft' : ''}`} style={{ borderColor: 'var(--border)' }}>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text uppercase tracking-wide">Shared Customer Memory</h3>
        <span className="text-[11px] text-text/60">Synchronized</span>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {items.map((it) => (
          <div key={it.label} className={`flex items-center justify-between gap-4 rounded-md p-3 bg-[var(--bg)] border`} style={{ borderColor: 'var(--border)' }}>
            <div className="text-xs text-text/60">{it.label}</div>
            <div className={`text-sm font-semibold ${it.label === 'Escalation Status' && it.value === 'Escalated' ? 'text-[var(--error)]' : 'text-text'}`}>{it.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
