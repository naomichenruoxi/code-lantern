# backend/services/rate_limiter.py
"""
Per-User Rate Limiting for AI Features
Limits function detail requests per project session
"""

import time
from typing import Dict, Tuple, Optional
from collections import defaultdict


class RateLimiter:
    """
    Rate limiter that tracks AI usage per session/project.
    Limits: 
    - Max function details per project: 5 (configurable)
    - Max project summaries per hour: 10 (configurable)
    """
    
    def __init__(
        self,
        max_function_details_per_project: int = 5,
        max_summaries_per_hour: int = 10,
    ):
        self.max_function_details = max_function_details_per_project
        self.max_summaries_per_hour = max_summaries_per_hour
        
        # Track usage: {(ip, repo_id): count}
        self._function_detail_usage: Dict[Tuple[str, str], int] = defaultdict(int)
        
        # Track summaries: {ip: [(timestamp, repo_id), ...]}
        self._summary_usage: Dict[str, list] = defaultdict(list)
        
        # Cache to avoid repeated AI calls for same function
        self._function_cache: Dict[str, dict] = {}
    
    def check_function_detail_limit(self, client_ip: str, repo_id: str) -> Tuple[bool, int, int]:
        """
        Check if user can request more function details.
        Returns: (allowed, current_count, max_allowed)
        """
        key = (client_ip, repo_id)
        current = self._function_detail_usage[key]
        allowed = current < self.max_function_details
        return (allowed, current, self.max_function_details)
    
    def record_function_detail(self, client_ip: str, repo_id: str):
        """Record a function detail request"""
        key = (client_ip, repo_id)
        self._function_detail_usage[key] += 1
    
    def get_function_detail_usage(self, client_ip: str, repo_id: str) -> Tuple[int, int]:
        """Get current usage for function details"""
        key = (client_ip, repo_id)
        return (self._function_detail_usage[key], self.max_function_details)
    
    def check_summary_limit(self, client_ip: str) -> Tuple[bool, int, int]:
        """
        Check if user can request more project summaries.
        Returns: (allowed, current_count, max_allowed)
        """
        # Clean old entries (older than 1 hour)
        now = time.time()
        hour_ago = now - 3600
        self._summary_usage[client_ip] = [
            entry for entry in self._summary_usage[client_ip]
            if entry[0] > hour_ago
        ]
        
        current = len(self._summary_usage[client_ip])
        allowed = current < self.max_summaries_per_hour
        return (allowed, current, self.max_summaries_per_hour)
    
    def record_summary(self, client_ip: str, repo_id: str):
        """Record a summary request"""
        self._summary_usage[client_ip].append((time.time(), repo_id))
    
    def get_cached_function(self, repo_id: str, file_path: str, function_name: str) -> Optional[dict]:
        """Get cached function detail if available"""
        cache_key = f"{repo_id}:{file_path}:{function_name}"
        return self._function_cache.get(cache_key)
    
    def cache_function(self, repo_id: str, file_path: str, function_name: str, data: dict):
        """Cache function detail to avoid repeated AI calls"""
        cache_key = f"{repo_id}:{file_path}:{function_name}"
        self._function_cache[cache_key] = data
    
    def reset_project_limits(self, client_ip: str, repo_id: str):
        """Reset limits for a specific project (when user uploads new project)"""
        key = (client_ip, repo_id)
        if key in self._function_detail_usage:
            del self._function_detail_usage[key]
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        return {
            "active_function_sessions": len(self._function_detail_usage),
            "active_summary_sessions": len(self._summary_usage),
            "cached_functions": len(self._function_cache),
        }


# Global rate limiter instance
rate_limiter = RateLimiter(
    max_function_details_per_project=5,
    max_summaries_per_hour=10,
)
