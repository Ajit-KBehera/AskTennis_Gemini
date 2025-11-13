"""
Return charts creation and display.

This script creates timeline and radar charts for return statistics analysis.
Charts are returned separately for flexible display in the UI.
"""

# Local application imports
from .return_stats import (
    build_year_suffix,
    calculate_aggregated_return_stats,
    calculate_aggregated_opponent_return_stats,
    calculate_match_return_stats
)
from .return_points_timeline import create_return_points_timeline_chart
from .break_point_conversion_timeline import create_break_point_conversion_timeline_chart
from .return_radar_chart import create_radar_chart


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


def create_combined_return_charts(player_name, df, year=None, opponent=None, tournament=None, surfaces=None):
    """
    Create return charts (return points timeline, break point conversion timeline, and radar) for a player.
    
    Args:
        player_name: Name of the player
        df: DataFrame containing match data (required). Should already be filtered by player,
            year, opponent, tournament, and surfaces.
        year: Optional year(s) for chart title (int, str, list, or None)
        opponent: Optional opponent name for chart title
        tournament: Optional tournament name for chart title
        surfaces: Optional list of surfaces for chart title
        
    Returns:
        tuple: (return_points_timeline_fig, bp_conversion_timeline_fig, radar_fig) - Three Plotly figures ready for display
    """
    # Build chart titles
    year_suffix, filter_suffix = _build_chart_title_suffixes(year, opponent, tournament, surfaces)
    return_points_title = f"{player_name} - Return Points Won % Timeline - {year_suffix}{filter_suffix}"
    bp_conversion_title = f"{player_name} - Break Point Conversion Timeline - {year_suffix}{filter_suffix}"
    radar_title = f"{player_name} - Return Statistics Radar Chart - {year_suffix}{filter_suffix}"
    
    # Calculate return statistics
    matches_with_stats = calculate_match_return_stats(df, player_name, case_sensitive=True)
    return_stats = calculate_aggregated_return_stats(matches_with_stats)
    
    # Determine if comparison mode should be enabled (specific opponent selected)
    show_comparison = opponent and opponent != "All Opponents"
    opponent_stats = None
    
    if show_comparison:
        # Calculate opponent aggregated stats
        opponent_stats = calculate_aggregated_opponent_return_stats(matches_with_stats, opponent_name=opponent)
        # If opponent stats not available (multiple opponents), disable comparison
        if opponent_stats is None:
            show_comparison = False
    
    # Create individual charts with titles and layout configured
    # Return Points Timeline chart: Opponent comparison disabled (to avoid clutter)
    return_points_timeline_fig = create_return_points_timeline_chart(
        matches_with_stats, 
        player_name, 
        title=return_points_title,
        show_opponent_comparison=False,  # Disabled - to avoid clutter
        opponent_name=None
    )
    
    # Break Point Conversion Timeline chart: Opponent comparison disabled (to avoid clutter)
    # Use matches_with_stats since break point conversion stats are already calculated
    bp_conversion_timeline_fig = create_break_point_conversion_timeline_chart(
        matches_with_stats,
        player_name,
        title=bp_conversion_title,
        show_opponent_comparison=False,  # Disabled - to avoid clutter
        opponent_name=None
    )
    
    # Radar chart: Opponent comparison enabled when specific opponent selected
    radar_fig = create_radar_chart(
        return_stats, 
        player_name, 
        title=radar_title,
        opponent_stats=opponent_stats,
        opponent_name=opponent if show_comparison else None
    )
    
    return return_points_timeline_fig, bp_conversion_timeline_fig, radar_fig

