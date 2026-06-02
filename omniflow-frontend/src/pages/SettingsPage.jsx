import React, { useState } from 'react';

export default function SettingsPage() {
  const [temperature, setTemperature] = useState(0.2);
  const [maxTokens, setMaxTokens] = useState(1024);
  const [selectedModel, setSelectedModel] = useState('llama3-70b');
  const [status, setStatus] = useState('');

  const handleSave = (e) => {
    e.preventDefault();
    setStatus('Configuration updated successfully!');
    setTimeout(() => setStatus(''), 3000);
  };

  return (
    <section className="space-y-6 pb-12 max-w-4xl mx-auto w-full">
      <div className="border-b border-border pb-4">
        <h2 className="text-xl font-bold text-text uppercase tracking-tight">System Settings</h2>
        <p className="text-xs text-muted">Adjust model temperature parameters, query token limits, and fallback clusters</p>
      </div>

      {status && (
        <div className="rounded-lg border border-success/20 bg-success/5 px-4 py-3 text-xs font-semibold text-success">
          {status}
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white border border-border rounded-xl p-6 shadow-soft space-y-6">
        
        {/* Model parameters */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-text uppercase tracking-wider border-b border-border pb-2">Model Parameters</h3>
          
          {/* Temperature */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-text uppercase">Inference Temperature</label>
              <span className="text-xs font-bold text-primary">{temperature}</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="1.0" 
              step="0.1" 
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <p className="text-[10px] text-muted">Lower temperatures yield factual answers, higher temperatures promote user engagement.</p>
          </div>

          {/* Max Tokens */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-text uppercase">Max Tokens</label>
              <span className="text-xs font-bold text-primary">{maxTokens}</span>
            </div>
            <input 
              type="range" 
              min="256" 
              max="4096" 
              step="128" 
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="w-full h-1.5 bg-border rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <p className="text-[10px] text-muted">Defines maximum token bounds generated in a single query response cycle.</p>
          </div>

          {/* Default Model */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-text uppercase block">Fallback Model Cluster</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full bg-white border border-border rounded-lg py-2 px-3 text-xs font-semibold focus:outline-none focus:border-primary text-text"
            >
              <option value="llama3-70b">Llama 3 70B (Groq cluster)</option>
              <option value="llama3-8b">Llama 3 8B (Groq mini)</option>
              <option value="llama-3.1-405b">Llama 3.1 405B (Heavy computing cluster)</option>
            </select>
          </div>

        </div>

        {/* Integration API Keys */}
        <div className="space-y-4 pt-4 border-t border-border">
          <h3 className="text-sm font-bold text-text uppercase tracking-wider">Credentials & API Integrations</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] text-muted font-bold uppercase block tracking-wider mb-1">Groq Cluster Endpoint</label>
              <input 
                type="password" 
                value="••••••••••••••••••••••••••••••••" 
                disabled 
                className="w-full bg-bg/50 border border-border rounded-lg py-2 px-3 text-xs font-semibold text-muted"
              />
            </div>

            <div>
              <label className="text-[10px] text-muted font-bold uppercase block tracking-wider mb-1">Gemini Inference Token</label>
              <input 
                type="password" 
                value="••••••••••••••••••••••••••••••••" 
                disabled 
                className="w-full bg-bg/50 border border-border rounded-lg py-2 px-3 text-xs font-semibold text-muted"
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="pt-4 border-t border-border flex justify-end gap-2">
          <button 
            type="submit"
            className="bg-primary text-white hover:bg-primary/95 text-xs font-bold uppercase px-4 py-2.5 rounded-lg shadow-soft transition-colors"
          >
            Save Parameter Configurations
          </button>
        </div>

      </form>
    </section>
  );
}
