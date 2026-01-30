import React, { useState } from 'react';
import { DEMO_ANALYSIS_DATA } from "../data/demoData";

// DeepDiveTab receives data from parent - uses lazy loading for function details
export default function DeepDiveTab({ analysisData, apiBase = 'http://localhost:8000', repoId }) {
  const [expandedFiles, setExpandedFiles] = useState(new Set());
  const [expandedFunctions, setExpandedFunctions] = useState(new Set());
  const [functionDetails, setFunctionDetails] = useState({});
  const [loadingFunction, setLoadingFunction] = useState(null);
  const [rateLimit, setRateLimit] = useState({ used: 0, max: 5, remaining: 5 });
  const [rateLimitError, setRateLimitError] = useState(null);

  const architectureMap = analysisData?.architecture_map;

  if (!analysisData) {
    return <div className="text-gray-400">Loading architecture...</div>;
  }

  if (!architectureMap || !architectureMap.listOfFiles) {
    return <div className="text-gray-400">No architecture data available.</div>;
  }

  const files = architectureMap.listOfFiles;

  function toggleFile(filePath) {
    const next = new Set(expandedFiles);
    if (next.has(filePath)) next.delete(filePath);
    else next.add(filePath);
    setExpandedFiles(next);
  }

  async function toggleFunction(filePath, functionName) {
    const key = `${filePath}::${functionName}`;
    const next = new Set(expandedFunctions);

    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
      // Only call API when expanding function for the first time
      if (!functionDetails[key]) {
        setLoadingFunction(key);
        setRateLimitError(null);
        try {

          // DEMO MODE CHECK
          if (repoId === 'demo-project') {
            const baseFunctionName = functionName.includes('-') ? functionName.split('-').pop() : functionName;
            const demoKey = `${filePath}::${baseFunctionName}`;
            const demoDetails = DEMO_ANALYSIS_DATA.function_details_map ? DEMO_ANALYSIS_DATA.function_details_map[demoKey] : null;

            setTimeout(() => {
              if (demoDetails) {
                setFunctionDetails(prev => ({ ...prev, [key]: demoDetails }));
              } else {
                setFunctionDetails(prev => ({
                  ...prev, [key]: {
                    inputs: "Unknown",
                    outputs: "Unknown",
                    description: "No demo data available for this function."
                  }
                }));
              }
              setLoadingFunction(null);
            }, 800); // 800ms fake AI delay
            return;
          }

          const baseFunctionName = functionName.includes('-') ? functionName.split('-').pop() : functionName;
          const res = await fetch(`${apiBase}/api/function/${repoId}?file_path=${encodeURIComponent(filePath)}&function_name=${encodeURIComponent(baseFunctionName)}`);

          if (res.status === 429) {
            const errorData = await res.json();
            setRateLimitError(errorData.detail || { message: "Rate limit reached" });
            setFunctionDetails(prev => ({ ...prev, [key]: { rateLimited: true } }));
          } else if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
          } else {
            const json = await res.json();
            setFunctionDetails(prev => ({ ...prev, [key]: json.details || json }));
            // Update rate limit info
            if (json.rate_limit) {
              setRateLimit(json.rate_limit);
            }
          }
        } catch (e) {
          setFunctionDetails(prev => ({ ...prev, [key]: { error: e.message } }));
        }
        setLoadingFunction(null);
      }
    }
    setExpandedFunctions(next);
  }

  return (
    <div className="w-full h-full flex flex-col">
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-[var(--accent-cyan)] flex items-center gap-4">
            deep dive - files & functions
            <span className="text-sm font-normal text-[var(--text-muted)]">
              ({files.length} files)
            </span>
          </h3>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-[var(--text-muted)]">AI Credits:</span>
            <span className={`font-mono ${rateLimit.remaining > 2 ? 'text-[var(--accent-cyan)]' : rateLimit.remaining > 0 ? 'text-[var(--accent-yellow)]' : 'text-[var(--accent-orange)]'}`}>
              {rateLimit.remaining}/{rateLimit.max}
            </span>
          </div>
        </div>

        {rateLimitError && (
          <div className="mt-3 p-3 bg-[var(--accent-orange)]/10 border border-[var(--accent-orange)]/30 rounded-lg">
            <p className="text-[var(--accent-orange)] text-sm font-medium">
              ⚠️ {rateLimitError.message || "Rate limit reached"}
            </p>
            <p className="text-[var(--text-muted)] text-xs mt-1">
              {rateLimitError.tip || "Upload a new project to reset your limit."}
            </p>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
        {files.map((fileData, i) => {
          const filePath = fileData.filePath;
          const functions = fileData.listOfFunctions || [];
          const isFileExpanded = expandedFiles.has(filePath);

          // Skip files with no functions
          if (functions.length === 0) return null;

          return (
            <div
              key={filePath}
              className="border border-[var(--border-default)] rounded-lg bg-[var(--bg-elevated)] overflow-hidden animate-fade-in"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div
                className="flex items-center justify-between cursor-pointer hover:bg-[var(--bg-secondary)] p-3 transition-colors"
                onClick={() => toggleFile(filePath)}
              >
                <div className="flex items-center gap-2">
                  <span className="text-[var(--accent-blue)]">{isFileExpanded ? '📂' : '📁'}</span>
                  <span className="font-mono text-sm text-[var(--text-primary)]">{filePath}</span>
                </div>
                <span className="text-[var(--text-muted)] text-xs">{functions.length} function{functions.length !== 1 ? 's' : ''}</span>
              </div>

              {isFileExpanded && (
                <div className="bg-[var(--bg-primary)] p-3 space-y-2 max-h-96 overflow-y-auto inner-scrollbar">
                  {functions.map((func) => {
                    const funcName = func.functionName;
                    const key = `${filePath}::${funcName}`;
                    const isFuncExpanded = expandedFunctions.has(key);
                    const details = functionDetails[key];
                    const isLoading = loadingFunction === key;

                    return (
                      <div key={funcName} className="border-l-2 border-[var(--accent-blue)] pl-3 py-1">
                        <div
                          className="flex items-center justify-between cursor-pointer hover:bg-[var(--bg-secondary)] p-2 rounded transition-colors group"
                          onClick={() => toggleFunction(filePath, funcName)}
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-[var(--accent-cyan)] group-hover:scale-110 transition-transform">⚙️</span>
                            <span className="font-mono text-sm text-[var(--accent-blue)]">{funcName.split('-').pop()}</span>
                          </div>
                          <span className="text-[var(--text-muted)] text-xs">{isFuncExpanded ? '▼' : '▶'}</span>
                        </div>

                        {isFuncExpanded && (
                          <div className="ml-6 mt-2 p-3 bg-[var(--bg-elevated)] border border-[var(--border-default)] rounded-lg text-sm space-y-2 glass-dark">
                            {isLoading ? (
                              <div className="text-[var(--text-secondary)] italic flex items-center gap-2">
                                <span className="animate-pulse">🤖</span> Generating AI description...
                              </div>
                            ) : !details ? (
                              <div className="text-[var(--text-secondary)] italic">Loading details...</div>
                            ) : details.error ? (
                              <div className="text-[var(--accent-orange)]">⚠️ Error: {details.error}</div>
                            ) : details.rateLimited ? (
                              <div className="p-3 bg-[var(--accent-orange)]/10 border border-[var(--accent-orange)]/30 rounded text-[var(--accent-orange)] text-sm">
                                ⚠️ <strong>Limit Reached:</strong> Cannot generate more AI descriptions for this project.
                              </div>
                            ) : (
                              <>
                                <div className="flex gap-2">
                                  <strong className="text-[var(--accent-cyan)] min-w-[80px]">Inputs:</strong>
                                  <span className="text-[var(--text-secondary)]">{String(details.inputs) || '—'}</span>
                                </div>
                                <div className="flex gap-2">
                                  <strong className="text-[var(--accent-cyan)] min-w-[80px]">Outputs:</strong>
                                  <span className="text-[var(--text-secondary)]">{String(details.outputs) || '—'}</span>
                                </div>
                                <div className="flex gap-2">
                                  <strong className="text-[var(--accent-cyan)] min-w-[80px]">Description:</strong>
                                  <span className="text-[var(--text-secondary)]">{String(details.description) || '—'}</span>
                                </div>
                                {details.calls && Array.isArray(details.calls) && details.calls.length > 0 && (
                                  <div>
                                    <strong className="text-[var(--accent-cyan)]">Calls:</strong>
                                    <ul className="list-disc ml-5 mt-1 space-y-1 text-[var(--text-secondary)]">
                                      {details.calls.map((c, i) => (<li key={i}>{String(c)}</li>))}
                                    </ul>
                                  </div>
                                )}

                                {details.code && (
                                  <div className="mt-4">
                                    <strong className="text-[var(--accent-cyan)] block mb-2">Source Code:</strong>
                                    <div className="relative group/code">
                                      <pre className="bg-[#0d1117] text-gray-300 p-4 rounded-lg overflow-x-auto font-mono text-xs leading-relaxed border border-[var(--border-default)]">
                                        <code>{details.code}</code>
                                      </pre>
                                      <div className="absolute top-2 right-2 opacity-0 group-hover/code:opacity-100 transition-opacity">
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            navigator.clipboard.writeText(details.code);
                                          }}
                                          className="text-xs bg-[var(--accent-blue)] text-white px-2 py-1 rounded hover:bg-[var(--accent-cyan)] transition-colors"
                                        >
                                          Copy
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        )
                        }
                      </div>
                    );
                  })}
                </div>
              )
              }
            </div>
          );
        })}
      </div>
    </div >
  );
}
