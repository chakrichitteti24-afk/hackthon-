import React from 'react';

const ACTIONS = [
  { label: 'Smartphones', icon: '📱', query: 'Show me the latest flagship smartphones with detailed comparisons' },
  { label: 'Laptops', icon: '💻', query: 'Recommend high-performance laptops for developers and content creators' },
  { label: 'Market Analysis', icon: '📊', query: 'Provide a market analysis on recent consumer electronics trends' },
  { label: 'Product Comparison', icon: '⚔️', query: 'Compare the technical specifications of iPhone 15 Pro vs Samsung S24 Ultra' },
  { label: 'Support', icon: '🛠️', query: 'I need support regarding warranty claims and system configurations' },
];

export default function QuickActionCards({ onSelect }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 w-full max-w-5xl mx-auto mb-6">
      {ACTIONS.map((action, i) => (
        <button
          key={i}
          onClick={() => onSelect(action.query)}
          className="bg-white border border-border rounded-xl p-4 flex flex-col items-center gap-2 hover:border-primary hover:shadow-premium transition-all group text-center"
        >
          <span className="text-2xl group-hover:scale-110 transition-transform">{action.icon}</span>
          <span className="text-xs font-semibold text-text group-hover:text-primary transition-colors">
            {action.label}
          </span>
        </button>
      ))}
    </div>
  );
}
