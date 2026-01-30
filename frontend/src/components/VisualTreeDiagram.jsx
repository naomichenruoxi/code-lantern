import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

// VisualTreeDiagram - Graphical tree visualization of project structure
export default function VisualTreeDiagram({ analysisData }) {
    const containerRef = useRef(null);
    const cyRef = useRef(null);
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        if (!containerRef.current) return;
        const timer = setTimeout(() => setIsReady(true), 100);
        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        if (!isReady || !containerRef.current) return;
        if (!analysisData?.architecture_map?.listOfFiles) return;

        const rect = containerRef.current.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        // Destroy previous instance
        if (cyRef.current && !cyRef.current.destroyed()) {
            cyRef.current.destroy();
        }

        const elements = buildTreeElements(analysisData.architecture_map.listOfFiles);
        console.log('[VisualTreeDiagram] Elements:', elements.length);

        if (elements.length === 0) return;

        const cy = cytoscape({
            container: containerRef.current,
            elements,
            style: [
                // Root node
                {
                    selector: 'node[type="root"]',
                    style: {
                        'background-color': '#4FB3FF',
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '14px',
                        'font-weight': 'bold',
                        'color': '#fff',
                        'text-outline-color': '#000',
                        'text-outline-width': 2,
                        'width': 80,
                        'height': 80,
                        'shape': 'round-rectangle',
                    }
                },
                // Folder nodes
                {
                    selector: 'node[type="folder"]',
                    style: {
                        'background-color': '#00E0B8',
                        'label': 'data(label)',
                        'text-valign': 'bottom',
                        'text-margin-y': 5,
                        'font-size': '11px',
                        'color': '#00E0B8',
                        'width': 50,
                        'height': 50,
                        'shape': 'round-rectangle',
                    }
                },
                // File nodes
                {
                    selector: 'node[type="file"]',
                    style: {
                        'background-color': 'data(color)',
                        'label': 'data(label)',
                        'text-valign': 'bottom',
                        'text-margin-y': 5,
                        'font-size': '9px',
                        'color': '#ccc',
                        'width': 35,
                        'height': 35,
                        'shape': 'ellipse',
                    }
                },
                // Edges
                {
                    selector: 'edge',
                    style: {
                        'curve-style': 'bezier',
                        'line-color': '#444',
                        'width': 2,
                        'opacity': 0.7,
                    }
                },
                // Highlighted
                {
                    selector: '.highlighted',
                    style: {
                        'background-color': '#FFD93D',
                        'line-color': '#FFD93D',
                        'border-width': 3,
                        'border-color': '#fff',
                    }
                }
            ],
            layout: {
                name: 'breadthfirst',
                directed: true,
                roots: '#root',
                padding: 30,
                spacingFactor: 1.2,
                animate: false,
            }
        });

        cyRef.current = cy;

        // Click to highlight path to root
        cy.on('tap', 'node', (evt) => {
            cy.elements().removeClass('highlighted');
            const node = evt.target;

            // Highlight path to root
            let current = node;
            while (current) {
                current.addClass('highlighted');
                const incomers = current.incomers('edge');
                incomers.addClass('highlighted');
                current = incomers.sources().first();
                if (current.length === 0) break;
                current = current.first();
            }
        });

        return () => {
            if (cyRef.current && !cyRef.current.destroyed()) {
                cyRef.current.destroy();
            }
        };
    }, [analysisData, isReady]);

    if (!analysisData?.architecture_map?.listOfFiles) {
        return (
            <div className="w-full h-full flex items-center justify-center">
                <div className="text-gray-400">No directory data available</div>
            </div>
        );
    }

    return (
        <div className="w-full h-full flex flex-col">
            <div className="text-xs text-gray-400 mb-2">
                Click a node to highlight the path from root. Folders are green, files are colored by type.
            </div>
            <div
                ref={containerRef}
                style={{ flex: 1, minHeight: '450px', backgroundColor: '#0a0a0a', borderRadius: '8px' }}
            />
        </div>
    );
}

function buildTreeElements(files) {
    const elements = [];
    const nodeSet = new Set();

    // File type colors
    const fileColors = {
        py: '#3776AB', js: '#F7DF1E', jsx: '#61DAFB', ts: '#3178C6', tsx: '#61DAFB',
        java: '#ED8B00', cpp: '#00599C', rs: '#DEA584', json: '#888', md: '#fff',
        html: '#E34F26', css: '#1572B6', sql: '#336791'
    };

    // Add root node
    elements.push({
        data: { id: 'root', label: '📦 Project', type: 'root' }
    });
    nodeSet.add('root');

    // Process each file to build tree
    files.forEach(file => {
        const parts = file.filePath.split('/').filter(p => p);
        let parentId = 'root';

        parts.forEach((part, i) => {
            const isFile = i === parts.length - 1;
            const nodeId = parts.slice(0, i + 1).join('/');

            if (!nodeSet.has(nodeId)) {
                nodeSet.add(nodeId);

                const ext = isFile ? part.split('.').pop() : null;

                elements.push({
                    data: {
                        id: nodeId,
                        label: part,
                        type: isFile ? 'file' : 'folder',
                        color: isFile ? (fileColors[ext] || '#888') : '#00E0B8'
                    }
                });

                // Edge from parent
                elements.push({
                    data: {
                        id: `${parentId}->${nodeId}`,
                        source: parentId,
                        target: nodeId
                    }
                });
            }

            parentId = nodeId;
        });
    });

    return elements;
}
