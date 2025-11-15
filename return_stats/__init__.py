"""
Return statistics visualizations and tables.

This module contains return-related analysis:
- charts/: Visualization scripts for return statistics
- tables/: Table generation scripts for return statistics
- return_stats.py: Shared calculation functions for return statistics
"""

from .return_stats import (
    calculate_match_return_stats,
    calculate_aggregated_player_return_stats,
    calculate_aggregated_opponent_return_stats,
    build_year_suffix
)

__all__ = [
    'calculate_match_return_stats',
    'calculate_aggregated_player_return_stats',
    'calculate_aggregated_opponent_return_stats',
    'build_year_suffix'
]

