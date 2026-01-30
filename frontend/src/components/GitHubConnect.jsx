// src/components/GitHubConnect.jsx
// GitHub OAuth connection and repository browser component

import React, { useState, useEffect } from "react";
import {
    connectGitHub,
    getGitHubStatus,
    listRepositories,
    cloneRepository,
    disconnectGitHub,
} from "../services/github";

export default function GitHubConnect({ onAnalyze }) {
    const [status, setStatus] = useState({ connected: false, loading: true });
    const [repos, setRepos] = useState([]);
    const [loadingRepos, setLoadingRepos] = useState(false);
    const [cloning, setCloning] = useState(null);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState("");

    // Check connection status on mount
    useEffect(() => {
        checkConnectionStatus();
    }, []);

    const checkConnectionStatus = async () => {
        try {
            const statusData = await getGitHubStatus();
            setStatus({ ...statusData, loading: false });
            if (statusData.connected) {
                loadRepositories();
            }
        } catch (e) {
            setStatus({ connected: false, loading: false });
        }
    };

    const loadRepositories = async () => {
        setLoadingRepos(true);
        setError(null);
        try {
            const data = await listRepositories();
            setRepos(data.repositories || []);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoadingRepos(false);
        }
    };

    const handleConnect = async () => {
        setError(null);
        try {
            await connectGitHub();
        } catch (e) {
            setError(e.message);
        }
    };

    const handleDisconnect = async () => {
        await disconnectGitHub();
        setStatus({ connected: false, loading: false });
        setRepos([]);
    };

    const handleClone = async (repo) => {
        setCloning(repo.id);
        setError(null);
        try {
            const result = await cloneRepository(repo.owner, repo.name);
            if (onAnalyze) {
                onAnalyze(result.repo_id);
            }
        } catch (e) {
            setError(e.message);
            setCloning(null);
        }
    };

    const filteredRepos = repos.filter(
        (repo) =>
            repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (repo.description || "").toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Loading state
    if (status.loading) {
        return (
            <div className="text-[var(--text-secondary)] font-display text-center py-8">
                <span className="animate-pulse">checking github connection...</span>
            </div>
        );
    }

    // Not connected - show connect button
    if (!status.connected) {
        return (
            <div className="flex flex-col items-center space-y-4">
                <p className="text-[var(--text-secondary)] font-display text-sm text-center">
                    connect your GitHub to analyze repositories
                </p>

                <button
                    onClick={handleConnect}
                    className="w-full py-3 bg-[#24292e] border border-[var(--border-default)] rounded-xl 
                     text-white font-display text-sm
                     hover:bg-[#2f363d] hover:border-[var(--border-hover)] transition-all
                     flex items-center justify-center gap-3"
                >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                    </svg>
                    Connect with GitHub
                </button>

                {error && (
                    <p className="text-[var(--accent-orange)] font-display text-sm">{error}</p>
                )}
            </div>
        );
    }

    // Connected - show repository list
    return (
        <div className="flex flex-col space-y-4 w-full">
            {/* Connection header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    {status.user?.avatar_url && (
                        <img
                            src={status.user.avatar_url}
                            alt="avatar"
                            className="w-6 h-6 rounded-full ring-2 ring-[var(--accent-cyan)]"
                        />
                    )}
                    <span className="text-white font-display text-sm">
                        {status.user?.login || "Connected"}
                    </span>
                    <span className="text-[var(--accent-cyan)] text-xs animate-pulse">●</span>
                </div>
                <button
                    onClick={handleDisconnect}
                    className="text-[var(--text-muted)] font-display text-xs hover:text-white transition"
                >
                    disconnect
                </button>
            </div>

            {/* Search */}
            <input
                type="text"
                placeholder="🔍 search repositories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg 
                   text-white font-display text-sm 
                   focus:outline-none focus:border-[var(--accent-cyan)] transition"
            />

            {/* Error */}
            {error && (
                <p className="text-[var(--accent-orange)] font-display text-sm">{error}</p>
            )}

            {/* Repository list */}
            <div className="max-h-[240px] overflow-y-auto space-y-2">
                {loadingRepos ? (
                    <p className="text-[var(--text-muted)] font-display text-sm text-center py-4 animate-pulse">
                        loading repositories...
                    </p>
                ) : filteredRepos.length === 0 ? (
                    <p className="text-[var(--text-muted)] font-display text-sm text-center py-4">
                        no repositories found
                    </p>
                ) : (
                    filteredRepos.slice(0, 10).map((repo) => (
                        <div
                            key={repo.id}
                            className="p-3 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg 
                         hover:border-[var(--accent-cyan)] transition cursor-pointer group"
                            onClick={() => handleClone(repo)}
                        >
                            <div className="flex justify-between items-center">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <span className="text-white font-display text-sm font-semibold truncate">
                                            {repo.name}
                                        </span>
                                        {repo.private && (
                                            <span className="text-xs text-[var(--accent-yellow)] border border-[var(--accent-yellow)] px-1 rounded">
                                                private
                                            </span>
                                        )}
                                    </div>
                                    {repo.language && (
                                        <span className="text-[var(--text-muted)] font-display text-xs">
                                            {repo.language}
                                        </span>
                                    )}
                                </div>
                                <button
                                    className={`px-3 py-1 rounded-lg font-display text-xs transition ${cloning === repo.id
                                        ? 'bg-[var(--border-default)] text-[var(--text-muted)] cursor-wait'
                                        : 'btn-primary !py-1 !px-3'
                                        }`}
                                    disabled={cloning === repo.id}
                                >
                                    {cloning === repo.id ? "analyzing..." : "analyze →"}
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
