import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
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
      <div className="flex items-center gap-2 text-xs">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-primary" />
        <span className="text-muted font-medium">Latency:</span>
        <span className="text-text font-bold">{payload[0].value} ms</span>
      </div>
    </div>
  );
};

export default function LatencyChart({ data = [] }) {
  const hasData = data && data.length > 0 && data.some((item) => item.latency > 0);

  return (
    <div className="rounded-xl border border-border bg-white p-5 shadow-soft relative overflow-hidden">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-text uppercase tracking-wider">Latency Trend</h3>
        <p className="text-xs text-muted">Average AI response latency in milliseconds</p>
      </div>

      {!hasData && (
        <div className="absolute inset-0 bg-white/90 backdrop-blur-[1px] flex flex-col items-center justify-center z-10">
          <span className="text-xs font-bold text-muted uppercase tracking-wider">No data available</span>
          <p className="text-[10px] text-muted/65 mt-1">Start a conversation to measure response latencies</p>
        </div>
      )}

      <ChartSurface className="h-64 w-full min-h-[200px]">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <AreaChart data={data} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
            <defs>
              <linearGradient id="latencyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0.01}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="day" stroke="#6B7280" style={{ fontSize: '10px', fontWeight: '500' }} />
            <YAxis stroke="#6B7280" style={{ fontSize: '10px', fontWeight: '500' }} />
            <Tooltip content={<TooltipBox />} />
            <Area type="monotone" dataKey="latency" name="Latency" stroke="#2563EB" strokeWidth={2.5} fillOpacity={1} fill="url(#latencyGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </ChartSurface>
    </div>
  );
}
