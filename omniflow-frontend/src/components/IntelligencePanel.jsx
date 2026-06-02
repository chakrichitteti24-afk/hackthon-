import React from 'react';

export default function IntelligencePanel({ memory = {}, currentAgent = 'sales', confidence = 0, isEscalated = false }) {
  const displayAgent = currentAgent 
    ? currentAgent.charAt(0).toUpperCase() + currentAgent.slice(1) + ' Agent'
    : 'No data available';
  
  // Real Data Policy: Extract values from backend user_profile memory
  const intentVal = memory.interests || 'No data available';
  const budgetVal = memory.budget || 'No data available';
  const brandVal = memory.preferred_brand || 'No data available';
  
  const lastSentiment = memory.sentiment_history && memory.sentiment_history.length > 0
    ? memory.sentiment_history[memory.sentiment_history.length - 1]
    : 'No data available';

  const metrics = [
    { label: 'Intent', value: intentVal, badge: false },
    { label: 'Budget', value: budgetVal, badge: false },
    { label: 'Preferred Brand', value: brandVal, badge: false },
    { 
      label: 'Sentiment', 
      value: lastSentiment, 
      badge: lastSentiment !== 'No data available',
      variant: lastSentiment.toLowerCase().includes('positive') ? 'success' : 
               lastSentiment.toLowerCase().includes('negative') || lastSentiment.toLowerCase().includes('angry') ? 'error' : 'warning'
    },
    { 
      label: 'Confidence', 
      value: confidence > 0 ? `${confidence}%` : 'No data available', 
      badge: confidence > 0, 
      variant: 'success' 
    },
    { 
      label: 'Current Agent', 
      value: displayAgent, 
      badge: currentAgent !== '', 
      variant: 'primary' 
    },
    { 
      label: 'Memory Status', 
      value: (memory.interests || memory.budget || memory.preferred_brand) ? 'Memory Synced' : 'No data available', 
      badge: !!(memory.interests || memory.budget || memory.preferred_brand), 
      variant: 'success' 
    },
    { 
      label: 'Escalation Status', 
      value: isEscalated ? '🚨 Escalated' : '✔ Normal', 
      badge: true,
      variant: isEscalated ? 'error' : 'success'
    },
  ];

  const badgeStyles = {
    success: 'bg-success/5 text-success border-success/20',
    error: 'bg-error/5 text-error border-error/20',
    warning: 'bg-warning/5 text-warning border-warning/20',
    primary: 'bg-primary/5 text-primary border-primary/20',
  };

  return (
    <div className="bg-white rounded-xl border border-border p-5 shadow-soft h-full flex flex-col justify-between">
      <div>
        <div className="mb-5 pb-3 border-b border-border">
          <h3 className="text-xs font-bold text-text uppercase tracking-wider">Customer Intelligence</h3>
          <p className="text-[10px] text-muted">Real-time profile heuristics</p>
        </div>

        <div className="space-y-4">
          {metrics.map((item, idx) => (
            <div key={idx} className="flex flex-col gap-1">
              <span className="text-[10px] font-semibold text-muted uppercase tracking-wider">{item.label}</span>
              {item.badge ? (
                <div className="flex">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${badgeStyles[item.variant] || 'bg-gray-50 text-text border-border'}`}>
                    {item.value}
                  </span>
                </div>
              ) : (
                <span className="text-sm font-semibold text-text">
                  {item.value}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-border">
        <div className="flex items-center justify-between text-[10px] font-semibold text-muted uppercase tracking-wider mb-2">
          <span>Grounding Engine</span>
          <span className={(memory.interests || memory.budget) ? 'text-success' : 'text-muted'}>
            {(memory.interests || memory.budget) ? 'Active' : 'No data available'}
          </span>
        </div>
        <div className="h-1.5 w-full bg-border rounded-full overflow-hidden">
          {(memory.interests || memory.budget) ? (
            <div className="h-full bg-success w-[94%] rounded-full" />
          ) : (
            <div className="h-full bg-border w-0" />
          )}
        </div>
      </div>
    </div>
  );
}
