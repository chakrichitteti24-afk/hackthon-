import React, { useState, useEffect, useRef } from 'react';

const SUGGESTIONS = [
  'Lenovo Legion',
  'Best gaming laptop under 1.5 lakh',
  'Compare iPhone vs Samsung',
  'AI market trends',
  'SaaS growth strategy 2026',
  'NVIDIA stock analysis',
];

export default function IntelligenceSearchBar({ onSearch, isProcessing = false }) {
  const [query, setQuery] = useState('');
  const [showDropdown, setShowSuggestions] = useState(false);
  const [recentSearches, setRecent] = useState([]);
  const containerRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem('omniflow_recent_searches');
    if (saved) setRecent(JSON.parse(saved).slice(0, 5));
    
    const clickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', clickOutside);
    return () => document.removeEventListener('mousedown', clickOutside);
  }, []);

  const handleAction = (txt) => {
    if (!txt?.trim()) return;
    const clean = txt.trim();
    
    // Save to recent
    const newRecent = [clean, ...recentSearches.filter(s => s !== clean)].slice(0, 5);
    setRecent(newRecent);
    localStorage.setItem('omniflow_recent_searches', JSON.stringify(newRecent));
    
    onSearch(clean);
    setQuery('');
    setShowSuggestions(false);
  };

  const filteredSuggestions = SUGGESTIONS.filter(s => 
    s.toLowerCase().includes(query.toLowerCase()) && s.toLowerCase() !== query.toLowerCase()
  );

  return (
    <div ref={containerRef} className="relative w-full max-w-xl mx-auto">
      <div className={`relative group transition-all duration-300 ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}>
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-primary/40 group-focus-within:text-primary transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        <input 
          type="text"
          value={query}
          onFocus={() => setShowSuggestions(true)}
          onChange={(e) => { setQuery(e.target.value); setShowSuggestions(true); }}
          onKeyDown={(e) => e.key === 'Enter' && handleAction(query)}
          placeholder="Search products, brands, trends, market insights, or ask a question..."
          className="w-full bg-white border border-border rounded-full py-2.5 pl-10 pr-4 text-sm font-semibold shadow-sm focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/5 transition-all placeholder:text-muted/60 text-text"
        />
        
        {isProcessing && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        )}
      </div>

      {showDropdown && (query || recentSearches.length > 0) && (
        <div className="absolute top-full left-0 right-0 mt-3 bg-white border border-border rounded-2xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          
          {recentSearches.length > 0 && !query && (
            <div className="p-4 border-b border-border/50">
              <p className="text-[10px] font-bold text-text/30 uppercase tracking-widest mb-3 px-2">Recent Intelligence Queries</p>
              <div className="flex flex-wrap gap-2">
                {recentSearches.map((s, i) => (
                  <button key={i} onClick={() => handleAction(s)} className="bg-gray-50 hover:bg-primary/5 hover:text-primary border border-border/60 rounded-full px-3 py-1.5 text-xs font-bold transition-all">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="py-2">
            <p className="text-[10px] font-bold text-text/30 uppercase tracking-widest mb-1 px-6 pt-2">Suggestions</p>
            {(query ? filteredSuggestions : SUGGESTIONS).slice(0, 6).map((s, i) => (
              <button key={i} onClick={() => handleAction(s)} className="w-full flex items-center gap-4 px-6 py-3 hover:bg-gray-50 transition-colors text-left group">
                <span className="text-primary/20 group-hover:text-primary transition-colors italic text-lg font-serif">#</span>
                <span className="text-sm font-bold text-text/70 group-hover:text-text transition-colors">{s}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
