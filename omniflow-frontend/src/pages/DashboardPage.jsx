import { useContext, useEffect, useState } from 'react';
import { getSession, checkHealth, postEscalate, getStatus, getAnalytics } from '../api/omniflow.js';
import { AppContext } from '../context/AppContext.js';
import { Link } from 'react-router-dom';

import KPIGrid from '../components/KPIGrid';
import SentimentChart from '../components/SentimentChart';
import AgentUsageChart from '../components/AgentUsageChart';
import LatencyChart from '../components/LatencyChart';
import KnowledgeUsageChart from '../components/KnowledgeUsageChart';
import DemoButtons from '../components/DemoButtons';
import ProcessingState from '../components/ProcessingState';

export default function DashboardPage() {
  const { userId, setUserId } = useContext(AppContext);
  const [health, setHealth] = useState('checking');
  const [backendSessions, setBackendSessions] = useState([]);
  const [statusInfo, setStatusInfo] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      try {
        const healthResult = await checkHealth().catch(() => ({ status: 'offline' }));
        const nextHealth = healthResult.status || 'offline';
        if (isMounted) {
          setHealth(nextHealth);
        }

        if (nextHealth !== 'ok') {
          if (isMounted) {
            setBackendSessions([]);
            setStatusInfo(null);
            setAnalytics(null);
            setError('');
          }
          return;
        }

        // Fetch real aggregated analytics
        const analyticsData = await getAnalytics().catch(() => null);
        if (isMounted && analyticsData) {
          setAnalytics(analyticsData);
        }

        let savedIds = [];
        try {
          const saved = localStorage.getItem('omniflow_sessions');
          savedIds = saved ? JSON.parse(saved) : [];
        } catch (e) {
          console.error(e);
        }

        if (!savedIds.includes(userId)) {
          savedIds.push(userId);
        }

        const sessionPromises = savedIds.map(async (id) => {
          try {
            const data = await getSession(id);
            return data;
          } catch {
            return {
              user_id: id,
              messages: [],
              sentiment_score: 5.0,
              escalated: false,
            };
          }
        });

        const results = await Promise.all(sessionPromises);
        if (isMounted) {
          // Filter out sessions that have no messages to ensure we only show real active sessions
          const realSessions = results.filter(s => s.messages && s.messages.length > 0);
          setBackendSessions(realSessions);
          setError('');
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Error updating dashboard analytics.');
        }
      }
    };

    loadDashboard();
    const interval = setInterval(loadDashboard, 4000);

    let mountedStatus = true;
    const loadStatus = async () => {
      try {
        const stat = await getStatus();
        if (mountedStatus) setStatusInfo(stat);
      } catch (e) {}
    };
    loadStatus();
    const statusIv = setInterval(loadStatus, 5000);

    return () => {
      isMounted = false;
      clearInterval(interval);
      mountedStatus = false;
      clearInterval(statusIv);
    };
  }, [userId]);

  const processSession = (session) => {
    let agent = 'sales';
    const lastAssistantMsg = [...(session.messages || [])]
      .reverse()
      .find((m) => m.role === 'assistant');
    if (lastAssistantMsg && lastAssistantMsg.agent_type) {
      agent = lastAssistantMsg.agent_type;
    }

    return {
      user_id: session.user_id,
      messages: session.messages || [],
      messageCount: session.messages?.length || 0,
      sentiment_score: session.sentiment_score ?? 5.0,
      escalated: session.escalated ?? false,
      agent_type: agent,
    };
  };

  const activeBackendSessions = backendSessions.map(processSession);
  const allSessions = activeBackendSessions;

  const totalSessions = analytics?.total_conversations || allSessions.length;
  const escalationsToday = analytics?.escalation_count || allSessions.filter((s) => s.escalated).length;
  const avgLatency = analytics?.average_response_ms || 0;
  const avgConfidence = analytics?.average_confidence || 0;
  const csat = analytics?.customer_satisfaction || 0;

  const agentData = [
    { name: 'Sales', count: analytics?.agent_usage?.sales || 0 },
    { name: 'Support', count: analytics?.agent_usage?.support || 0 },
    { name: 'Insight', count: analytics?.agent_usage?.insight || 0 },
  ];

  const getSentimentText = (score) => {
    if (score <= 3.5) return 'Positive';
    if (score <= 6.5) return 'Neutral';
    if (score <= 8.0) return 'Negative';
    return 'Angry';
  };

  const getSentimentBadgeStyles = (text) => {
    switch (text.toLowerCase()) {
      case 'positive':
        return 'bg-success/5 text-success border-success/20';
      case 'neutral':
        return 'bg-warning/5 text-warning border-warning/20';
      case 'negative':
        return 'bg-error/5 text-error border-error/20';
      case 'angry':
      default:
        return 'bg-error/10 text-error border-error/30';
    }
  };

  const handleEscalateClick = async (targetUserId) => {
    setActionLoading((prev) => ({ ...prev, [targetUserId]: true }));
    try {
      await postEscalate(targetUserId);
      setBackendSessions((prev) =>
        prev.map((s) => (s.user_id === targetUserId ? { ...s, escalated: true } : s))
      );
    } catch (err) {
      console.error('Escalation failed', err);
    } finally {
      setActionLoading((prev) => ({ ...prev, [targetUserId]: false }));
    }
  };

  return (
    <section className="space-y-6 pb-12 max-w-7xl mx-auto w-full">
      
      {/* Title block */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-text uppercase tracking-tight">
            Enterprise Dashboard
          </h2>
          <p className="text-xs text-muted">Global multi-agent performance metrics & telemetry logs</p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
          <span className="font-semibold text-muted uppercase">Health Status:</span>
          <span className={`font-bold px-2.5 py-0.5 rounded border ${
            health === 'ok' 
              ? 'bg-success/5 text-success border-success/20' 
              : 'bg-error/5 text-error border-error/20'
          }`}>
            {health === 'ok' ? 'Online' : 'Offline'}
          </span>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-error/20 bg-error/5 px-4 py-3 text-xs font-semibold text-error">
          System Notice: {error}
        </div>
      )}

      {/* KPI Stats Grid */}
      <KPIGrid
        totals={{
          totalSessions,
          escalations: escalationsToday,
          avgConfidence,
          avgLatency,
          csat,
        }}
      />

      {/* Simulator actions toolbar */}
      <div className="bg-white border border-border rounded-xl p-4 shadow-soft flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-muted uppercase tracking-wider">Test Scenario Simulator:</span>
          <DemoButtons />
        </div>
        <ProcessingState enabled={health === 'ok'} />
      </div>

      {/* Grid of the 4 required charts */}
      <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
        <SentimentChart data={analytics?.sentiment_trend || []} />
        <AgentUsageChart data={agentData} />
        <LatencyChart data={analytics?.latency_trend || []} />
        <KnowledgeUsageChart data={analytics?.knowledge_trend || []} />
      </div>

      {/* Sessions Management Table */}
      <div className="bg-white rounded-xl border border-border p-5 shadow-soft overflow-hidden">
        <div className="mb-4">
          <h3 className="text-sm font-bold text-text uppercase tracking-wider">
            Active Multi-Agent Orchestration Sessions
          </h3>
          <p className="text-xs text-muted">Browse live agent logs and escalation status</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border text-xs font-semibold text-muted uppercase tracking-wider">
                <th className="py-3 px-4 font-semibold">User Identity</th>
                <th className="py-3 px-4 font-semibold">Assigned Agent</th>
                <th className="py-3 px-4 font-semibold">Log Count</th>
                <th className="py-3 px-4 font-semibold text-center">Avg Sentiment</th>
                <th className="py-3 px-4 font-semibold text-center">Status</th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-sm">
              {allSessions.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-xs font-semibold text-muted italic">
                    No active orchestration sessions found. Start a conversation in the Workspace to populate logs.
                  </td>
                </tr>
              ) : (
                allSessions.map((session) => {
                  const sentimentText = getSentimentText(session.sentiment_score);
                  const isEscalated = session.escalated;
                  const isCurrent = session.user_id === userId;

                  return (
                    <tr key={session.user_id} className="hover:bg-bg/40 transition duration-150">
                      <td className="py-3.5 px-4 font-bold text-text truncate max-w-[200px]">
                        {isCurrent ? (
                          <span className="flex items-center gap-1.5 text-primary">
                            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-ping" />
                            {session.user_id}
                            <span className="text-[9px] bg-primary/5 border border-primary/20 px-1.5 py-0.2 rounded font-semibold uppercase">
                              active
                            </span>
                          </span>
                        ) : (
                          session.user_id
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`text-xs uppercase font-semibold px-2.5 py-0.5 rounded border ${
                          session.agent_type === 'sales'
                            ? 'border-primary/20 bg-primary/5 text-primary'
                            : session.agent_type === 'support'
                            ? 'border-secondary/20 bg-secondary/5 text-secondary'
                            : 'border-warning/20 bg-warning/5 text-warning'
                        }`}>
                          {session.agent_type}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-text font-bold">
                        {session.messageCount} messages
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded border ${getSentimentBadgeStyles(sentimentText)}`}>
                          {sentimentText} ({session.sentiment_score.toFixed(1)})
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`text-xs uppercase font-bold px-2 py-0.5 rounded border ${
                          isEscalated
                            ? 'bg-error/5 text-error border-error/20'
                            : 'bg-success/5 text-success border-success/20'
                        }`}>
                          {isEscalated ? '🚨 Escalated' : '✔ Normal'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => handleEscalateClick(session.user_id)}
                            disabled={isEscalated || actionLoading[session.user_id]}
                            className={`text-xs px-2.5 py-1 rounded border transition ${
                              isEscalated
                                ? 'border-border text-muted bg-bg/50 cursor-not-allowed'
                                : 'border-error/30 text-error hover:bg-error/5'
                            }`}
                          >
                            {actionLoading[session.user_id] ? '...' : 'Escalate'}
                          </button>
                          <button
                            type="button"
                            onClick={() => setUserId(session.user_id)}
                            className="text-xs px-2.5 py-1 rounded border border-primary text-primary hover:bg-primary/5 transition font-semibold"
                          >
                            <Link to="/">View</Link>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

    </section>
  );
}
