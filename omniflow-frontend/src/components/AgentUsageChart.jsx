import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Legend, Tooltip } from 'recharts';
import ChartSurface from './ChartSurface.jsx';

const CustomLegend = ({ payload }) => {
  return (
    <div className="flex gap-4 items-center justify-center mt-3">
      {payload.map((entry) => (
        <div key={entry.value} className="flex items-center gap-2">
          <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: entry.color }} />
          <span className="text-xs font-semibold text-text">{entry.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function AgentUsageChart({ data = [] }) {
  const themedData = data.map((d) => {
    let color = '#2563EB'; // primary
    if (d.name.toLowerCase() === 'sales') color = '#2563EB';
    if (d.name.toLowerCase() === 'support') color = '#14B8A6';
    if (d.name.toLowerCase() === 'insight') color = '#F59E0B';
    return { ...d, color };
  });

  const hasData = themedData && themedData.some((d) => d.count > 0);

  return (
    <div className="rounded-xl border border-border bg-white p-5 shadow-soft flex flex-col justify-between relative overflow-hidden">
      <div>
        <h3 className="text-sm font-bold text-text uppercase tracking-wider">Agent Usage</h3>
        <p className="text-xs text-muted mb-2">Distribution of active user sessions by agent routing</p>
      </div>

      {!hasData && (
        <div className="absolute inset-0 bg-white/90 backdrop-blur-[1px] flex flex-col items-center justify-center z-10">
          <span className="text-xs font-bold text-muted uppercase tracking-wider">No data available</span>
          <p className="text-[10px] text-muted/65 mt-1">Start a conversation to view agent distribution</p>
        </div>
      )}

      <ChartSurface className="h-60 w-full min-h-[180px]">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <PieChart>
            <Pie 
              data={themedData} 
              dataKey="count" 
              nameKey="name" 
              innerRadius={50} 
              outerRadius={80} 
              paddingAngle={4}
            >
              {themedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend verticalAlign="bottom" content={<CustomLegend />} />
          </PieChart>
        </ResponsiveContainer>
      </ChartSurface>
    </div>
  );
}
