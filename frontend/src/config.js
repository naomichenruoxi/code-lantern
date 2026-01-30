// Global configuration

// In production (Vercel), set VITE_API_URL environment variable
// In development, this falls back to localhost
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
