import React, { useState, useContext } from 'react';
import { postDemo } from '../api/omniflow.js';
import { AppContext } from '../context/AppContext.js';

const SCENARIOS = [
  { key: 'lead_qualification', label: 'Lead Qualification' },
  { key: 'angry_customer', label: 'Angry Customer' },
  { key: 'escalation_demo', label: 'Escalation Flow' },
  { key: 'product_recommendation', label: 'Product Match' },
  { key: 'web_intel', label: 'Web Intelligence' },
];

export default function DemoButtons() {
  const { userId } = useContext(AppContext);
  const [loading, setLoading] = useState(null);

  const run = async (scenario) => {
    setLoading(scenario);
    try {
      await postDemo(scenario, userId);
    } catch (err) {
      console.error('Demo failed', err);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {SCENARIOS.map((s) => (
        <button
          key={s.key}
          onClick={() => run(s.key)}
          disabled={!!loading}
          className={`text-[10px] font-bold uppercase px-3 py-2 rounded-lg transition-all ${
            loading === s.key 
              ? 'bg-primary/20 border border-primary/30 text-primary' 
              : 'border border-border bg-white text-muted hover:border-primary hover:text-primary hover:shadow-soft'
          }`}
        >
          {loading === s.key ? 'Executing...' : s.label}
        </button>
      ))}
    </div>
  );
}
