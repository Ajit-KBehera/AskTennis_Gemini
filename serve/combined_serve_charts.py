"""
Combined serve charts display.

This script combines multiple serve charts (timeline and radar) into a single
display page, showing them one under another for comprehensive analysis.
"""

# Third-party imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    Create combined serve charts (timeline and radar) for a player.
    
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
        go.Figure: Combined Plotly figure with both charts
    """
    # Sort by date and match number
    if 'tourney_date' in df.columns and 'match_num' in df.columns:
        df = df.sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
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
    
    # Create individual charts using reusable functions
    timeline_fig = create_timeline_chart(matches_with_stats, player_name, year)
    radar_fig = create_radar_chart(serve_stats, player_name, year)
    
    # Create subplot figure with 2 rows, 1 column
    combined_fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            f"{player_name} - First Serve Performance Timeline - {year_suffix}{filter_suffix}",
            f"{player_name} - Serve Statistics Radar Chart - {year_suffix}{filter_suffix}"
        ),
        specs=[[{"type": "xy"}], [{"type": "polar"}]],
        vertical_spacing=0.15
    )
    
    # Add timeline chart traces to first subplot
    for trace in timeline_fig.data:
        combined_fig.add_trace(trace, row=1, col=1)
    
    # Add radar chart trace to second subplot
    for trace in radar_fig.data:
        combined_fig.add_trace(trace, row=2, col=1)
    
    # Update layout for timeline subplot (row 1)
    combined_fig.update_xaxes(title_text="Matches", row=1, col=1)
    combined_fig.update_yaxes(title_text="(%)", range=[0, 100], row=1, col=1)  # Fix y-axis range to 0-100%
    
    # Update polar layout for radar subplot (row 2)
    # Use update_polars() with patch parameter to avoid deprecated keyword arguments
    combined_fig.update_polars(
        patch=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                gridcolor='lightgray',
                gridwidth=1
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                rotation=90,
                direction='counterclockwise'
            )
        ),
        row=2,
        col=1
    )
    
    # Update general layout
    combined_fig.update_layout(
        template='plotly_white',
        showlegend=True,
        height=1400,
        width=1200
    )
    
    return combined_fig

