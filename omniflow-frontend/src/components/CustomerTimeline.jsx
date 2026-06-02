import React from 'react';

export default function CustomerTimeline({ events = [] }) {
  return (
    <div className="rounded-xl border border-border bg-white p-5 shadow-soft">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-text uppercase tracking-wider">Customer Timeline</h3>
        <p className="text-xs text-muted">Lifecycle & session history events</p>
      </div>

      {events.length === 0 ? (
        <p className="text-xs text-muted italic">No timeline events captured yet.</p>
      ) : (
        <ol className="relative border-l border-border ml-2.5">
          {events.map((ev, idx) => (
            <li key={idx} className="mb-5 ml-4">
              <span className="absolute -left-1.5 mt-1.5 flex h-3 w-3 items-center justify-center rounded-full bg-white border-2 border-primary" />
              <div className="text-[10px] text-muted font-semibold">{ev.time}</div>
              <div className="mt-0.5 text-sm font-bold text-text">{ev.title}</div>
              {ev.detail && <div className="mt-0.5 text-xs text-muted">{ev.detail}</div>}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
