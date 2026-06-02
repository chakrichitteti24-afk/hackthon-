import React, { useEffect, useState, useContext } from 'react';
import { AppContext } from '../context/AppContext.js';
import { getActivities } from '../api/omniflow.js';

// Mapping of orchestration stages
const STAGES = [
  'Intent Analysis',
  'Knowledge Retrieval',
  'Agent Activation',
  'Response Generated',
];

function sanitizeActivities(raw = []) {
  // Keep only high-level orchestration markers and ignore internal/debug logs
  // We map any acceptable activity.message that mentions a stage to that stage.
  const lower = raw.map((a) => ({ ...a, text: (a.message || '').toLowerCase() }));
  const out = new Set();

  for (const a of lower) {
    if (!a.text) continue;
    if (a.text.includes('intent')) out.add('Intent Analysis');
    if (a.text.includes('knowledge') || a.text.includes('retrieve') || a.text.includes('faiss') || a.text.includes('wikipedia')) out.add('Knowledge Retrieval');
    if (a.text.includes('agent') || a.text.includes('routing') || a.text.includes('activate')) out.add('Agent Activation');
    if (a.text.includes('response') || a.text.includes('generated') || a.text.includes('reply')) out.add('Response Generated');
  }

  // Return array preserving the canonical stage order
  return STAGES.filter((s) => out.has(s));
}

export default function ActivityFeed({ initialEvents = [], enabled = true }) {
  const { userId } = useContext(AppContext);
  const [completed, setCompleted] = useState([]);
  const [active, setActive] = useState(null);

  useEffect(() => {
    if (!enabled) return undefined;
    let mounted = true;

    const fetch = async () => {
      try {
        const resp = await getActivities(userId).catch(() => ({ activities: [] }));
        if (!mounted) return;

        // sanitize and map to high-level stages
        const stagesSeen = sanitizeActivities(resp.activities || []);

        // Determine completed and active steps
        const comp = [];
        for (const s of STAGES) {
          if (stagesSeen.includes(s)) comp.push(s);
        }

        // active is the next stage not yet completed, or null if all done
        const next = STAGES.find((s) => !comp.includes(s)) || null;

        // Keep max 4 stages (canonical order)
        setCompleted(comp.slice(0, 4));
        setActive(next);
      } catch (e) {
        // do not surface errors; silence per requirements
      }
    };

    fetch();
    const iv = setInterval(fetch, 1200);
    return () => { mounted = false; clearInterval(iv); };
  }, [enabled, userId]);

  // render the compact vertical timeline
  return (
    <div className="rounded-lg border bg-card p-3" style={{ borderColor: 'var(--border)' }}>
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text uppercase tracking-wide">AI Workflow</h3>
        <span className="text-[11px] text-text/60">Live</span>
      </div>

      <div className="flex flex-col gap-3">
        {STAGES.map((stage, idx) => {
          const isDone = completed.includes(stage);
          const isActive = active === stage && !isDone;
          return (
            <div key={stage} className="flex items-center gap-3">
              <div className="flex items-center justify-center h-6 w-6 rounded-full">
                {isDone ? (
                  <svg className="h-5 w-5 text-[var(--success)]" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                ) : isActive ? (
                  <div className="h-4 w-4 rounded-full border-2 border-[var(--primary)] flex items-center justify-center animate-pulse">
                    <div className="h-2 w-2 rounded-full bg-[var(--primary)]" />
                  </div>
                ) : (
                  <div className="h-3 w-3 rounded-full border border-border bg-[var(--bg)]" />
                )}
              </div>

              <div className="flex flex-col">
                <div className={`text-sm font-medium ${isDone ? 'text-text' : 'text-text/70'}`}>{stage}</div>
                {isActive && <div className="text-xs text-text/50">(Active)</div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
