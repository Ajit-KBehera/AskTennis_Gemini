"""
Serve charts creation and display.

This script creates timeline and radar charts for serve statistics analysis.
Charts are returned separately for flexible display in the UI.
"""

# Local application imports
from .serve_stats import (
    build_year_suffix,
    calculate_aggregated_serve_stats,
    calculate_match_serve_stats
)
from .first_serve_timeline import create_timeline_chart
from .serve_radar_chart import create_radar_chart


def create_combined_serve_charts(player_name, year, df, opponent=None, tournament=None, surfaces=None):
    """
    Create serve charts (timeline and radar) for a player.
    
    Args:
        player_name: Name of the player
        year: Year(s) for the chart. Can be:
            - int or str: Single year (e.g., 2024)
            - list: Multiple years (e.g., [2022, 2023, 2024])
            - None: Career view (all years)
        df: DataFrame containing match data (required). Should already be filtered by player,
            year, opponent, tournament, and surfaces.
        opponent: Optional opponent name (for chart title display)
        tournament: Optional tournament name (for chart title display)
        surfaces: Optional list of surfaces (for chart title display)
        
    Returns:
        tuple: (timeline_fig, radar_fig) - Two Plotly figures ready for display
    """
    # Build filter suffix for chart titles
    filter_parts = []
    if opponent:
        filter_parts.append(f"vs {opponent}")
    if tournament:
        filter_parts.append(f"at {tournament}")
    if surfaces and len(surfaces) > 0:
        filter_parts.append(f"on {', '.join(surfaces)}")
    filter_suffix = f" ({', '.join(filter_parts)})" if filter_parts else ""
    
    # Build year suffix for titles
    year_suffix = build_year_suffix(year)
    
    # Calculate serve statistics
    matches_with_stats = calculate_match_serve_stats(df, player_name, case_sensitive=True)
    serve_stats = calculate_aggregated_serve_stats(matches_with_stats)
    
    # Build chart titles with filter and year suffixes
    timeline_title = f"{player_name} - First Serve Performance Timeline - {year_suffix}{filter_suffix}"
    radar_title = f"{player_name} - Serve Statistics Radar Chart - {year_suffix}{filter_suffix}"
    
    # Create individual charts with titles and layout configured
    timeline_fig = create_timeline_chart(matches_with_stats, player_name, year, title=timeline_title)
    radar_fig = create_radar_chart(serve_stats, player_name, year, title=radar_title)
    
    return timeline_fig, radar_fig

