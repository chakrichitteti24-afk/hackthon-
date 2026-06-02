import { useContext, useEffect, useState } from 'react';
import { getSession } from '../api/omniflow.js';
import { AppContext } from '../context/AppContext.js';
import { useNavigate } from 'react-router-dom';

export default function SessionsPage() {
  const { userId, setUserId } = useContext(AppContext);
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Search & filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [agentFilter, setAgentFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sentimentFilter, setSentimentFilter] = useState('all');

  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    const loadSessions = async () => {
      try {
        setIsLoading(true);
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

        const processed = results.map((session) => {
          let agent = 'sales';
          if (session.user_id === userId) {
            const lastAssistantMsg = [...(session.messages || [])]
              .reverse()
              .find((m) => m.role === 'assistant');
            if (lastAssistantMsg && lastAssistantMsg.content.includes('sentiment')) {
              agent = 'insight';
            } else if (session.messages?.length > 0) {
              agent = 'support';
            }
          } else {
            agent = session.agent_type || 'sales';
          }

          return {
            ...session,
            agent_type: agent,
            messageCount: session.messages?.length || 0,
            lastActivity: session.messages?.length > 0 
              ? new Date(session.messages[session.messages.length - 1].timestamp || Date.now()).toLocaleTimeString()
              : 'Idle',
          };
        });

        const mockSessions = [
          {
            user_id: 'user_sales_pro',
            messages: Array(14).fill(null),
            agent_type: 'sales',
            sentiment_score: 2.1,
            escalated: false,
            messageCount: 14,
            lastActivity: '12:35 PM',
          },
          {
            user_id: 'user_support_help',
            messages: Array(8).fill(null),
            agent_type: 'support',
            sentiment_score: 4.8,
            escalated: false,
            messageCount: 8,
            lastActivity: '11:15 AM',
          },
          {
            user_id: 'user_insight_demo',
            messages: Array(11).fill(null),
            agent_type: 'insight',
            sentiment_score: 8.5,
            escalated: true,
            messageCount: 11,
            lastActivity: '02:40 PM',
          },
        ];

        const filteredMocks = mockSessions.filter(
          (m) => !processed.some((p) => p.user_id === m.user_id)
        );

        if (isMounted) {
          setSessions([...processed, ...filteredMocks]);
          setError('');
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to load session logs.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadSessions();
  }, [userId]);

  const handleViewChat = (targetUserId) => {
    setUserId(targetUserId);
    navigate('/');
  };

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

  // Filter logic
  const filteredSessions = sessions.filter((s) => {
    // Search filter
    const matchesSearch = s.user_id.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Agent filter
    const matchesAgent = agentFilter === 'all' || s.agent_type === agentFilter;
    
    // Status filter (Escalated vs Normal)
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'escalated' && s.escalated) || 
      (statusFilter === 'normal' && !s.escalated);

    // Sentiment filter
    const sentimentText = getSentimentText(s.sentiment_score).toLowerCase();
    const matchesSentiment = sentimentFilter === 'all' || sentimentText === sentimentFilter;

    return matchesSearch && matchesAgent && matchesStatus && matchesSentiment;
  });

  return (
    <section className="space-y-6 pb-12 max-w-7xl mx-auto w-full">
      <div className="border-b border-border pb-4">
        <h2 className="text-xl font-bold text-text uppercase tracking-tight">
          Session Browser
        </h2>
        <p className="text-xs text-muted">Browse, filter, and inspect client routing payloads</p>
      </div>

      {error && (
        <div className="rounded-lg border border-error/20 bg-error/5 px-4 py-3 text-xs font-semibold text-error">
          System Notice: {error}
        </div>
      )}

      {/* Search & Filter Toolbar */}
      <div className="bg-white border border-border rounded-xl p-4 shadow-soft grid grid-cols-1 sm:grid-cols-4 gap-4 items-center">
        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search User ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white border border-border rounded-lg py-2 pl-3 pr-3 text-xs font-semibold focus:outline-none focus:border-primary text-text placeholder:text-muted"
          />
        </div>

        {/* Agent Filter */}
        <div>
          <select
            value={agentFilter}
            onChange={(e) => setAgentFilter(e.target.value)}
            className="w-full bg-white border border-border rounded-lg py-2 px-3 text-xs font-semibold focus:outline-none focus:border-primary text-text"
          >
            <option value="all">All Agents</option>
            <option value="sales">Sales Agent</option>
            <option value="support">Support Agent</option>
            <option value="insight">Insight Agent</option>
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-white border border-border rounded-lg py-2 px-3 text-xs font-semibold focus:outline-none focus:border-primary text-text"
          >
            <option value="all">All Statuses</option>
            <option value="escalated">Escalated</option>
            <option value="normal">Normal</option>
          </select>
        </div>

        {/* Sentiment Filter */}
        <div>
          <select
            value={sentimentFilter}
            onChange={(e) => setSentimentFilter(e.target.value)}
            className="w-full bg-white border border-border rounded-lg py-2 px-3 text-xs font-semibold focus:outline-none focus:border-primary text-text"
          >
            <option value="all">All Sentiments</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
            <option value="angry">Angry</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <span className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <span className="text-xs uppercase text-muted font-bold tracking-wider">Querying Session Store...</span>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredSessions.map((session) => {
            const sentimentText = getSentimentText(session.sentiment_score);
            const isEscalated = session.escalated;
            const isCurrent = session.user_id === userId;

            return (
              <article
                key={session.user_id}
                className={`flex flex-col justify-between rounded-xl border bg-white p-5 shadow-soft hover:shadow-premium transition-all duration-200 ${
                  isCurrent ? 'border-primary ring-2 ring-primary/5' : 'border-border'
                }`}
              >
                <div className="space-y-4">
                  {/* Card Header */}
                  <div className="flex items-start justify-between border-b border-border pb-3">
                    <div className="min-w-0">
                      <p className="text-[10px] uppercase text-muted tracking-wider font-bold">User</p>
                      <h3 className="truncate text-sm font-bold text-text mt-0.5" title={session.user_id}>
                        {session.user_id}
                      </h3>
                    </div>
                    {isCurrent && (
                      <span className="text-[9px] bg-primary/5 text-primary border border-primary/20 px-2 py-0.5 rounded uppercase font-bold tracking-wider">
                        Active
                      </span>
                    )}
                  </div>

                  {/* Details Grid */}
                  <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-xs">
                    <div>
                      <p className="text-[10px] text-muted uppercase font-semibold">Agent</p>
                      <span className={`inline-block text-[11px] uppercase font-bold px-2 py-0.5 rounded border mt-1 ${
                        session.agent_type === 'sales'
                          ? 'border-primary/20 bg-primary/5 text-primary'
                          : session.agent_type === 'support'
                          ? 'border-secondary/20 bg-secondary/5 text-secondary'
                          : 'border-warning/20 bg-warning/5 text-warning'
                      }`}>
                        {session.agent_type}
                      </span>
                    </div>

                    <div>
                      <p className="text-[10px] text-muted uppercase font-semibold">Messages</p>
                      <p className="text-xs font-bold text-text mt-1">
                        {session.messageCount} payloads
                      </p>
                    </div>

                    <div>
                      <p className="text-[10px] text-muted uppercase font-semibold">Status</p>
                      <span className={`inline-block text-[10px] uppercase font-bold px-2 py-0.5 rounded mt-1 border ${
                        isEscalated
                          ? 'bg-error/5 text-error border-error/20 animate-pulse'
                          : 'bg-success/5 text-success border-success/20'
                      }`}>
                        {isEscalated ? '🚨 Escalated' : '✔ Normal'}
                      </span>
                    </div>

                    <div>
                      <p className="text-[10px] text-muted uppercase font-semibold">Sentiment</p>
                      <span className={`inline-block mt-1 text-[9px] uppercase font-semibold px-2 py-0.5 rounded-full border ${getSentimentBadgeStyles(sentimentText)}`}>
                        {sentimentText} ({session.sentiment_score.toFixed(1)})
                      </span>
                    </div>

                    <div className="col-span-2">
                      <p className="text-[10px] text-muted uppercase font-semibold">Last Activity</p>
                      <p className="text-xs font-semibold text-text mt-1">
                        {session.lastActivity}
                      </p>
                    </div>
                  </div>
                </div>

                {/* View Chat Action */}
                <div className="mt-5 pt-4 border-t border-border">
                  <button
                    type="button"
                    onClick={() => handleViewChat(session.user_id)}
                    className="w-full text-center rounded-lg border border-primary bg-transparent py-2 text-xs font-bold text-primary hover:bg-primary/5 transition duration-150"
                  >
                    Launch Agent Workspace
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
