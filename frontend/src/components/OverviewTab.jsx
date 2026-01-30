import React from 'react';

export default function OverviewTab({ summary, loading, error, onRetry }) {
  const ai = summary?.ai_summary;
  const stats = summary?.project_stats;

  // Loading state with skeleton
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass rounded-2xl p-6 h-64" />
          <div className="glass rounded-2xl p-6 h-64" />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="glass rounded-2xl p-8 text-center">
        <span className="text-4xl mb-4 block">❌</span>
        <p className="text-[var(--accent-orange)] mb-4">{error}</p>
        <button onClick={onRetry} className="btn-primary">
          Retry Analysis
        </button>
      </div>
    );
  }

  // No data
  if (!summary) {
    return (
      <div className="glass rounded-2xl p-8 text-center">
        <span className="text-4xl mb-4 block">📭</span>
        <p className="text-[var(--text-secondary)]">No project data available.</p>
      </div>
    );
  }

  const healthScore = stats?.complexity_metrics?.code_health_score || 0;
  const healthColor = healthScore >= 70 ? 'var(--accent-cyan)' : healthScore >= 40 ? 'var(--accent-yellow)' : 'var(--accent-orange)';

  return (
    <div className="space-y-6">
      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* AI Summary Card */}
        <div className="lg:col-span-2 glass rounded-2xl p-6 animate-fade-in">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-3">
            <span className="text-2xl">🤖</span>
            <span className="text-gradient">AI Summary</span>
          </h3>

          <p className="text-[var(--text-primary)] leading-relaxed mb-6">
            {ai?.overview || 'No summary available'}
          </p>

          {/* Strengths */}
          {ai?.strengths?.length > 0 && (
            <div className="glass-accent rounded-xl p-4 mb-4">
              <h4 className="text-[var(--accent-cyan)] font-semibold mb-3 flex items-center gap-2">
                💪 Strengths
              </h4>
              <ul className="space-y-2">
                {ai.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-[var(--accent-cyan)]">✓</span>
                    <span className="text-[var(--text-secondary)]">{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {ai?.recommendations?.length > 0 && (
            <div className="glass rounded-xl p-4 border-l-4 border-[var(--accent-yellow)]">
              <h4 className="text-[var(--accent-yellow)] font-semibold mb-3 flex items-center gap-2">
                💡 Recommendations
              </h4>
              <ul className="space-y-2">
                {ai.recommendations.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-[var(--accent-yellow)]">→</span>
                    <span className="text-[var(--text-secondary)]">{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Metrics Card */}
        <div className="glass rounded-2xl p-6 animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <h3 className="text-xl font-bold mb-4 flex items-center gap-3">
            <span className="text-2xl">📊</span>
            <span>Metrics</span>
          </h3>

          {/* Health Score Circle */}
          <div className="flex justify-center mb-6">
            <div
              className="w-28 h-28 rounded-full flex items-center justify-center border-4"
              style={{ borderColor: healthColor }}
            >
              <div className="text-center">
                <div className="text-3xl font-bold" style={{ color: healthColor }}>
                  {healthScore}
                </div>
                <div className="text-xs text-[var(--text-muted)]">Health</div>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="space-y-3">
            <StatRow icon="📁" label="Files" value={stats?.file_stats?.total_files} />
            <StatRow icon="⚙️" label="Functions" value={stats?.function_stats?.total_functions} />
            <StatRow icon="🔗" label="Calls" value={stats?.function_stats?.total_function_calls} />

            <div className="border-t border-[var(--border-default)] my-3" />

            <StatRow icon="📈" label="Avg Complexity" value={stats?.function_stats?.average_complexity} />
            <StatRow icon="📦" label="Size" value={stats?.complexity_metrics?.project_size} />
          </div>

          {/* Languages */}
          {stats?.language_stats?.language_percentages && (
            <>
              <div className="border-t border-[var(--border-default)] my-4" />
              <h4 className="text-sm font-semibold mb-3 text-[var(--text-secondary)]">Languages</h4>
              <div className="space-y-2">
                {Object.entries(stats.language_stats.language_percentages).slice(0, 4).map(([lang, percent]) => (
                  <div key={lang} className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-[var(--bg-secondary)] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[var(--accent-cyan)] to-[var(--accent-blue)]"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <span className="text-xs text-[var(--text-muted)] w-12">{lang}</span>
                    <span className="text-xs font-semibold w-10 text-right">{percent}%</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Architecture & Technology Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {ai?.architecture_insights && (
          <div className="glass rounded-xl p-5 border-l-4 border-[var(--accent-blue)] animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <h4 className="text-[var(--accent-blue)] font-semibold mb-2 flex items-center gap-2">
              🏗️ Architecture
            </h4>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              {ai.architecture_insights}
            </p>
          </div>
        )}

        {ai?.technology_assessment && (
          <div className="glass rounded-xl p-5 border-l-4 border-[var(--accent-purple)] animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <h4 className="text-[var(--accent-purple)] font-semibold mb-2 flex items-center gap-2">
              ⚡ Technology
            </h4>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              {ai.technology_assessment}
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-[var(--text-muted)] pt-4">
        Analysis by {ai?.source || 'AI'} • Generated {summary?.generated_at || '—'}
      </div>
    </div>
  );
}

function StatRow({ icon, label, value }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span>{icon}</span>
        <span className="text-sm text-[var(--text-secondary)]">{label}</span>
      </div>
      <span className="font-semibold">{value ?? '—'}</span>
    </div>
  );
}
