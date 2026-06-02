import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import ChartSurface from './ChartSurface.jsx';

const TooltipBox = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="rounded-lg border border-border bg-white p-3 shadow-premium">
      <div className="text-xs font-semibold text-text uppercase mb-1">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center gap-2 mt-1 text-xs">
          <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: p.fill }} />
          <span className="text-muted font-medium">{p.name}:</span>
          <span className="text-text font-bold">{p.value} queries</span>
        </div>
      ))}
    </div>
  );
};

export default function KnowledgeUsageChart({ data = [] }) {
  const hasData = data && data.length > 0 && data.some((item) => item.direct > 0 || item.rag > 0);

  return (
    <div className="rounded-xl border border-border bg-white p-5 shadow-soft relative overflow-hidden">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-text uppercase tracking-wider">Knowledge Engine Usage</h3>
        <p className="text-xs text-muted">Direct LLM responses vs Factual RAG retrievals</p>
      </div>

      {!hasData && (
        <div className="absolute inset-0 bg-white/90 backdrop-blur-[1px] flex flex-col items-center justify-center z-10">
          <span className="text-xs font-bold text-muted uppercase tracking-wider">No data available</span>
          <p className="text-[10px] text-muted/65 mt-1">Start a conversation to activate grounding engine analytics</p>
        </div>
      )}

      <ChartSurface className="h-64 w-full min-h-[200px]">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <BarChart data={data} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="name" stroke="#6B7280" style={{ fontSize: '10px', fontWeight: '500' }} />
            <YAxis stroke="#6B7280" style={{ fontSize: '10px', fontWeight: '500' }} />
            <Tooltip content={<TooltipBox />} />
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />
            <Bar dataKey="direct" name="Direct LLM Inferences" fill="#2563EB" stackId="a" radius={[0, 0, 0, 0]} />
            <Bar dataKey="rag" name="Factual RAG Retrieval" fill="#14B8A6" stackId="a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartSurface>
    </div>
  );
}
