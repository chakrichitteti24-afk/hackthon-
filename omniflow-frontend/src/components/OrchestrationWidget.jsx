import React from 'react';

const steps = [
  { id: 'intent', label: 'Intent Analysis' },
  { id: 'knowledge', label: 'Knowledge Retrieval' },
  { id: 'agent', label: 'Agent Activation' },
  { id: 'response', label: 'Response Generated' },
];

export default function OrchestrationWidget({ activeStep = '', isProcessing = false }) {
  // Map activeStep to index
  const activeIdx = steps.findIndex(s => s.id === activeStep);
  
  return (
    <div className="bg-white rounded-xl border border-border p-4 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        {steps.map((step, idx) => {
          const isDone = idx < activeIdx || (activeIdx === steps.length - 1);
          const isActive = idx === activeIdx && isProcessing;
          
          return (
            <div key={step.id} className="flex flex-1 items-center gap-2 group">
              <div className="relative flex items-center justify-center">
                <div className={`h-5 w-5 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${
                  isDone ? 'bg-success border-success' : 
                  isActive ? 'border-primary' : 'border-border'
                }`}>
                  {isDone ? (
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={4} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : isActive ? (
                    <div className="h-1.5 w-1.5 bg-primary rounded-full animate-pulse" />
                  ) : null}
                </div>
              </div>
              
              <span className={`text-[10px] font-bold uppercase tracking-tight transition-colors ${
                isDone ? 'text-success' : isActive ? 'text-primary' : 'text-text/20'
              }`}>
                {step.label}
              </span>

              {idx !== steps.length - 1 && (
                <div className={`flex-1 h-[1px] mx-2 transition-colors duration-300 ${
                  isDone ? 'bg-success' : 'bg-border/50'
                }`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
