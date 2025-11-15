"""
Break point timeline chart visualization.

This module provides functions to create timeline charts showing break points faced
and break points saved over time for a player.
"""

# Third-party imports
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Local application imports
from .serve_stats import calculate_match_serve_stats
from utils.timeline_chart_utils import add_scatter_trace, add_trend_line, add_vertical_lines, get_match_hover_data


# ============================================================================
# Function Definitions
# ============================================================================


def add_opponent_comparison_traces(fig, x_positions, df, opponent_name=None, hoverdata=None):
    """
    Add opponent comparison traces to break point timeline chart.
    
    Adds opponent break point stats when they were serving.
    
    Args:
        fig: Plotly figure object
        x_positions: List of x-axis positions
        df: DataFrame with match data (needs is_winner column and w_bpFaced, l_bpFaced, w_bpSaved, l_bpSaved)
        opponent_name: Name of opponent for legend
        hoverdata: Hover data for tooltips
    """
    if 'is_winner' not in df.columns:
        return
    
    # Calculate opponent break points when serving
    # If player was winner, opponent was loser (use l_* columns)
    # If player was loser, opponent was winner (use w_* columns)
    opponent_bpFaced = np.where(~df['is_winner'], df['w_bpFaced'], df['l_bpFaced'])
    opponent_bpSaved = np.where(~df['is_winner'], df['w_bpSaved'], df['l_bpSaved'])
    
    opponent_label = f"{opponent_name}" if opponent_name else "Opponent"
    
    # Add opponent scatter traces with lighter colors
    add_scatter_trace(fig, x_positions, opponent_bpFaced, 
                     'Opponent BPs Faced', 
                     '#FCA5A5', 'Opponent Break Points Faced', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=False)  # light red
    add_scatter_trace(fig, x_positions, opponent_bpSaved, 
                     'Opponent BPs Saved', 
                     '#86EFAC', 'Opponent Break Points Saved', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=False)  # light green
    
    # Add opponent trend lines with lighter colors
    add_trend_line(fig, pd.Series(opponent_bpFaced), 'Opponent BPs Faced', '#FCA5A5', secondary_y=False)
    add_trend_line(fig, pd.Series(opponent_bpSaved), 'Opponent BPs Saved', '#86EFAC', secondary_y=False)


def create_break_point_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create break point timeline chart showing break points faced, saved, and save percentage.
    
    Args:
        player_df: DataFrame with match data (should have w_bpFaced, l_bpFaced, w_bpSaved, l_bpSaved columns)
        player_name: Name of the player
        title: Chart title
        show_opponent_comparison: If True, show opponent stats overlay (default: False)
        opponent_name: Name of opponent for comparison (optional, for legend)
        
    Returns:
        go.Figure: Plotly figure object for timeline chart
    """
    # Calculate serve statistics (includes break point stats)
    df = calculate_match_serve_stats(player_df)
    
    # Sort by date and match number for chronological timeline display
    if 'tourney_date' in df.columns and 'match_num' in df.columns:
        df = df.sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
    # Get hover data for tooltips
    hoverdata = get_match_hover_data(df, player_name, case_sensitive=True)
    
    x_positions = list(range(len(df)))
    
    # Create figure (no secondary y-axis needed since we're not showing percentage)
    fig = go.Figure()
    
    # Collect all series for y-axis range calculation and vertical lines
    all_series = []
    
    # Add elements in order: background first, then main data, then overlays
    # 1. Prepare series list for vertical lines
    series_for_lines = [df['player_bpFaced'], df['player_bpSaved']]
    
    # 2. Add scatter plots (main data layer) - Player stats (markers only, no lines)
    # Break Points Faced (count)
    add_scatter_trace(fig, x_positions, df['player_bpFaced'], 
                     'BPs Faced', 
                     '#EF4444', 'Break Points Faced', hoverdata, use_lines=False, secondary_y=False, is_percentage=False)  # red-500
    
    # Break Points Saved (count)
    add_scatter_trace(fig, x_positions, df['player_bpSaved'], 
                     'BPs Saved', 
                     '#10B981', 'Break Points Saved', hoverdata, use_lines=False, secondary_y=False, is_percentage=False)  # green-500
    
    # Note: Break Point Save % is calculated but not displayed on the chart
    
    all_series.extend([df['player_bpFaced'], df['player_bpSaved']])
    
    # 3. Draw vertical lines (background layer) - after we know all series
    add_vertical_lines(fig, series_for_lines)
    
    # 4. Add trend lines (overlay layer) - Player trends
    add_trend_line(fig, df['player_bpFaced'], 'BPs Faced', '#EF4444', secondary_y=False)
    add_trend_line(fig, df['player_bpSaved'], 'BPs Saved', '#10B981', secondary_y=False)
    
    # 5. Add opponent comparison traces if enabled
    if show_opponent_comparison:
        add_opponent_comparison_traces(fig, x_positions, df, opponent_name, hoverdata)
        # Calculate opponent stats for y-axis range
        if 'is_winner' in df.columns:
            opponent_bpFaced = np.where(~df['is_winner'], df['w_bpFaced'], df['l_bpFaced'])
            opponent_bpSaved = np.where(~df['is_winner'], df['w_bpSaved'], df['l_bpSaved'])
            all_series.extend([pd.Series(opponent_bpFaced), pd.Series(opponent_bpSaved)])
    
    # Calculate appropriate y-axis range for counts
    max_values = []
    for series in all_series:
        if series is not None and len(series) > 0:
            max_val = series.max()
            if not np.isnan(max_val):
                max_values.append(max_val)
    
    if max_values:
        max_value = max(max_values)
        # Add 15% padding
        y_max_count = max_value * 1.15
    else:
        y_max_count = 10  # Default to 10 if no valid data
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Matches",
        yaxis_title="Break Points (Count)",
        yaxis=dict(range=[0, y_max_count]),
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        width=1200,
        height=600
    )
    
    return fig

