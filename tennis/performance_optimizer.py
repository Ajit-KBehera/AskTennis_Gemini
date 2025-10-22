"""
Performance optimization utilities for tennis AI system.
Monitors and optimizes system performance.
"""

import time
from typing import Dict, Any, List, Optional
from functools import wraps
from datetime import datetime
import json


class PerformanceMonitor:
    """
    Performance monitoring and optimization utilities.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics = {
            "tool_calls": {},
            "query_times": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "duplicate_calls": 0,
            "total_queries": 0
        }
    
    def track_tool_call(self, tool_name: str, execution_time: float, is_duplicate: bool = False):
        """
        Track tool call performance.
        
        Args:
            tool_name: Name of the tool called
            execution_time: Time taken to execute
            is_duplicate: Whether this was a duplicate call
        """
        if tool_name not in self.metrics["tool_calls"]:
            self.metrics["tool_calls"][tool_name] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "duplicates": 0
            }
        
        self.metrics["tool_calls"][tool_name]["count"] += 1
        self.metrics["tool_calls"][tool_name]["total_time"] += execution_time
        self.metrics["tool_calls"][tool_name]["avg_time"] = (
            self.metrics["tool_calls"][tool_name]["total_time"] / 
            self.metrics["tool_calls"][tool_name]["count"]
        )
        
        if is_duplicate:
            self.metrics["tool_calls"][tool_name]["duplicates"] += 1
            self.metrics["duplicate_calls"] += 1
    
    def track_query_performance(self, query: str, execution_time: float, result_count: int):
        """
        Track database query performance.
        
        Args:
            query: SQL query executed
            execution_time: Time taken to execute
            result_count: Number of results returned
        """
        query_hash = hash(query)
        if query_hash not in self.metrics["query_times"]:
            self.metrics["query_times"][query_hash] = {
                "query": query,
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "result_count": result_count
            }
        
        self.metrics["query_times"][query_hash]["count"] += 1
        self.metrics["query_times"][query_hash]["total_time"] += execution_time
        self.metrics["query_times"][query_hash]["avg_time"] = (
            self.metrics["query_times"][query_hash]["total_time"] / 
            self.metrics["query_times"][query_hash]["count"]
        )
        
        self.metrics["total_queries"] += 1
    
    def track_cache_performance(self, hit: bool):
        """
        Track cache performance.
        
        Args:
            hit: Whether it was a cache hit
        """
        if hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary.
        
        Returns:
            Performance metrics summary
        """
        total_calls = sum(tool["count"] for tool in self.metrics["tool_calls"].values())
        total_time = sum(tool["total_time"] for tool in self.metrics["tool_calls"].values())
        
        cache_hit_rate = (
            self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
            if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
        )
        
        return {
            "total_tool_calls": total_calls,
            "total_execution_time": total_time,
            "average_tool_time": total_time / total_calls if total_calls > 0 else 0,
            "duplicate_calls": self.metrics["duplicate_calls"],
            "duplicate_rate": self.metrics["duplicate_calls"] / total_calls if total_calls > 0 else 0,
            "cache_hit_rate": cache_hit_rate,
            "total_queries": self.metrics["total_queries"],
            "tool_breakdown": self.metrics["tool_calls"],
            "slow_queries": self._get_slow_queries()
        }
    
    def _get_slow_queries(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """
        Get queries that are slower than threshold.
        
        Args:
            threshold: Time threshold in seconds
            
        Returns:
            List of slow queries
        """
        slow_queries = []
        for query_hash, data in self.metrics["query_times"].items():
            if data["avg_time"] > threshold:
                slow_queries.append({
                    "query": data["query"],
                    "avg_time": data["avg_time"],
                    "count": data["count"],
                    "result_count": data["result_count"]
                })
        
        return sorted(slow_queries, key=lambda x: x["avg_time"], reverse=True)
    
    def get_optimization_recommendations(self) -> List[str]:
        """
        Get optimization recommendations based on performance data.
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Check for duplicate calls
        if self.metrics["duplicate_calls"] > 0:
            recommendations.append(
                f"Found {self.metrics['duplicate_calls']} duplicate tool calls. "
                "Consider implementing better caching or tool call deduplication."
            )
        
        # Check for slow queries
        slow_queries = self._get_slow_queries(0.5)  # 500ms threshold
        if slow_queries:
            recommendations.append(
                f"Found {len(slow_queries)} slow queries. "
                "Consider optimizing database queries or adding indexes."
            )
        
        # Check cache performance
        total_cache_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total_cache_requests > 0:
            cache_hit_rate = self.metrics["cache_hits"] / total_cache_requests
            if cache_hit_rate < 0.5:
                recommendations.append(
                    f"Low cache hit rate ({cache_hit_rate:.2%}). "
                    "Consider improving cache strategy or increasing cache size."
                )
        
        return recommendations


class PerformanceOptimizer:
    """
    Performance optimization utilities.
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.monitor = PerformanceMonitor()
        self.call_history = []
        self.duplicate_threshold = 0.1  # 100ms threshold for duplicate detection
    
    def detect_duplicate_calls(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """
        Detect if a tool call is a duplicate.
        
        Args:
            tool_name: Name of the tool
            tool_input: Input parameters
            
        Returns:
            True if this is a duplicate call
        """
        current_time = time.time()
        call_signature = f"{tool_name}:{json.dumps(tool_input, sort_keys=True)}"
        
        # Check recent calls for duplicates
        for call in self.call_history:
            if (call["signature"] == call_signature and 
                current_time - call["timestamp"] < self.duplicate_threshold):
                return True
        
        # Add to history
        self.call_history.append({
            "signature": call_signature,
            "timestamp": current_time,
            "tool_name": tool_name,
            "tool_input": tool_input
        })
        
        # Clean old history (keep last 100 calls)
        if len(self.call_history) > 100:
            self.call_history = self.call_history[-100:]
        
        return False
    
    def optimize_query(self, query: str) -> str:
        """
        Optimize a SQL query for better performance.
        
        Args:
            query: Original SQL query
            
        Returns:
            Optimized SQL query
        """
        # Add basic optimizations
        optimized_query = query
        
        # Add LIMIT if not present and query might return many results
        if "LIMIT" not in query.upper() and "COUNT" not in query.upper():
            if "SELECT" in query.upper() and "FROM" in query.upper():
                # Add LIMIT 100 for safety
                optimized_query = query.rstrip() + " LIMIT 100"
        
        # Add ORDER BY for consistent results
        if "ORDER BY" not in query.upper() and "GROUP BY" not in query.upper():
            if "SELECT" in query.upper() and "FROM" in query.upper():
                # Add basic ordering
                optimized_query = query.rstrip() + " ORDER BY event_year DESC, event_date DESC"
        
        return optimized_query
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report.
        
        Returns:
            Performance report with metrics and recommendations
        """
        summary = self.monitor.get_performance_summary()
        recommendations = self.monitor.get_optimization_recommendations()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "recommendations": recommendations,
            "optimization_score": self._calculate_optimization_score(summary)
        }
    
    def _calculate_optimization_score(self, summary: Dict[str, Any]) -> float:
        """
        Calculate optimization score (0-100).
        
        Args:
            summary: Performance summary
            
        Returns:
            Optimization score
        """
        score = 100.0
        
        # Penalize duplicate calls
        if summary["duplicate_rate"] > 0:
            score -= summary["duplicate_rate"] * 50
        
        # Penalize slow queries
        if summary["average_tool_time"] > 1.0:
            score -= (summary["average_tool_time"] - 1.0) * 20
        
        # Reward cache hits
        if summary["cache_hit_rate"] > 0.8:
            score += 10
        
        return max(0, min(100, score))


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
performance_optimizer = PerformanceOptimizer()


def performance_tracker(tool_name: str):
    """
    Decorator to track tool performance.
    
    Args:
        tool_name: Name of the tool being tracked
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Check for duplicates
            is_duplicate = performance_optimizer.detect_duplicate_calls(
                tool_name, 
                {"args": args, "kwargs": kwargs}
            )
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Track performance
                performance_monitor.track_tool_call(
                    tool_name, 
                    execution_time, 
                    is_duplicate
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.track_tool_call(
                    tool_name, 
                    execution_time, 
                    is_duplicate
                )
                raise e
        
        return wrapper
    return decorator
