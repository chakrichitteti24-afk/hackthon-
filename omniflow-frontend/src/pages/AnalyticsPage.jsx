import React, { useState, useEffect } from 'react';
import { getAnalytics } from '../api/omniflow.js';
import SentimentChart from '../components/SentimentChart';
import AgentUsageChart from '../components/AgentUsageChart';
import LatencyChart from '../components/LatencyChart';
import KnowledgeUsageChart from '../components/KnowledgeUsageChart';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const data = await getAnalytics();
        if (isMounted) {
          setAnalytics(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchAnalytics();
    return () => { isMounted = false; };
  }, []);

  const agentData = [
    { name: 'Sales', count: analytics?.agent_usage?.sales || 0 },
    { name: 'Support', count: analytics?.agent_usage?.support || 0 },
    { name: 'Insight', count: analytics?.agent_usage?.insight || 0 },
  ];

  return (
    <section className="space-y-6 pb-12 max-w-7xl mx-auto w-full">
      <div className="border-b border-border pb-4">
        <h2 className="text-xl font-bold text-text uppercase tracking-tight">System Analytics</h2>
        <p className="text-xs text-muted">Deep dive metrics into agent routing, user sentiments, and system latency trends</p>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
          <SentimentChart data={analytics?.sentiment_trend || []} />
          <AgentUsageChart data={agentData} />
          <LatencyChart data={analytics?.latency_trend || []} />
          <KnowledgeUsageChart data={analytics?.knowledge_trend || []} />
        </div>
      )}
    </section>
  );
}
