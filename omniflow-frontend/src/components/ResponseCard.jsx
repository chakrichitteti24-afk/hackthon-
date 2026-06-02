import React from 'react';
import ModelBadge from './ModelBadge';

export default function ResponseCard({ content, sentiment, meta }) {
  // Helper to categorize responses based on query/response keywords
  const determineCategory = (txt = '') => {
    const textLower = txt.toLowerCase();
    if (textLower.includes('phone') || textLower.includes('iphone') || textLower.includes('samsung') || textLower.includes('mobile')) {
      return '📱 Smartphones';
    }
    if (textLower.includes('laptop') || textLower.includes('macbook') || textLower.includes('thinkpad') || textLower.includes('dell')) {
      return '💻 Laptops';
    }
    if (textLower.includes('market') || textLower.includes('trends') || textLower.includes('analysis') || textLower.includes('growth')) {
      return '📊 Market Analysis';
    }
    if (textLower.includes('compare') || textLower.includes('vs') || textLower.includes('comparison')) {
      return '⚔️ Product Comparison';
    }
    if (textLower.includes('support') || textLower.includes('help') || textLower.includes('issue') || textLower.includes('warranty')) {
      return '🛠️ Support';
    }
    return '💡 Product Intelligence';
  };

  const category = determineCategory(content);

  // Parse sections dynamically from LLM response
  // We can look for sections or separate by paragraphs / lists
  const parseInsightsAndRecs = (text = '') => {
    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
    const keyInsights = [];
    const recommendations = [];
    const generalParagraphs = [];

    lines.forEach(line => {
      // Check if it looks like a list item
      if (line.startsWith('-') || line.startsWith('*') || /^\d+\./.test(line)) {
        const cleanLine = line.replace(/^[-*\d.]+\s*/, '');
        if (cleanLine.toLowerCase().includes('recommend') || cleanLine.toLowerCase().includes('suggest') || recommendations.length > keyInsights.length) {
          recommendations.push(cleanLine);
        } else {
          keyInsights.push(cleanLine);
        }
      } else {
        generalParagraphs.push(line);
      }
    });

    // Fallbacks if lists are empty
    if (keyInsights.length === 0 && generalParagraphs.length > 0) {
      // Use the first few sentences as insights
      keyInsights.push(generalParagraphs[0]);
    }
    if (recommendations.length === 0 && generalParagraphs.length > 1) {
      recommendations.push(...generalParagraphs.slice(1));
    }

    return {
      insights: keyInsights.slice(0, 3),
      recommendations: recommendations.length > 0 ? recommendations : ['No specific actions required. Platform synced.'],
      paragraphs: generalParagraphs
    };
  };

  const { insights, recommendations } = parseInsightsAndRecs(content);

  // Confidence is either computed or default
  const confidenceScore = meta?.confidence || 85;

  return (
    <div className="bg-white rounded-xl border border-border shadow-soft overflow-hidden transition-all duration-300 hover:shadow-premium max-w-full">
      {/* Header section with Category */}
      <div className="bg-bg/40 px-5 py-4 border-b border-border flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-muted">Category</span>
          <span className="text-sm font-bold text-text bg-white px-2.5 py-1 rounded-md border border-border">
            {category}
          </span>
        </div>
        {sentiment && (
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border ${
            sentiment.includes('positive') ? 'bg-success/5 text-success border-success/20' :
            sentiment.includes('negative') || sentiment.includes('angry') ? 'bg-error/5 text-error border-error/20' :
            'bg-warning/5 text-warning border-warning/20'
          }`}>
            Sentiment: {sentiment}
          </span>
        )}
      </div>

      {/* Main Body Grid */}
      <div className="p-5 space-y-4">
        {/* Key Insights Section */}
        {insights.length > 0 && (
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-muted uppercase tracking-wider">Key Insights</h4>
            <div className="bg-primary/5 border border-primary/10 rounded-lg p-3 space-y-2">
              {insights.map((insight, idx) => (
                <div key={idx} className="flex gap-2 text-sm text-text leading-relaxed font-medium">
                  <span className="text-primary font-bold">•</span>
                  <span>{insight}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Recommendations Section */}
        <div className="space-y-1.5 pt-1">
          <h4 className="text-xs font-bold text-muted uppercase tracking-wider">Recommendations</h4>
          <div className="space-y-2">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="flex gap-2.5 text-sm text-text leading-relaxed font-medium">
                <span className="text-secondary font-bold">✓</span>
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Confidence and Knowledge Sources Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-border mt-2">
          {/* Confidence bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <h4 className="text-xs font-bold text-muted uppercase tracking-wider">Confidence Level</h4>
              <span className="text-xs font-bold text-success">{confidenceScore}%</span>
            </div>
            <div className="h-2 w-full bg-border rounded-full overflow-hidden">
              <div 
                className="h-full bg-success rounded-full" 
                style={{ width: `${confidenceScore}%` }} 
              />
            </div>
          </div>

          {/* Knowledge Sources */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-muted uppercase tracking-wider">Knowledge Sources</h4>
            <div className="flex flex-wrap gap-1.5">
              <ModelBadge text={meta?.llm?.toUpperCase() || 'LLM Engine'} variant={meta?.llm?.toLowerCase()} />
              {meta?.sources && meta.sources.length > 0 ? (
                meta.sources.map((source, sIdx) => (
                  <ModelBadge key={sIdx} text={`✓ ${source}`} variant="verified" />
                ))
              ) : (
                <span className="text-[10px] text-muted font-bold uppercase tracking-wider">No data available</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
