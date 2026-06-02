import React, { useEffect, useState, useContext } from 'react';
import { AppContext } from '../context/AppContext.js';
import { getActivities } from '../api/omniflow.js';

const STATE_LABELS = {
  ingest: 'Analyzing intent',
  routing: 'Routing decision',
  search: 'Searching live web',
  agent_response: 'Generating AI response',
  memory: 'Synchronizing memory',
  sentiment: 'Updating analytics',
  escalation: 'Escalation triggered',
  demo: 'Running demo scenario',
};

export default function ProcessingState({ enabled = true }) {
  const { userId } = useContext(AppContext);
  const [state, setState] = useState({ label: 'Idle', level: 'INFO' });

  useEffect(() => {
    if (!enabled) {
      setState({ label: 'Backend offline', level: 'WARNING' });
      return undefined;
    }

    let mounted = true;
    const fetch = async () => {
      try {
        const resp = await getActivities(userId).catch(() => ({ activities: [] }));
        const last = (resp.activities || []).slice(-1)[0];
        if (!last) return;
        const labelKey = last.category || last.message?.split(' ')?.[0]?.toLowerCase();
        const label = STATE_LABELS[labelKey] || last.message || 'Processing';
        if (mounted) setState({ label, level: last.level || 'INFO' });
      } catch (err) {
        // ignore
      }
    };

    fetch();
    const iv = setInterval(fetch, 1600);
    return () => {
      mounted = false;
      clearInterval(iv);
    };
  }, [enabled, userId]);

  return (
    <div className={`rounded-lg border border-white/5 bg-black/35 p-3 backdrop-blur-md`}> 
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-secondary">Orchestration</p>
          <p className="text-sm font-extrabold text-primary mt-1">{state.label}<span className="ml-2 text-primary/60 animate-pulse">•••</span></p>
        </div>
        <div>
          <span className={`text-xs font-semibold px-2 py-0.5 rounded ${state.level === 'WARNING' ? 'text-[#ffb86b]' : state.level === 'ERROR' ? 'text-[#ff006e]' : 'text-primary/60'}`}>
            {state.level}
          </span>
        </div>
      </div>
    </div>
  );
}
