import React, { useState } from 'react';

// DirectoryTree - Collapsible tree view of project structure
export default function DirectoryTree({ analysisData }) {
    const [expandedFolders, setExpandedFolders] = useState(new Set());

    if (!analysisData?.architecture_map?.listOfFiles) {
        return <div className="text-gray-400">No directory data available</div>;
    }

    const files = analysisData.architecture_map.listOfFiles;
    const tree = buildTree(files);

    function toggleFolder(path) {
        setExpandedFolders(prev => {
            const next = new Set(prev);
            if (next.has(path)) next.delete(path);
            else next.add(path);
            return next;
        });
    }

    function expandAll() {
        const allPaths = new Set();
        function collect(node, path) {
            if (node.type === 'folder') {
                allPaths.add(path);
                Object.entries(node.children).forEach(([name, child]) => {
                    collect(child, `${path}/${name}`);
                });
            }
        }
        collect(tree, 'root');
        setExpandedFolders(allPaths);
    }

    function collapseAll() {
        setExpandedFolders(new Set());
    }

    return (
        <div className="w-full h-full overflow-auto">
            {/* Controls */}
            <div className="flex gap-2 mb-4">
                <button
                    onClick={expandAll}
                    className="px-3 py-1 text-xs bg-[#333] hover:bg-[#444] rounded transition"
                >
                    Expand All
                </button>
                <button
                    onClick={collapseAll}
                    className="px-3 py-1 text-xs bg-[#333] hover:bg-[#444] rounded transition"
                >
                    Collapse All
                </button>
            </div>

            {/* Tree */}
            <div className="font-mono text-sm">
                <TreeNode
                    node={tree}
                    path="root"
                    name="📦 Project Root"
                    expandedFolders={expandedFolders}
                    toggleFolder={toggleFolder}
                    depth={0}
                />
            </div>
        </div>
    );
}

// Build nested tree structure from flat file paths
function buildTree(files) {
    const root = { type: 'folder', children: {} };

    files.forEach(file => {
        const parts = file.filePath.split('/').filter(p => p);
        let current = root;

        parts.forEach((part, i) => {
            const isFile = i === parts.length - 1;

            if (!current.children[part]) {
                current.children[part] = {
                    type: isFile ? 'file' : 'folder',
                    children: {},
                    extension: isFile ? getExtension(part) : null,
                    funcCount: isFile ? (file.listOfFunctions?.length || 0) : 0
                };
            }

            current = current.children[part];
        });
    });

    return root;
}

function getExtension(filename) {
    const parts = filename.split('.');
    return parts.length > 1 ? parts.pop() : null;
}

function getFileIcon(extension) {
    const icons = {
        py: '🐍', js: '📜', jsx: '⚛️', ts: '📘', tsx: '⚛️',
        java: '☕', cpp: '⚙️', h: '📄', hpp: '📄', rs: '🦀',
        json: '📋', md: '📝', html: '🌐', css: '🎨', sql: '🗃️'
    };
    return icons[extension] || '📄';
}

function getFileColor(extension) {
    const colors = {
        py: '#3776AB', js: '#F7DF1E', jsx: '#61DAFB', ts: '#3178C6', tsx: '#61DAFB',
        java: '#ED8B00', cpp: '#00599C', rs: '#DEA584', json: '#888', md: '#fff'
    };
    return colors[extension] || '#ccc';
}

function countFiles(node) {
    if (node.type === 'file') return 1;
    return Object.values(node.children).reduce((sum, child) => sum + countFiles(child), 0);
}

function countFunctions(node) {
    if (node.type === 'file') return node.funcCount || 0;
    return Object.values(node.children).reduce((sum, child) => sum + countFunctions(child), 0);
}

function TreeNode({ node, path, name, expandedFolders, toggleFolder, depth }) {
    const isExpanded = expandedFolders.has(path);
    const children = Object.entries(node.children).sort(([, a], [, b]) => {
        if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
        return 0;
    });

    // File node
    if (node.type === 'file') {
        return (
            <div
                className="flex items-center gap-2 py-1.5 px-2 hover:bg-[#252525] rounded transition-colors cursor-default"
                style={{ paddingLeft: `${depth * 20 + 8}px` }}
            >
                <span>{getFileIcon(node.extension)}</span>
                <span style={{ color: getFileColor(node.extension) }}>{name}</span>
                {node.funcCount > 0 && (
                    <span className="text-xs text-gray-500 ml-auto bg-[#333] px-2 py-0.5 rounded">
                        {node.funcCount} fn
                    </span>
                )}
            </div>
        );
    }

    // Folder node
    const fileCount = countFiles(node);
    const funcCount = countFunctions(node);

    return (
        <div>
            <div
                className="flex items-center gap-2 py-1.5 px-2 hover:bg-[#252525] rounded cursor-pointer transition-colors"
                style={{ paddingLeft: `${depth * 20 + 8}px` }}
                onClick={() => toggleFolder(path)}
            >
                <span className="text-[#4FB3FF] text-lg">{isExpanded ? '📂' : '📁'}</span>
                <span className="text-[#00E0B8] font-semibold">{name}</span>
                <span className="text-xs text-gray-500 ml-auto">
                    {fileCount} file{fileCount !== 1 ? 's' : ''}, {funcCount} fn
                </span>
                <span className="text-gray-500">{isExpanded ? '▼' : '▶'}</span>
            </div>

            {isExpanded && children.length > 0 && (
                <div className="border-l border-[#333] ml-4">
                    {children.map(([childName, child]) => (
                        <TreeNode
                            key={childName}
                            node={child}
                            path={`${path}/${childName}`}
                            name={childName}
                            expandedFolders={expandedFolders}
                            toggleFolder={toggleFolder}
                            depth={depth + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
