import React, { useEffect, useRef, useState } from 'react';

const MIN_CHART_DIMENSION = 24;

export default function ChartSurface({
  className = '',
  children,
  loadingLabel = 'Sizing chart...',
}) {
  const containerRef = useRef(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) {
      return undefined;
    }

    const updateReadiness = (width, height) => {
      setIsReady(width > MIN_CHART_DIMENSION && height > MIN_CHART_DIMENSION);
    };

    const measure = () => {
      const { width, height } = node.getBoundingClientRect();
      updateReadiness(width, height);
    };

    measure();

    if (typeof ResizeObserver === 'undefined') {
      return undefined;
    }

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) {
        return;
      }
      updateReadiness(entry.contentRect.width, entry.contentRect.height);
    });

    observer.observe(node);

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <div ref={containerRef} className={className}>
      {isReady ? (
        children
      ) : (
        <div className="flex h-full w-full items-center justify-center text-xs text-primary/45">
          {loadingLabel}
        </div>
      )}
    </div>
  );
}
