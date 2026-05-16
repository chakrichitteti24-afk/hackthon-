import { useContext, useEffect, useState } from 'react';
import { getSession, checkHealth } from '../api/omniflow.js';
import { AppContext } from '../context/AppContext.js';

export default function DashboardPage() {
  const { userId } = useContext(AppContext);
  const [health, setHealth] = useState('checking');
  const [session, setSession] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      const [healthResult, sessionResult] = await Promise.allSettled([
        checkHealth(),
        getSession(userId),
      ]);

      if (!isMounted) {
        return;
      }

      if (healthResult.status === 'fulfilled') {
        setHealth(healthResult.value.status || 'unknown');
      } else {
        setHealth('offline');
      }

      if (sessionResult.status === 'fulfilled') {
        setSession(sessionResult.value);
      }

      if (healthResult.status === 'rejected' || sessionResult.status === 'rejected') {
        const failedRequest =
          healthResult.status === 'rejected' ? healthResult : sessionResult;
        setError(failedRequest.reason.message || 'Unable to connect to the backend.');
      } else {
        setError('');
      }
    };

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, [userId]);

  const messageCount = session?.messages?.length ?? 0;
  const sentimentScore = session?.sentiment_score ?? 0;
  const escalated = session?.escalated ? 'Yes' : 'No';

  return (
    <section className="mx-auto max-w-5xl space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-primary">Dashboard</h2>
        <p className="text-sm text-primary/70">Live session overview for {userId}</p>
      </div>

      {error ? (
        <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
          {error}
        </p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <article className="rounded-lg border border-primary/20 bg-black/30 p-4">
          <p className="text-xs uppercase text-secondary">Backend</p>
          <p className="mt-2 text-2xl font-semibold text-primary">{health}</p>
        </article>
        <article className="rounded-lg border border-primary/20 bg-black/30 p-4">
          <p className="text-xs uppercase text-secondary">Messages</p>
          <p className="mt-2 text-2xl font-semibold text-primary">{messageCount}</p>
        </article>
        <article className="rounded-lg border border-primary/20 bg-black/30 p-4">
          <p className="text-xs uppercase text-secondary">Sentiment</p>
          <p className="mt-2 text-2xl font-semibold text-primary">{sentimentScore}</p>
        </article>
        <article className="rounded-lg border border-primary/20 bg-black/30 p-4">
          <p className="text-xs uppercase text-secondary">Escalated</p>
          <p className="mt-2 text-2xl font-semibold text-primary">{escalated}</p>
        </article>
      </div>

      <div className="rounded-lg border border-primary/20 bg-black/30 p-4">
        <h3 className="mb-3 text-base font-semibold text-primary">Recent Messages</h3>
        {messageCount === 0 ? (
          <p className="text-sm text-primary/60">No messages in this session yet.</p>
        ) : (
          <div className="space-y-2">
            {session.messages.slice(-6).map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className="rounded-md border border-primary/10 bg-black/30 p-3"
              >
                <p className="text-xs uppercase text-secondary">{message.role}</p>
                <p className="mt-1 text-sm text-primary">{message.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
