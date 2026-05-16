import { useContext } from 'react';
import { AppContext } from '../context/AppContext.js';

const agentLabels = {
  sales: 'Sales Agent',
  support: 'Support Agent',
  insight: 'Insight Agent',
};

export default function Header() {
  const { currentAgent, userId } = useContext(AppContext);

  return (
    <header className="border-b border-primary/20 bg-black/30 px-4 py-4 backdrop-blur sm:px-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-secondary">OmniFlow AI</p>
          <h1 className="text-xl font-semibold text-primary">Agent Workspace</h1>
        </div>
        <div className="flex flex-col gap-1 text-sm text-primary/80 sm:items-end">
          <span>{agentLabels[currentAgent] ?? 'Agent'}</span>
          <span className="text-xs text-secondary/80">{userId}</span>
        </div>
      </div>
    </header>
  );
}
