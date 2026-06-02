import React from 'react';

export default function ModelBadge({ text = 'LLM', variant = 'info' }) {
  const styles = {
    web: 'bg-primary/10 text-primary border-primary/20',
    wiki: 'bg-primary/10 text-primary border-primary/20',
    wikipedia: 'bg-primary/10 text-primary border-primary/20',
    escalated: 'bg-error/10 text-error border-error/20',
    memory_synced: 'bg-secondary/10 text-secondary border-secondary/20',
    groq: 'bg-primary/10 text-primary border-primary/20',
    gemini: 'bg-secondary/10 text-secondary border-secondary/20',
    factual_mode: 'bg-secondary/10 text-secondary border-secondary/20',
    validated: 'bg-success/10 text-success border-success/20',
    verified: 'bg-success/10 text-success border-success/20',
    alert: 'bg-error/10 text-error border-error/20',
  };

  const styleClass = styles[variant?.toLowerCase()] || 'bg-gray-100 text-gray-700 border-gray-200';

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold border ${styleClass}`}>
      {text}
    </span>
  );
}
