// src/components/FunctionCallGraph.jsx
import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

import convertToGraph from '../services/convertToGraph';

const FunctionCallGraph = ({ architectureData }) => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [isReady, setIsReady] = useState(false);

  // Filter state
  const [minComplexity, setMinComplexity] = useState(1);
  const [minConnections, setMinConnections] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFiles, setShowFiles] = useState(true);
  const [stats, setStats] = useState({ total: 0, visible: 0, edges: 0 });

  // Wait for container
  useEffect(() => {
    if (!containerRef.current) return;
    const timer = setTimeout(() => setIsReady(true), 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!architectureData || !containerRef.current || !isReady) return;

    const rect = containerRef.current.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    // Destroy previous
    if (cyRef.current && !cyRef.current.destroyed()) {
      cyRef.current.destroy();
    }

    // Build and filter elements
    const allElements = convertToGraph(architectureData);
    const filteredElements = filterElements(allElements, {
      minComplexity,
      minConnections,
      searchTerm,
      showFiles
    });

    // Update stats
    const allNodes = allElements.filter(el => !el.data.source);
    const visibleNodes = filteredElements.filter(el => !el.data.source);
    const edges = filteredElements.filter(el => el.data.source);
    setStats({
      total: allNodes.length,
      visible: visibleNodes.length,
      edges: edges.length
    });

    if (filteredElements.length === 0) {
      return;
    }

    try {
      const cy = cytoscape({
        container: containerRef.current,
        boxSelectionEnabled: false,
        style: [
          {
            selector: 'node[parent]',
            css: {
              shape: 'ellipse',
              'background-color': '#2E7FFF',
              content: 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': '10px',
              'font-weight': 'bold',
              color: '#FFFFFF',
              'text-outline-color': '#000000',
              'text-outline-width': 1,
              width: 50,
              height: 50,
              'border-width': 2,
              'border-color': '#00E0B8',
            },
          },
          {
            selector: ':parent',
            css: {
              'background-color': 'data(fileColor)',
              'background-opacity': 0.3,
              content: 'data(label)',
              'text-valign': 'top',
              'text-halign': 'center',
              'font-size': '11px',
              'font-weight': 'bold',
              color: '#00FFD1',
              'text-outline-color': '#000000',
              'text-outline-width': 1,
              shape: 'round-rectangle',
              'corner-radius': 8,
              padding: 15,
              'border-width': 2,
              'border-color': '#00E0B8',
              'border-opacity': 0.6,
            },
          },
          {
            selector: 'edge',
            css: {
              'curve-style': 'bezier',
              'target-arrow-shape': 'triangle',
              'line-color': '#555',
              'target-arrow-color': '#555',
              width: 1.5,
              opacity: 0.5,
            },
          },
          {
            selector: '.highlighted',
            css: {
              'background-color': '#FF4444',
              'line-color': '#FF6B35',
              'target-arrow-color': '#FF6B35',
              'border-color': '#FFD700',
              'border-width': 3,
              opacity: 1,
            },
          },
          {
            selector: '.dimmed',
            css: {
              opacity: 0.2,
            },
          },
        ],
        elements: filteredElements,
        layout: {
          name: 'cose',
          animate: false,
          nodeRepulsion: 6000,
          idealEdgeLength: 60,
          edgeElasticity: 80,
          gravity: 30,
          fit: true,
          padding: 30,
        },
      });

      cyRef.current = cy;

      // Click handler
      cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        cy.elements().removeClass('highlighted dimmed');

        // Highlight clicked node and its connections
        node.addClass('highlighted');
        node.connectedEdges().addClass('highlighted');
        node.neighborhood('node').addClass('highlighted');

        // Dim everything else
        cy.elements().not(node.union(node.connectedEdges()).union(node.neighborhood())).addClass('dimmed');
      });

      // Click on background to reset
      cy.on('tap', (evt) => {
        if (evt.target === cy) {
          cy.elements().removeClass('highlighted dimmed');
        }
      });

    } catch (error) {
      console.error('[FunctionCallGraph] Error:', error);
    }

    return () => {
      if (cyRef.current && !cyRef.current.destroyed()) {
        cyRef.current.destroy();
      }
    };
  }, [architectureData, isReady, minComplexity, minConnections, searchTerm, showFiles]);

  return (
    <div className="w-full h-full flex flex-col">
      {/* Filter Controls */}
      <div className="flex flex-wrap gap-4 p-3 bg-[#1a1a1a] border-b border-[#333] mb-2">
        {/* Search */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">🔍</span>
          <input
            type="text"
            placeholder="Search functions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-[#252525] border border-[#444] rounded px-2 py-1 text-sm text-white w-40"
          />
        </div>

        {/* Min Complexity */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Min Complexity:</span>
          <input
            type="range"
            min="1"
            max="10"
            value={minComplexity}
            onChange={(e) => setMinComplexity(Number(e.target.value))}
            className="w-20"
          />
          <span className="text-xs text-[#4FB3FF] w-4">{minComplexity}</span>
        </div>

        {/* Min Connections */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Min Calls:</span>
          <input
            type="range"
            min="0"
            max="5"
            value={minConnections}
            onChange={(e) => setMinConnections(Number(e.target.value))}
            className="w-20"
          />
          <span className="text-xs text-[#4FB3FF] w-4">{minConnections}</span>
        </div>

        {/* Show Files Toggle */}
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showFiles}
            onChange={(e) => setShowFiles(e.target.checked)}
            className="form-checkbox"
          />
          <span className="text-xs text-gray-400">Group by file</span>
        </label>

        {/* Stats */}
        <div className="ml-auto text-xs text-gray-400">
          Showing <span className="text-[#00E0B8] font-bold">{stats.visible}</span> of {stats.total} nodes
          ({stats.edges} edges)
        </div>
      </div>

      {/* Graph Container */}
      <div
        ref={containerRef}
        className="flex-1"
        style={{
          minHeight: '400px',
          backgroundColor: '#0a0a0a',
        }}
      />

      {/* Help text */}
      <div className="text-xs text-gray-500 p-2 text-center">
        Click a function to highlight its connections. Click background to reset.
      </div>
    </div>
  );
};

// Filter elements based on user settings
function filterElements(elements, { minComplexity, minConnections, searchTerm, showFiles }) {
  const nodes = elements.filter(el => !el.data.source);
  const edges = elements.filter(el => el.data.source);

  // Get connection counts
  const connectionCounts = {};
  edges.forEach(edge => {
    connectionCounts[edge.data.source] = (connectionCounts[edge.data.source] || 0) + 1;
    connectionCounts[edge.data.target] = (connectionCounts[edge.data.target] || 0) + 1;
  });

  // Filter nodes
  const visibleNodeIds = new Set();
  const filteredNodes = nodes.filter(node => {
    const id = node.data.id;
    const label = (node.data.label || '').toLowerCase();
    const complexity = node.data.complexity || 1;
    const connections = connectionCounts[id] || 0;

    // Parent nodes (files) always pass through if showFiles is true
    if (!node.data.parent) {
      return showFiles;
    }

    // Apply filters
    if (complexity < minComplexity) return false;
    if (connections < minConnections) return false;
    if (searchTerm && !label.includes(searchTerm.toLowerCase())) return false;

    visibleNodeIds.add(id);
    return true;
  });

  // Include parent nodes for visible child nodes
  const parentsToKeep = new Set();
  filteredNodes.forEach(node => {
    if (node.data.parent) {
      parentsToKeep.add(node.data.parent);
    }
  });

  const finalNodes = showFiles
    ? filteredNodes.filter(n => !n.data.parent || visibleNodeIds.has(n.data.id))
      .concat(nodes.filter(n => !n.data.parent && parentsToKeep.has(n.data.id)))
    : filteredNodes.filter(n => n.data.parent);

  // Filter edges to only include visible nodes
  const finalNodeIds = new Set(finalNodes.map(n => n.data.id));
  const filteredEdges = edges.filter(edge =>
    finalNodeIds.has(edge.data.source) && finalNodeIds.has(edge.data.target)
  );

  return [...finalNodes, ...filteredEdges];
}

export default FunctionCallGraph;