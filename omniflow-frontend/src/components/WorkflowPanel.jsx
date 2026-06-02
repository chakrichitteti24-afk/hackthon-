import React from 'react';

const STAGES = [
  { id: 'intent', label: 'Intent Analysis' },
  { id: 'knowledge', label: 'Knowledge Retrieval' },
  { id: 'agent', label: 'Agent Activation' },
  { id: 'response', label: 'Response Generated' },
];

export default function WorkflowPanel({ activeStep = '', currentAgent = 'sales', isProcessing = false }) {
  // Map activeStep to active index
  const activeIdx = STAGES.findIndex((s) => s.id === activeStep);
  const displayAgent = currentAgent.charAt(0).toUpperCase() + currentAgent.slice(1) + ' Agent';

  return (
    <div className="bg-white border border-border rounded-xl p-5 shadow-soft">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        
        {/* Left Side: AI Workflow Steps */}
        <div>
          <div className="flex items-center justify-between mb-3.5">
            <h3 className="text-xs font-bold text-muted uppercase tracking-wider">AI Workflow</h3>
            {isProcessing && <span className="text-[10px] text-primary font-semibold animate-pulse">Processing...</span>}
          </div>
          
          <div className="flex items-center justify-between gap-2 flex-wrap">
            {STAGES.map((stage, idx) => {
              const isDone = idx < activeIdx || (activeIdx === STAGES.length - 1 && !isProcessing) || (activeIdx === -1 && !isProcessing && activeStep === 'response');
              const isActive = idx === activeIdx && isProcessing;

              return (
                <div key={stage.id} className="flex items-center gap-2 flex-1 min-w-[120px]">
                  <div className={`h-5 w-5 rounded-full border flex items-center justify-center transition-all duration-300 ${
                    isDone 
                      ? 'bg-success/10 border-success text-success' 
                      : isActive 
                      ? 'border-primary text-primary bg-primary/5' 
                      : 'border-border text-muted bg-bg/50'
                  }`}>
                    {isDone ? (
                      <span className="text-xs font-bold">✓</span>
                    ) : isActive ? (
                      <span className="h-1.5 w-1.5 rounded-full bg-primary animate-ping" />
                    ) : (
                      <span className="text-[10px] font-bold">{idx + 1}</span>
                    )}
                  </div>
                  <span className={`text-xs font-semibold ${
                    isDone ? 'text-text' : isActive ? 'text-primary font-bold' : 'text-muted'
                  }`}>
                    {stage.label}
                  </span>
                  {idx !== STAGES.length - 1 && (
                    <div className="hidden sm:block flex-1 h-[1px] bg-border mx-2" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side: Agent Orchestration routing animation */}
        <div className="border-t lg:border-t-0 lg:border-l border-border pt-4 lg:pt-0 lg:pl-8">
          <h3 className="text-xs font-bold text-muted uppercase tracking-wider mb-3">Agent Orchestration</h3>
          
          <div className="flex items-center justify-center sm:justify-start gap-4">
            
            {/* Step 1: Intent Analysis Node */}
            <div className={`px-3 py-1.5 rounded-lg border text-xs font-bold transition-all ${
              isProcessing && activeStep === 'intent'
                ? 'bg-primary/5 border-primary text-primary shadow-soft animate-pulse'
                : 'bg-bg border-border text-text'
            }`}>
              Intent Analysis
            </div>

            {/* Arrow 1 */}
            <div className="flex items-center justify-center text-muted">
              <svg className={`w-4 h-4 ${isProcessing && activeIdx >= 0 ? 'text-primary animate-bounce' : 'text-border'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </div>

            {/* Step 2: Agent Node (Sales / Insight / Support) */}
            <div className="relative flex flex-col items-center">
              <div className={`px-4 py-1.5 rounded-lg border text-xs font-bold transition-all ${
                isProcessing && (activeStep === 'agent' || activeStep === 'memory')
                  ? 'bg-secondary/10 border-secondary text-secondary shadow-soft animate-pulse'
                  : 'bg-white border-border text-text'
              }`}>
                {displayAgent}
              </div>
              
              {/* Other agents running in background */}
              <div className="absolute top-full mt-1 flex gap-1.5">
                {['Sales', 'Insight', 'Support'].map((agentName) => {
                  const isCurrent = currentAgent.toLowerCase() === agentName.toLowerCase();
                  if (isCurrent) return null;
                  return (
                    <span key={agentName} className="text-[9px] text-muted/40 font-medium px-1 border border-border/30 rounded bg-bg/25">
                      {agentName}
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Arrow 2 */}
            <div className="flex items-center justify-center text-muted">
              <svg className={`w-4 h-4 ${isProcessing && activeIdx >= 3 ? 'text-primary animate-bounce' : 'text-border'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </div>

            {/* Step 3: Response Generated Node */}
            <div className={`px-3 py-1.5 rounded-lg border text-xs font-bold transition-all ${
              !isProcessing && activeStep === 'response'
                ? 'bg-success/5 border-success text-success shadow-soft'
                : 'bg-bg border-border text-muted'
            }`}>
              Response
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
