// src/services/github.js
// GitHub OAuth and repository integration

import { API_BASE_URL } from "../config";

const API_BASE = `${API_BASE_URL}/api`;

// Get or set the GitHub session ID from localStorage
export function getGitHubSession() {
    return localStorage.getItem("github_session");
}

export function setGitHubSession(sessionId) {
    localStorage.setItem("github_session", sessionId);
}

export function clearGitHubSession() {
    localStorage.removeItem("github_session");
}

// Check URL params for session ID (from OAuth callback)
// Returns { sessionId, shouldSwitchToGitHubTab }
export function checkOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get("github_session");
    const tab = urlParams.get("tab");

    if (sessionId) {
        setGitHubSession(sessionId);
    }

    // Clean URL if we have any OAuth-related params
    if (sessionId || tab) {
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    return {
        sessionId: sessionId || null,
        shouldSwitchToGitHubTab: tab === "github" || !!sessionId
    };
}

// Initiate GitHub OAuth flow
export async function connectGitHub() {
    // Include tab=github in redirect so we return to the GitHub tab
    const redirectUrl = `${window.location.origin}?tab=github`;
    const response = await fetch(`${API_BASE}/github/connect?frontend_redirect=${encodeURIComponent(redirectUrl)}`);
    const data = await response.json();

    if (data.auth_url) {
        // Redirect to GitHub OAuth
        window.location.href = data.auth_url;
    } else {
        throw new Error("Failed to get GitHub OAuth URL");
    }
}

// Check GitHub connection status
export async function getGitHubStatus() {
    const sessionId = getGitHubSession();
    if (!sessionId) {
        return { connected: false };
    }

    const response = await fetch(`${API_BASE}/github/status?session_id=${sessionId}`);
    const data = await response.json();

    if (!data.connected) {
        clearGitHubSession();
    }

    return data;
}

// List user's repositories
export async function listRepositories() {
    const sessionId = getGitHubSession();
    if (!sessionId) {
        throw new Error("Not connected to GitHub");
    }

    const response = await fetch(`${API_BASE}/github/repos?session_id=${sessionId}`);

    if (response.status === 401) {
        clearGitHubSession();
        throw new Error("GitHub session expired. Please reconnect.");
    }

    if (!response.ok) {
        throw new Error("Failed to fetch repositories");
    }

    return await response.json();
}

// Clone a repository for analysis
export async function cloneRepository(owner, repo, branch = null) {
    const sessionId = getGitHubSession();
    if (!sessionId) {
        throw new Error("Not connected to GitHub");
    }

    let url = `${API_BASE}/github/clone/${owner}/${repo}?session_id=${sessionId}`;
    if (branch) {
        url += `&branch=${encodeURIComponent(branch)}`;
    }

    const response = await fetch(url, { method: "POST" });

    if (response.status === 401) {
        clearGitHubSession();
        throw new Error("GitHub session expired. Please reconnect.");
    }

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to clone repository");
    }

    return await response.json();
}

// Disconnect GitHub
export async function disconnectGitHub() {
    const sessionId = getGitHubSession();
    if (sessionId) {
        try {
            await fetch(`${API_BASE}/github/disconnect?session_id=${sessionId}`, { method: "POST" });
        } catch (e) {
            // Ignore errors on disconnect
        }
        clearGitHubSession();
    }
}
