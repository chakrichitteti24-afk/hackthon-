import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
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
          <span className="inline-block w-2 h-2 rounded-full" style={{ background: p.stroke }}></span>
          <span className="text-muted font-medium">{p.name}:</span>
          <span className="text-text font-bold">{p.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function SentimentChart({ data = [] }) {
  const hasData = data && data.length > 0 && data.some(
    (item) => item.positive > 0 || item.neutral > 0 || item.negative > 0 || item.angry > 0
  );

  return (
    <div className="rounded-xl border border-border bg-white p-5 shadow-soft relative overflow-hidden">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-text uppercase tracking-wider">Sentiment Trend</h3>
        <p className="text-xs text-muted">Customer emotional distribution over 7 days</p>
      </div>

      {!hasData && (
        <div className="absolute inset-0 bg-white/90 backdrop-blur-[1px] flex flex-col items-center justify-center z-10">
          <span className="text-xs font-bold text-muted uppercase tracking-wider">No data available</span>
          <p className="text-[10px] text-muted/65 mt-1">Start a conversation to generate sentiment metrics</p>
        </div>
      )}

      <ChartSurface className="h-64 w-full min-h-[200px]">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <LineChart data={data} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="day" stroke="#6B7280" style={{ fontSize: '10px', fontWeight: '500' }} />
            <YAxis stroke="#6B7280" style={{ fontSize: '10px', fontWeight: '500' }} />
            <Tooltip content={<TooltipBox />} />
            <Line type="monotone" dataKey="positive" name="Positive" stroke="#10B981" strokeWidth={2.5} dot={{ r: 3 }} />
            <Line type="monotone" dataKey="neutral" name="Neutral" stroke="#2563EB" strokeWidth={2} dot={{ r: 3 }} />
            <Line type="monotone" dataKey="negative" name="Negative" stroke="#F59E0B" strokeWidth={2} dot={{ r: 3 }} />
            <Line type="monotone" dataKey="angry" name="Angry" stroke="#EF4444" strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </ChartSurface>
    </div>
  );
}
