import React from 'react';
import KPIStatCard from './KPIStatCard';

export default function KPIGrid({ totals = {} }) {
  const { 
    totalSessions = 0, 
    escalations = 0, 
    avgConfidence = 0, 
    avgLatency = 0, 
    csat = 0 
  } = totals;

  const confidenceValue = avgConfidence > 0 ? `${avgConfidence}%` : 'No data available';
  const latencyValue = avgLatency > 0 ? `${avgLatency} ms` : 'No data available';
  const csatValue = csat > 0 ? `${csat.toFixed(2)} / 5` : 'No data available';

  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
      <KPIStatCard
        title="Total Conversations"
        value={totalSessions}
        subtitle="Active & historic sessions"
        hint="Live database count"
        trend="neutral"
      />

      <KPIStatCard
        title="Knowledge Confidence"
        value={confidenceValue}
        subtitle="Factual grounding accuracy"
        hint={avgConfidence > 0 ? 'Verified' : 'No data'}
        trend={avgConfidence > 0 ? 'up' : 'neutral'}
      />

      <KPIStatCard
        title="Escalations"
        value={escalations}
        subtitle="Active support triggers"
        hint={escalations > 0 ? 'Urgent attention' : 'All clear'}
        trend={escalations > 0 ? 'down' : 'up'}
      />

      <KPIStatCard
        title="Average Latency"
        value={latencyValue}
        subtitle="Agent response speed"
        hint="Engine performance"
        trend={avgLatency > 0 && avgLatency < 200 ? 'up' : 'neutral'}
      />

      <KPIStatCard
        title="Customer Satisfaction"
        value={csatValue}
        subtitle="Sentiment satisfaction score"
        hint={csat > 0 ? 'Real CSAT average' : 'No data'}
        trend={csat > 3.5 ? 'up' : 'neutral'}
      />
    </div>
  );
}
