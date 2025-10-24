"""
Tennis Utility Functions and Performance Monitoring
Contains utility functions and performance monitoring classes.
"""

import pandas as pd

def standardize_tourney_level(level, tour=None, era=None):
    """
    Replace old tourney levels with new standardized levels.
    
    Args:
        level: The original tourney_level value
        tour: The tour (ATP or WTA) for context
        era: The era for historical context (optional)
    
    Returns:
        Standardized tourney_level value
    """
    if pd.isna(level) or level == '':
        return level
    
    level_str = str(level).strip()
    
    # Special case: WTA D level → BJK_Cup
    if level_str == 'D' and tour == 'WTA':
        return 'BJK_Cup'
    
    # Import here to avoid circular imports
    from .tennis_mappings import TOURNEY_LEVEL_MAPPINGS
    
    # Direct mapping
    if level_str in TOURNEY_LEVEL_MAPPINGS:
        return TOURNEY_LEVEL_MAPPINGS[level_str]
    
    # Handle unknown levels
    print(f"Warning: Unknown tourney_level '{level_str}' for tour '{tour}'")
    return level_str  # Keep as-is if unknown

class PerformanceMonitor:
    """Lightweight performance monitoring for tennis tools."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics = {
            "tool_calls": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "total_queries": 0
        }
    
    def track_tool_call(self, tool_name: str, execution_time: float):
        """Track tool call performance."""
        if tool_name not in self.metrics["tool_calls"]:
            self.metrics["tool_calls"][tool_name] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0
            }
        
        self.metrics["tool_calls"][tool_name]["count"] += 1
        self.metrics["tool_calls"][tool_name]["total_time"] += execution_time
        self.metrics["tool_calls"][tool_name]["avg_time"] = (
            self.metrics["tool_calls"][tool_name]["total_time"] / 
            self.metrics["tool_calls"][tool_name]["count"]
        )
    
    def get_performance_summary(self):
        """Get performance summary."""
        return {
            "total_tool_calls": sum(tool["count"] for tool in self.metrics["tool_calls"].values()),
            "cache_hit_rate": self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0,
            "tool_performance": self.metrics["tool_calls"]
        }

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'standardize_tourney_level',
    'PerformanceMonitor'
]
