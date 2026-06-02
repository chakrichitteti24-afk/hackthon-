import React, { useContext, useEffect, useState } from 'react';
import { AppContext } from '../context/AppContext.js';
import { getSession } from '../api/omniflow.js';

export default function CustomerMemoryPage() {
  const { userId } = useContext(AppContext);
  const [memory, setMemory] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchMemory = async () => {
      try {
        setLoading(true);
        const data = await getSession(userId);
        if (mounted && data) {
          setMemory(data.memory || {});
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchMemory();
    return () => { mounted = false; };
  }, [userId]);

  const hasMemory = memory.interests || memory.previous_products || memory.previous_issues || memory.budget || (memory.sentiment_history && memory.sentiment_history.length > 0);

  return (
    <section className="space-y-6 pb-12 max-w-5xl mx-auto w-full">
      <div className="border-b border-border pb-4">
        <h2 className="text-xl font-bold text-text uppercase tracking-tight">Shared Customer Memory</h2>
        <p className="text-xs text-muted">Synchronized persistent customer metadata profiles across routing agents</p>
      </div>

      <div className="bg-white border border-border rounded-xl p-6 shadow-soft space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4 border-b border-border pb-4">
          <div>
            <h3 className="text-sm font-bold text-text uppercase">Client Profile ID: {userId}</h3>
            <p className="text-xs text-muted">
              Session sync status: {hasMemory ? 'Active' : 'Idle'}
            </p>
          </div>
          <span className={`text-xs border px-2.5 py-1 rounded font-bold uppercase tracking-wider ${
            hasMemory ? 'bg-success/5 text-success border-success/20' : 'bg-gray-50 text-muted border-border'
          }`}>
            {hasMemory ? 'Memory Synced' : 'No data available'}
          </span>
        </div>

        {loading ? (
          <div className="flex h-32 items-center justify-center">
            <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Previous Interests Card */}
            <div className="bg-bg/25 border border-border rounded-xl p-5 shadow-soft space-y-2">
              <h4 className="text-[10px] font-bold text-muted uppercase tracking-wider">Previous Interests</h4>
              <p className="text-sm font-semibold text-text leading-relaxed">
                {memory.interests || 'No data available'}
              </p>
              <p className="text-[10px] text-muted italic">Inferred from client query heuristics</p>
            </div>

            {/* Previous Products Card */}
            <div className="bg-bg/25 border border-border rounded-xl p-5 shadow-soft space-y-2">
              <h4 className="text-[10px] font-bold text-muted uppercase tracking-wider">Previous Products</h4>
              <p className="text-sm font-semibold text-text leading-relaxed">
                {memory.previous_products || 'No data available'}
              </p>
              <p className="text-[10px] text-muted italic">Retrieved from product catalog mapping</p>
            </div>

            {/* Previous Issues Card */}
            <div className="bg-bg/25 border border-border rounded-xl p-5 shadow-soft space-y-2">
              <h4 className="text-[10px] font-bold text-muted uppercase tracking-wider">Previous Issues</h4>
              <p className="text-sm font-semibold text-text leading-relaxed">
                {memory.previous_issues || 'No data available'}
              </p>
              <p className="text-[10px] text-muted italic">Derived from escalation histories</p>
            </div>

            {/* Budget History Card */}
            <div className="bg-bg/25 border border-border rounded-xl p-5 shadow-soft space-y-2">
              <h4 className="text-[10px] font-bold text-muted uppercase tracking-wider">Budget History</h4>
              <p className="text-sm font-semibold text-text leading-relaxed">
                {memory.budget || 'No data available'}
              </p>
              <p className="text-[10px] text-muted italic">Heuristically compiled transaction boundaries</p>
            </div>

            {/* Sentiment Trend Card */}
            <div className="bg-bg/25 border border-border rounded-xl p-5 shadow-soft space-y-2 md:col-span-2">
              <h4 className="text-[10px] font-bold text-muted uppercase tracking-wider">Sentiment Trend</h4>
              <p className="text-sm font-semibold text-text leading-relaxed capitalize">
                {memory.sentiment_history && memory.sentiment_history.length > 0
                  ? memory.sentiment_history.join(' ➜ ')
                  : 'No data available'}
              </p>
              <p className="text-[10px] text-muted italic">Continuous NLP sentiment classification average</p>
            </div>

          </div>
        )}
      </div>
    </section>
  );
}
