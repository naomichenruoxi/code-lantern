import React, { useState, useEffect } from 'react';

const LOG_LINES = [
    "Initializing neural interface...",
    "Reading codebase structure...",
    "Parsing Abstract Syntax Trees (AST)...",
    "Analyzing function complexity...",
    "Generating dependency graph...",
    "Calculating cyclomatic complexity...",
    "Identifying code hotspots...",
    "Preparing visualization data..."
];

export default function TerminalLoader() {
    const [lines, setLines] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        if (currentIndex >= LOG_LINES.length) return;

        const timeout = setTimeout(() => {
            setLines(prev => [...prev, LOG_LINES[currentIndex]]);
            setCurrentIndex(prev => prev + 1);
        }, Math.random() * 600 + 400); // Random delay between 400-1000ms

        return () => clearTimeout(timeout);
    }, [currentIndex]);

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md rounded-2xl">
            <div className="w-full max-w-md p-6 font-mono text-sm">
                <div className="flex items-center gap-2 mb-4 border-b border-gray-800 pb-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-gray-500 text-xs ml-2">analysis_engine.exe</span>
                </div>

                <div className="space-y-2 text-[#00E0B8]">
                    {lines.map((line, i) => (
                        <div key={i} className="flex gap-2">
                            <span className="text-gray-500">{`>`}</span>
                            <span className="typing-effect">{line}</span>
                        </div>
                    ))}
                    <div className="flex gap-2 animate-pulse">
                        <span className="text-gray-500">{`>`}</span>
                        <span className="w-2 h-5 bg-[#00E0B8]" />
                    </div>
                </div>
            </div>
        </div>
    );
}
