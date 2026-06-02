import { useContext, useEffect, useState } from 'react';
import { AppContext } from '../context/AppContext.js';
import { getStatus } from '../api/omniflow.js';

export default function Header() {
  const { userId } = useContext(AppContext);
  const [statusInfo, setStatusInfo] = useState({
    api: 'checking',
    memory_active: false,
    gemini_available: false,
    wiki_available: false,
  });

  useEffect(() => {
    let mounted = true;
    const fetch = async () => {
      try {
        const s = await getStatus();
        if (!mounted) return;
        setStatusInfo(s);
      } catch (e) {
        if (mounted) {
          setStatusInfo((prev) => ({ ...prev, api: 'offline' }));
        }
      }
    };
    fetch();
    const iv = setInterval(fetch, 10000);
    return () => { 
      mounted = false; 
      clearInterval(iv); 
    };
  }, []);

  const isOnline = statusInfo.api === 'ok';

  return (
    <header className="border-b border-border bg-white px-6 py-3 sticky top-0 z-40 shadow-soft">
      <div className="flex items-center justify-between">
        
        {/* Left Side: System status indicators / badges */}
        <div className="flex flex-wrap items-center gap-2">
          
          {/* System Online badge */}
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            isOnline 
              ? 'bg-success/5 text-success border-success/20' 
              : 'bg-error/5 text-error border-error/20'
          }`}>
            <span className={`h-1.5 w-1.5 rounded-full ${isOnline ? 'bg-success' : 'bg-error animate-pulse'}`} />
            System Online
          </span>

          {/* Memory Synced badge */}
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            statusInfo.memory_active 
              ? 'bg-secondary/5 text-secondary border-secondary/20' 
              : 'bg-gray-50 text-muted border-border'
          }`}>
            <span className={`h-1.5 w-1.5 rounded-full ${statusInfo.memory_active ? 'bg-secondary' : 'bg-muted'}`} />
            Memory Synced
          </span>

          {/* Active Model badge */}
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-primary/5 text-primary border-primary/20">
            <span className="h-1.5 w-1.5 rounded-full bg-primary" />
            Active Model: {statusInfo.gemini_available ? 'Gemini 3.5 Flash' : 'Groq'}
          </span>

          {/* Knowledge Engine badge */}
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            statusInfo.wiki_available 
              ? 'bg-secondary/5 text-secondary border-secondary/20' 
              : 'bg-gray-50 text-muted border-border'
          }`}>
            <span className={`h-1.5 w-1.5 rounded-full ${statusInfo.wiki_available ? 'bg-secondary' : 'bg-muted'}`} />
            Knowledge Engine
          </span>

          {/* AI Latency badge */}
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-gray-50 text-text border-border">
            <span className="h-1.5 w-1.5 rounded-full bg-muted" />
            AI Latency: 118ms
          </span>

        </div>

        {/* Right Side: Active User Account */}
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-semibold text-text">{userId ? userId.split('_')[1] || 'Guest' : 'Guest'}</p>
            <p className="text-[9px] font-medium text-muted uppercase">Terminal User</p>
          </div>
          <div className="w-8 h-8 bg-primary/10 text-primary rounded-full flex items-center justify-center font-bold text-xs border border-primary/20">
            {userId ? userId.split('_')[1]?.charAt(0).toUpperCase() || 'U' : 'U'}
          </div>
        </div>

      </div>
    </header>
  );
}
