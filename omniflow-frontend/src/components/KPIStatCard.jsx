import React from 'react';

export default function KPIStatCard({
  title,
  value,
  subtitle,
  hint,
  trend = 'up', // 'up' | 'down' | 'neutral'
}) {
  return (
    <article className="bg-white border border-border rounded-xl p-5 shadow-soft hover:shadow-premium transition-all duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-muted uppercase tracking-wider">{title}</p>
          <div className="mt-2.5 flex items-baseline gap-2">
            <h3 className="text-2xl font-bold text-text tracking-tight">{value}</h3>
            {hint && (
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${
                trend === 'up' 
                  ? 'bg-success/5 text-success border border-success/10' 
                  : trend === 'down' 
                  ? 'bg-error/5 text-error border border-error/10' 
                  : 'bg-warning/5 text-warning border border-warning/10'
              }`}>
                {hint}
              </span>
            )}
          </div>
          {subtitle && <p className="mt-1.5 text-xs text-muted font-medium">{subtitle}</p>}
        </div>

        <div className="h-9 w-9 rounded-lg bg-primary/5 text-primary flex items-center justify-center border border-primary/10">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
          </svg>
        </div>
      </div>
    </article>
  );
}
