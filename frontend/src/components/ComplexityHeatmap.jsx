import React from 'react';

// ComplexityHeatmap - Visual grid showing complexity of each file
export default function ComplexityHeatmap({ analysisData }) {
    if (!analysisData?.architecture_map?.listOfFiles) {
        return <div className="text-gray-400">No complexity data available</div>;
    }

    const files = analysisData.architecture_map.listOfFiles
        .map(file => {
            const functions = file.listOfFunctions || [];
            const avgComplexity = functions.length > 0
                ? functions.reduce((sum, f) => sum + (f.complexity || 1), 0) / functions.length
                : 0;

            return {
                path: file.filePath,
                name: file.filePath.split('/').pop(),
                functions: functions.length,
                complexity: avgComplexity,
                maxComplexity: Math.max(...functions.map(f => f.complexity || 1), 0)
            };
        })
        .filter(f => f.functions > 0)
        .sort((a, b) => b.complexity - a.complexity);

    const maxComplexity = Math.max(...files.map(f => f.complexity), 1);

    return (
        <div className="w-full h-full overflow-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 p-2">
                {files.map(file => (
                    <FileHeatmapCard key={file.path} file={file} maxComplexity={maxComplexity} />
                ))}
            </div>

            {/* Legend */}
            <div className="mt-4 p-3 border-t border-[#333] flex items-center justify-center gap-4">
                <span className="text-sm text-gray-400">Complexity:</span>
                <div className="flex items-center gap-2">
                    <div className="w-6 h-4 rounded" style={{ backgroundColor: '#22c55e' }}></div>
                    <span className="text-xs text-gray-400">Low</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-6 h-4 rounded" style={{ backgroundColor: '#eab308' }}></div>
                    <span className="text-xs text-gray-400">Medium</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-6 h-4 rounded" style={{ backgroundColor: '#ef4444' }}></div>
                    <span className="text-xs text-gray-400">High</span>
                </div>
            </div>
        </div>
    );
}

function FileHeatmapCard({ file, maxComplexity }) {
    // Calculate color based on complexity (0-1 normalized)
    const normalized = Math.min(file.complexity / Math.max(maxComplexity, 5), 1);
    const color = getComplexityColor(normalized);

    return (
        <div
            className="p-3 rounded-lg border border-[#333] hover:border-[#555] transition-all cursor-pointer"
            style={{
                backgroundColor: `${color}20`,
                borderLeftColor: color,
                borderLeftWidth: '4px'
            }}
        >
            <div className="font-mono text-sm text-white truncate" title={file.path}>
                {file.name}
            </div>
            <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-gray-400">
                    {file.functions} function{file.functions !== 1 ? 's' : ''}
                </span>
                <span
                    className="text-xs font-bold px-2 py-0.5 rounded"
                    style={{ backgroundColor: color, color: normalized > 0.5 ? '#fff' : '#000' }}
                >
                    {file.complexity.toFixed(1)}
                </span>
            </div>
        </div>
    );
}

function getComplexityColor(normalized) {
    // Green (0) -> Yellow (0.5) -> Red (1)
    if (normalized < 0.3) return '#22c55e'; // Green
    if (normalized < 0.5) return '#84cc16'; // Lime
    if (normalized < 0.7) return '#eab308'; // Yellow
    if (normalized < 0.85) return '#f97316'; // Orange
    return '#ef4444'; // Red
}
