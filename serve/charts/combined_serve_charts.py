"""
Combined serve charts display.

This script combines multiple serve charts (timeline and radar) into a single
display page, showing them one under another for comprehensive analysis.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add parent directories to path to import shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from serve_stats import (
    calculate_match_serve_stats, 
    calculate_aggregated_serve_stats,
    get_match_hover_data
)
from serveCharts import load_player_matches
from utils.chart_utils import display_chart

# Import chart creation functions from individual chart files
sys.path.insert(0, os.path.dirname(__file__))
from first_serve_timeline import create_timeline_chart
from serve_radar_chart import create_radar_chart


def create_combined_serve_charts(player_name, year, df=None):
    """
    Create combined serve charts (timeline and radar) for a player.
    
    Args:
        player_name: Name of the player
        year: Year of the season
        df: Optional pre-loaded DataFrame. If None, data will be loaded from database.
        
    Returns:
        go.Figure: Combined Plotly figure with both charts
    """
    # Load match data if not provided
    if df is None:
        df = load_player_matches(player_name, year)
    else:
        # Filter DataFrame by year if provided DataFrame contains multiple years
        if 'event_year' in df.columns:
            df = df[df['event_year'] == year].copy()
            if df.empty:
                raise ValueError(f"No matches found for {player_name} in {year}")
    
    # Sort by date and match number
    if 'tourney_date' in df.columns and 'match_num' in df.columns:
        df = df.sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
    # Calculate serve statistics
    player = calculate_match_serve_stats(df, player_name, case_sensitive=True)
    playerdata = get_match_hover_data(df, player_name, case_sensitive=True)
    serve_stats = calculate_aggregated_serve_stats(df, player_name, case_sensitive=False)
    
    # Create x-axis positions for timeline
    x_positions = list(range(len(player)))
    
    # Create individual charts using reusable functions
    timeline_fig = create_timeline_chart(player, player_name, year, playerdata, x_positions)
    radar_fig = create_radar_chart(serve_stats, player_name, year)
    
    # Create subplot figure with 2 rows, 1 column
    combined_fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            f"{player_name} - First Serve Performance Timeline - {year} Season",
            f"{player_name} - Serve Statistics Radar Chart - {year} Season"
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
    combined_fig.update_yaxes(title_text="(%)", row=1, col=1)
    
    # Update polar layout for radar subplot (row 2)
    # Note: polar2 refers to the second polar subplot (row 2, col 1)
    combined_fig.update_layout(
        polar2=dict(
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
        template='plotly_white',
        showlegend=True,
        height=1400,
        width=1200
    )
    
    return combined_fig


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    # Example player name
    player_name = 'Iga Swiatek'
    year = 2024
    
    # Create combined charts
    fig = create_combined_serve_charts(player_name, year)
    
    # Display combined charts
    display_chart(fig, html_filename='combined_serve_charts.html')

