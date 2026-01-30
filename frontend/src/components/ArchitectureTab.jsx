import React, { useState } from 'react';
import FunctionCallGraph from './FunctionCallGraph';
import ComplexityHeatmap from './ComplexityHeatmap';
import FileDependencyGraph from './FileDependencyGraph';
import VisualTreeDiagram from './VisualTreeDiagram';

export default function ArchitectureTab({ analysisData, loading }) {
  const [activeView, setActiveView] = useState('tree');

  const views = [
    { id: 'tree', label: '🌳 Tree View', icon: '🌳' },
    { id: 'deps', label: '🔗 Dependencies', icon: '🔗' },
    { id: 'graph', label: '⚙️ Call Graph', icon: '⚙️' },
    { id: 'heatmap', label: '🔥 Heatmap', icon: '🔥' },
  ];

  if (loading) {
    return (
      <div className="glass rounded-2xl p-8 animate-pulse">
        <div className="h-8 bg-[var(--bg-secondary)] rounded w-48 mb-4" />
        <div className="h-96 bg-[var(--bg-secondary)] rounded-xl" />
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="glass rounded-2xl p-8 text-center">
        <span className="text-4xl block mb-4">⏳</span>
        <p className="text-[var(--text-secondary)]">Waiting for analysis data...</p>
      </div>
    );
  }

  const architectureData = analysisData?.architecture_map;
  let totalFunctions = 0;
  let filesWithFunctions = 0;

  if (architectureData?.listOfFiles) {
    architectureData.listOfFiles.forEach(file => {
      if (file.listOfFunctions?.length > 0) {
        filesWithFunctions++;
        totalFunctions += file.listOfFunctions.length;
      }
    });
  }

  const MAX_FUNCTIONS = 200;
  const isTooLargeForGraph = totalFunctions > MAX_FUNCTIONS;

  return (
    <div className="space-y-4">
      {/* Sub-tabs */}
      <div className="flex flex-wrap gap-2">
        {views.map(view => (
          <button
            key={view.id}
            onClick={() => setActiveView(view.id)}
            className={`
              px-4 py-2 rounded-xl font-medium text-sm transition-all
              ${activeView === view.id
                ? 'bg-[var(--accent-cyan)] text-black'
                : 'glass text-[var(--text-secondary)] hover:text-white hover:border-[var(--accent-blue)]'
              }
            `}
          >
            {view.label}
          </button>
        ))}

        {/* Stats badge */}
        <div className="ml-auto flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--bg-secondary)] text-xs text-[var(--text-muted)]">
          <span>📁 {filesWithFunctions} files</span>
          <span className="text-[var(--border-default)]">•</span>
          <span>⚙️ {totalFunctions} functions</span>
        </div>
      </div>

      {/* Content Area */}
      <div className="glass rounded-2xl overflow-hidden" style={{ minHeight: '500px' }}>
        {activeView === 'tree' && (
          <div className="p-4 h-full animate-fade-in">
            <VisualTreeDiagram analysisData={analysisData} />
          </div>
        )}

        {activeView === 'deps' && (
          <div className="p-4 h-full animate-fade-in">
            <FileDependencyGraph analysisData={analysisData} />
          </div>
        )}

        {activeView === 'graph' && (
          isTooLargeForGraph ? (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center">
              <span className="text-5xl mb-4">⚠️</span>
              <h3 className="text-xl font-bold text-[var(--accent-yellow)] mb-2">
                Project Too Large
              </h3>
              <p className="text-[var(--text-secondary)] mb-4">
                This project has <span className="text-[var(--accent-blue)] font-bold">{totalFunctions}</span> functions.
              </p>
              <p className="text-sm text-[var(--text-muted)]">
                Call graph visualization is limited to {MAX_FUNCTIONS} functions.
                <br />Try the Tree View or Dependencies instead.
              </p>
            </div>
          ) : (
            <div className="animate-fade-in h-full">
              <FunctionCallGraph architectureData={architectureData} />
            </div>
          )
        )}

        {activeView === 'heatmap' && (
          <div className="p-4 h-full overflow-auto animate-fade-in">
            <ComplexityHeatmap analysisData={analysisData} />
          </div>
        )}
      </div>
    </div>
  );
}
