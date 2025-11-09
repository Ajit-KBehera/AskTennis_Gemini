"""
Serve charts creation and display.

This script creates timeline and radar charts for serve statistics analysis.
Charts are returned separately for flexible display in the UI.
"""

# Local application imports
from .serve_stats import (
    calculate_aggregated_serve_stats,
    calculate_match_serve_stats
)
from .first_serve_timeline import create_timeline_chart
from .serve_radar_chart import create_radar_chart


def create_combined_serve_charts(player_name, df, timeline_title, radar_title):
    """
    Create serve charts (timeline and radar) for a player.
    
    Args:
        player_name: Name of the player
        df: DataFrame containing match data (required). Should already be filtered by player,
            year, opponent, tournament, and surfaces.
        timeline_title: Title for the timeline chart
        radar_title: Title for the radar chart
        
    Returns:
        tuple: (timeline_fig, radar_fig) - Two Plotly figures ready for display
    """
    # Calculate serve statistics
    matches_with_stats = calculate_match_serve_stats(df, player_name, case_sensitive=True)
    serve_stats = calculate_aggregated_serve_stats(matches_with_stats)
    
    # Create individual charts with titles and layout configured
    timeline_fig = create_timeline_chart(matches_with_stats, player_name, title=timeline_title)
    radar_fig = create_radar_chart(serve_stats, player_name, title=radar_title)
    
    return timeline_fig, radar_fig

