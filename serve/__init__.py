"""
Serve statistics visualizations and tables.

This module contains serve-related analysis:
- charts/: Visualization scripts for serve statistics
- tables/: Table generation scripts for serve statistics
- serve_stats.py: Shared calculation functions for serve statistics
"""

from .serve_stats import (
    calculate_match_serve_stats,
    calculate_aggregated_player_serve_stats,
    calculate_aggregated_opponent_serve_stats,
    get_match_hover_data,
    build_year_suffix
)

__all__ = [
    'calculate_match_serve_stats',
    'calculate_aggregated_player_serve_stats',
    'calculate_aggregated_opponent_serve_stats',
    'get_match_hover_data',
    'build_year_suffix'
]


