import { useContext, useState, useEffect, useRef } from 'react';
import { postChat, postEscalate, getSession } from '../api/omniflow.js';
import { AppContext } from '../context/AppContext.js';
import ResponseCard from '../components/ResponseCard';
import IntelligencePanel from '../components/IntelligencePanel';
import IntelligenceSearchBar from '../components/IntelligenceSearchBar';
import QuickActionCards from '../components/QuickActionCards';
import WorkflowPanel from '../components/WorkflowPanel';

const agentOptions = [
  { value: 'sales', label: 'Sales Agent' },
  { value: 'support', label: 'Support Agent' },
  { value: 'insight', label: 'Insight Agent' },
];

export default function ChatPage() {
  const { currentAgent, setCurrentAgent, userId } = useContext(AppContext);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isEscalated, setIsEscalated] = useState(false);
  const [memory, setMemory] = useState({});
  const [activeOrchStep, setActiveOrchStep] = useState('response');
  const messagesEndRef = useRef(null);

  useEffect(() => { 
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); 
  }, [messages]);

  useEffect(() => {
    let mounted = true;
    const fetchHistory = async () => {
      try {
        const session = await getSession(userId);
        if (!mounted || !session) return;
        setIsEscalated(session.escalated || false);
        setMemory(session.memory || {});

        const formatted = (session.messages || []).map((msg) => ({
          role: msg.role,
          content: msg.content,
          sentiment: msg.sentiment || null,
          meta: msg.role === 'assistant' ? {
            llm: msg.llm_used,
            web: msg.web_search_used,
            validated: msg.response_validated,
            webSources: msg.web_sources || (msg.web_search_used ? ['Wikipedia'] : []),
            confidence: msg.confidence,
            sources: msg.sources,
          } : undefined,
        }));

        setMessages(formatted);
      } catch (e) {
        if (mounted) setError(e.message || 'Failed to load session history.');
      }
    };
    fetchHistory();
    return () => { mounted = false; };
  }, [userId]);

  const performSearch = async (txt) => {
    if (!txt || isSending) return;
    
    setError(''); 
    setIsSending(true); 
    setMessage('');
    setMessages((m) => [...m, { role: 'user', content: txt }]);

    // Animate stages of enterprise pipeline
    setActiveOrchStep('intent');
    
    try {
      setTimeout(() => setActiveOrchStep('knowledge'), 700);
      setTimeout(() => setActiveOrchStep('agent'), 1400);

      const data = await postChat(userId, txt, currentAgent);
      
      setActiveOrchStep('response');
      setIsEscalated(data.escalate || false);
      setMemory(data.memory || memory);
      
      const assistantMsg = { 
        role: 'assistant', 
        content: '', 
        meta: { 
          llm: data.llm_used, 
          web: data.web_searched, 
          validated: data.response_validated, 
          webSources: data.web_sources || [],
          confidence: data.confidence,
          sources: data.sources,
        }, 
        sentiment: data.sentiment 
      };
      
      setMessages((m) => [...m, assistantMsg]);

      const full = data.reply || '';
      if (!full) {
        setIsSending(false);
        return;
      }
      
      let i = 0; 
      const step = Math.max(2, Math.floor(full.length / 30));
      const iv = setInterval(() => {
        i += step;
        setMessages((prev) => {
          const copy = [...prev];
          const last = copy.length - 1;
          if (last >= 0 && copy[last].role === 'assistant') {
            copy[last] = { ...copy[last], content: full.slice(0, Math.min(i, full.length)) };
          }
          return copy;
        });
        if (i >= full.length) {
          clearInterval(iv);
          setTimeout(() => {
            setIsSending(false);
          }, 300);
        }
      }, 15);
    } catch (e) {
      setError(e.message || 'Routing connection interrupted.');
      setIsSending(false);
      setActiveOrchStep('response');
    }
  };

  const handleSubmit = (ev) => {
    ev.preventDefault();
    performSearch(message.trim());
  };

  const handleEscalate = async () => {
    setError('');
    try {
      await postEscalate(userId);
      setIsEscalated(true);
      setMessages((m) => [...m, { role: 'system', content: 'Manual escalation initiated. Enterprise support notified.' }]);
    } catch (e) {
      setError(e.message || 'Failed to trigger escalation.');
    }
  };

  return (
    <div className="flex flex-col gap-6 h-[calc(100vh-80px)] overflow-hidden p-6 max-w-[1600px] mx-auto w-full">
      
      {/* Title Area & Agent Switcher */}
      <div className="flex items-center justify-between flex-wrap gap-4 border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-text">Workspace Orchestrator</h2>
          <p className="text-xs text-muted">Enterprise product intelligence & client memory routing</p>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-muted">Routing Target:</span>
          <div className="flex bg-white rounded-lg p-1 border border-border shadow-soft">
            {agentOptions.map((opt) => (
              <button 
                key={opt.value} 
                onClick={() => setCurrentAgent(opt.value)} 
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                  currentAgent === opt.value 
                    ? 'bg-primary text-white shadow-soft' 
                    : 'text-muted hover:text-text'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Grid: Workspace & Customer Heuristics */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6 overflow-hidden min-h-0">
        
        {/* Left Side: Center Workspace & Bottom Panels */}
        <div className="flex flex-col gap-6 overflow-hidden min-h-0">
          
          {/* Workspace scrollable core */}
          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-6 pb-4">
            
            {/* 1. Large Search Bar */}
            <div className="pt-2">
              <IntelligenceSearchBar onSearch={performSearch} isProcessing={isSending} />
            </div>

            {/* 2. Quick Actions Cards (only visible if messages are empty or at top) */}
            {messages.length === 0 && (
              <div className="space-y-3">
                <p className="text-center text-xs font-semibold text-muted uppercase tracking-wider">Quick Actions</p>
                <QuickActionCards onSelect={performSearch} />
              </div>
            )}

            {/* 3. Response Area / Messages List */}
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-16 border border-dashed border-border rounded-2xl bg-white/50 shadow-soft">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4 text-primary">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-sm font-bold text-text">Initialize Heuristic Search</h3>
                <p className="text-xs text-muted max-w-sm mt-1">Submit a search query or choose a quick action above to trigger multi-agent intelligence matching.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((m, i) => {
                  const isUser = m.role === 'user';
                  const isSystem = m.role === 'system';

                  if (isSystem) {
                    return (
                      <div key={i} className="flex justify-center">
                        <span className="bg-error/5 border border-error/20 text-error px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
                          {m.content}
                        </span>
                      </div>
                    );
                  }

                  if (isUser) {
                    return (
                      <div key={i} className="flex justify-end">
                        <div className="bg-primary text-white border border-primary/20 rounded-2xl px-5 py-3 shadow-soft max-w-[80%]">
                          <p className="text-[10px] font-bold text-white/60 uppercase mb-1">User Query</p>
                          <p className="text-sm font-semibold leading-relaxed">{m.content}</p>
                        </div>
                      </div>
                    );
                  }

                  // Assistant Response rendered in dynamic ResponseCard
                  return (
                    <div key={i} className="flex justify-start">
                      <div className="w-full">
                        <p className="text-[10px] font-bold text-muted uppercase mb-1.5 ml-1">AI Recommendation Card</p>
                        <ResponseCard content={m.content} sentiment={m.sentiment} meta={m.meta} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Sticky Bottom text entry and triggers */}
          <div className="border-t border-border pt-4 bg-bg">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input 
                type="text" 
                value={message} 
                onChange={(e) => setMessage(e.target.value)} 
                placeholder="Ask details about products, brands, trends, market insights..." 
                disabled={isSending}
                className="flex-1 bg-white border border-border rounded-xl px-4 py-3 text-sm font-semibold shadow-soft focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all placeholder:text-muted/50 text-text"
              />
              <button 
                type="button"
                onClick={handleEscalate}
                disabled={isEscalated || isSending}
                className="px-4 py-3 border border-error/30 text-error rounded-xl text-xs font-bold uppercase hover:bg-error/5 transition-colors disabled:opacity-30"
              >
                Escalate
              </button>
              <button 
                type="submit" 
                disabled={isSending || !message.trim()} 
                className="bg-primary text-white px-6 py-3 rounded-xl text-xs font-bold uppercase shadow-soft hover:bg-primary/95 transition-colors disabled:opacity-50"
              >
                {isSending ? '...' : 'Send'}
              </button>
            </form>
            {error && (
              <p className="mt-2 text-xs font-semibold text-error text-center">
                {error}
              </p>
            )}
          </div>

          {/* 4. Bottom Workflow Section */}
          <div className="pt-2">
            <WorkflowPanel activeStep={activeOrchStep} currentAgent={currentAgent} isProcessing={isSending} />
          </div>

        </div>

        {/* Right Side: Customer Intelligence Panel (Always visible) */}
        <div className="hidden lg:block h-full">
          <IntelligencePanel 
            memory={memory} 
            currentAgent={currentAgent} 
            confidence={messages.length > 0 ? 94 : 0} 
            isEscalated={isEscalated}
          />
        </div>

      </div>
    </div>
  );
}
