import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

// FileDependencyGraph - Shows which files depend on other files
export default function FileDependencyGraph({ analysisData }) {
    const containerRef = useRef(null);
    const cyRef = useRef(null);
    const [isReady, setIsReady] = useState(false);

    // Build file-level dependencies from function calls
    const dependencies = buildFileDependencies(analysisData);

    useEffect(() => {
        if (!containerRef.current) return;
        const timer = setTimeout(() => setIsReady(true), 100);
        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        if (!isReady || !containerRef.current || !dependencies) return;

        const rect = containerRef.current.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        // Destroy previous
        if (cyRef.current && !cyRef.current.destroyed()) {
            cyRef.current.destroy();
        }

        const elements = buildElements(dependencies);
        console.log('[FileDependencyGraph] Elements:', elements.length);

        if (elements.length === 0) {
            return;
        }

        const cy = cytoscape({
            container: containerRef.current,
            elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': 'data(color)',
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '10px',
                        'color': '#fff',
                        'text-outline-color': '#000',
                        'text-outline-width': 1,
                        'width': 'data(size)',
                        'height': 'data(size)',
                        'border-width': 2,
                        'border-color': '#00E0B8',
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'curve-style': 'bezier',
                        'target-arrow-shape': 'triangle',
                        'line-color': '#555',
                        'target-arrow-color': '#555',
                        'width': 2,
                        'opacity': 0.6,
                    }
                },
                {
                    selector: '.highlighted',
                    style: {
                        'background-color': '#FF6B35',
                        'line-color': '#FF6B35',
                        'target-arrow-color': '#FF6B35',
                        'border-color': '#FFD700',
                    }
                }
            ],
            layout: {
                name: 'cose',
                animate: false,
                nodeRepulsion: 8000,
                idealEdgeLength: 100,
                fit: true,
                padding: 50,
            }
        });

        cyRef.current = cy;

        // Click to highlight connections
        cy.on('tap', 'node', (evt) => {
            cy.elements().removeClass('highlighted');
            const node = evt.target;
            node.addClass('highlighted');
            node.connectedEdges().addClass('highlighted');
            node.neighborhood('node').addClass('highlighted');
        });

        return () => {
            if (cyRef.current && !cyRef.current.destroyed()) {
                cyRef.current.destroy();
            }
        };
    }, [dependencies, isReady]);

    if (!dependencies || dependencies.files.length === 0) {
        return (
            <div className="w-full h-full flex items-center justify-center">
                <div className="text-gray-400">No dependency data available</div>
            </div>
        );
    }

    return (
        <div className="w-full h-full flex flex-col">
            <div className="text-xs text-gray-400 mb-2">
                Click a file to highlight its connections. Files are connected when functions call across files.
            </div>
            <div
                ref={containerRef}
                style={{ flex: 1, minHeight: '450px', backgroundColor: '#0a0a0a', borderRadius: '8px' }}
            />
        </div>
    );
}

function buildFileDependencies(analysisData) {
    if (!analysisData?.architecture_map?.listOfFiles) {
        return { files: [], edges: [] };
    }

    const files = analysisData.architecture_map.listOfFiles;
    const fileMap = new Map(); // fileName -> { functions, calls }
    const allFunctions = new Map(); // functionName -> fileName

    // Index all functions by file
    files.forEach(file => {
        const fileName = file.filePath.split('/').pop();
        const funcs = file.listOfFunctions || [];

        fileMap.set(file.filePath, {
            name: fileName,
            path: file.filePath,
            functions: funcs.length,
            outgoing: new Set(),
            incoming: new Set()
        });

        funcs.forEach(f => {
            const baseName = f.functionName.includes('-')
                ? f.functionName.split('-').pop()
                : f.functionName;
            allFunctions.set(baseName, file.filePath);
        });
    });

    // Build edges based on function calls
    const edges = [];
    const edgeSet = new Set();

    files.forEach(file => {
        const funcs = file.listOfFunctions || [];
        funcs.forEach(func => {
            const calls = func.calls || [];
            calls.forEach(calledFunc => {
                const targetFile = allFunctions.get(calledFunc);
                if (targetFile && targetFile !== file.filePath) {
                    const edgeKey = `${file.filePath}->${targetFile}`;
                    if (!edgeSet.has(edgeKey)) {
                        edgeSet.add(edgeKey);
                        edges.push({ source: file.filePath, target: targetFile });

                        fileMap.get(file.filePath)?.outgoing.add(targetFile);
                        fileMap.get(targetFile)?.incoming.add(file.filePath);
                    }
                }
            });
        });
    });

    return {
        files: Array.from(fileMap.values()).filter(f => f.functions > 0),
        edges
    };
}

function buildElements(dependencies) {
    const elements = [];
    const colors = [
        '#4FB3FF', '#FF6B9D', '#00E0B8', '#FFD93D', '#FF6B35',
        '#A855F7', '#22D3EE', '#F472B6', '#34D399', '#FBBF24'
    ];

    // Add file nodes
    dependencies.files.forEach((file, i) => {
        const connections = file.outgoing.size + file.incoming.size;
        elements.push({
            data: {
                id: file.path,
                label: file.name,
                color: colors[i % colors.length],
                size: Math.max(40, Math.min(80, 30 + file.functions * 3 + connections * 5))
            }
        });
    });

    // Add edges
    dependencies.edges.forEach(edge => {
        elements.push({
            data: {
                id: `${edge.source}->${edge.target}`,
                source: edge.source,
                target: edge.target
            }
        });
    });

    return elements;
}
