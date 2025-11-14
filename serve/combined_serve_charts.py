"""
Serve charts creation and display.

This script creates timeline and radar charts for serve statistics analysis.
Charts are returned separately for flexible display in the UI.
"""

# Local application imports
from .serve_stats import (
    build_year_suffix,
    calculate_aggregated_player_serve_stats,
    calculate_aggregated_opponent_serve_stats,
    calculate_match_serve_stats
)
from .first_serve_timeline import create_timeline_chart
from .ace_df_timeline import create_ace_df_timeline_chart
from .break_point_timeline import create_break_point_timeline_chart
from utils.radar_chart_utils import create_radar_chart


def _build_chart_title_suffixes(year, opponent=None, tournament=None, surfaces=None):
    """
    Build filter and year suffixes for chart titles.
    
    Args:
        year: Year(s) for the chart
        opponent: Optional opponent name
        tournament: Optional tournament name
        surfaces: Optional list of surfaces
        
    Returns:
        tuple: (year_suffix, filter_suffix) - Two suffix strings for chart titles
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
    
    return year_suffix, filter_suffix


def create_combined_serve_charts(player_name, df, year=None, opponent=None, tournament=None, surfaces=None):
    """
    Create serve charts (timeline, ace/DF timeline, break point timeline, and radar) for a player.
    
    Args:
        player_name: Name of the player
        df: DataFrame containing match data (required). Should already be filtered by player,
            year, opponent, tournament, and surfaces.
        year: Optional year(s) for chart title (int, str, list, or None)
        opponent: Optional opponent name for chart title
        tournament: Optional tournament name for chart title
        surfaces: Optional list of surfaces for chart title
        
    Returns:
        tuple: (timeline_fig, ace_df_timeline_fig, bp_timeline_fig, radar_fig) - Four Plotly figures ready for display
    """
    # Build chart titles
    year_suffix, filter_suffix = _build_chart_title_suffixes(year, opponent, tournament, surfaces)
    timeline_title = f"{player_name} - First Serve Performance Timeline - {year_suffix}{filter_suffix}"
    ace_df_timeline_title = f"{player_name} - Ace & Double Fault Rate Timeline - {year_suffix}{filter_suffix}"
    bp_timeline_title = f"{player_name} - Break Point Timeline - {year_suffix}{filter_suffix}"
    radar_title = f"{player_name} - Serve Statistics Radar Chart - {year_suffix}{filter_suffix}"
    
    # Calculate serve statistics
    matches_with_stats = calculate_match_serve_stats(df)
    serve_stats = calculate_aggregated_player_serve_stats(matches_with_stats)
    
    # Determine if comparison mode should be enabled (specific opponent selected)
    show_comparison = opponent and opponent != "All Opponents"
    opponent_stats = None
    
    if show_comparison:
        # Calculate opponent aggregated stats
        opponent_stats = calculate_aggregated_opponent_serve_stats(matches_with_stats, opponent_name=opponent)
        # If opponent stats not available (multiple opponents), disable comparison
        if opponent_stats is None:
            show_comparison = False
    
    # Create individual charts with titles and layout configured
    # Timeline chart: Opponent comparison disabled (too many parameters clutter the chart)
    timeline_fig = create_timeline_chart(
        matches_with_stats, 
        player_name, 
        title=timeline_title,
        show_opponent_comparison=False,  # Disabled - too many parameters
        opponent_name=None
    )
    # Ace/DF Timeline chart: Opponent comparison enabled (only 4 series total, manageable)
    ace_df_timeline_fig = create_ace_df_timeline_chart(
        matches_with_stats,
        player_name,
        title=ace_df_timeline_title,
        show_opponent_comparison=False,
        opponent_name=None
    )
    # Break Point Timeline chart: Shows break points faced, saved, and save percentage
    bp_timeline_fig = create_break_point_timeline_chart(
        df,  # Use original df, not matches_with_stats (break point stats calculated inside)
        player_name,
        title=bp_timeline_title,
        show_opponent_comparison=False,
        opponent_name=None
    )
    # Radar chart: Opponent comparison enabled when specific opponent selected
    radar_fig = create_radar_chart(
        serve_stats, 
        player_name, 
        title=radar_title,
        opponent_stats=opponent_stats,
        opponent_name=opponent if show_comparison else None
    )
    
    return timeline_fig, ace_df_timeline_fig, bp_timeline_fig, radar_fig

