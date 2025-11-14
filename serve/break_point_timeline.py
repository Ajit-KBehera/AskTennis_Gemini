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
from .serve_stats import get_match_hover_data, calculate_match_serve_stats


# ============================================================================
# Function Definitions
# ============================================================================

def add_scatter_trace(fig, x_positions, y_data, name, color, hover_label, customdata, use_lines=True, secondary_y=False, is_percentage=False):
    """Add a scatter plot trace to the figure with optional lines"""
    mode = 'markers+lines' if use_lines else 'markers'
    
    # Format hover value based on whether it's a percentage or count
    if is_percentage:
        hover_format = f'{hover_label}: %{{y:.2f}}%<br>'
    else:
        hover_format = f'{hover_label}: %{{y:.0f}}<br>'
    
    trace_kwargs = {
        'x': x_positions,
        'y': y_data,
        'mode': mode,
        'name': name,
        'marker': dict(color=color, size=8),
        'hovertemplate': hover_format +                  
                      'Year: %{customdata[4]}<br>' +
                      'Tournament: %{customdata[0]}<br>' +
                      'Round: %{customdata[1]}<br>' +
                      'Opponent: %{customdata[2]}<br>' +
                      'Result: %{customdata[3]}<extra></extra>',
        'customdata': customdata
    }
    
    if use_lines:
        trace_kwargs['line'] = dict(color=color, width=2)
    
    if secondary_y:
        fig.add_trace(go.Scatter(**trace_kwargs), secondary_y=True)
    else:
        fig.add_trace(go.Scatter(**trace_kwargs))


def add_trend_line(fig, y_data, name, color, secondary_y=False):
    """Add a linear trend line to the figure"""
    mask = y_data.notna()
    x = np.arange(len(y_data))[mask]
    y = y_data.loc[mask].values
    
    if len(x) >= 2:
        xc = x - x.mean()
        z = np.polyfit(xc, y, 1)
        p = np.poly1d(z)
        trend_trace = go.Scatter(
            x=x,
            y=p(xc),
            mode='lines',
            name=f'{name}',
            line=dict(color=color, dash='dash', width=2),
            opacity=0.8,
            hoverinfo='skip'
        )
        
        if secondary_y:
            fig.add_trace(trend_trace, secondary_y=True)
        else:
            fig.add_trace(trend_trace)


def add_vertical_lines(fig, y_data_series, y_min=0, y_max=None, color='gray', width=0.8, opacity=0.3):
    """
    Draw vertical lines from y_min to the highest value between the series at each x position.
    
    Args:
        fig (go.Figure): Plotly figure object to add lines to
        y_data_series (list): List of pandas Series containing y-values (e.g., [series1, series2])
        y_min (float): Starting y-value for vertical lines (default: 0)
        y_max (float): Ending y-value for vertical lines. If None, uses max of all series per match (default: None)
        color (str): Line color (default: 'gray')
        width (float): Line width (default: 0.8)
        opacity (float): Line opacity between 0 and 1 (default: 0.3)
    """
    if not y_data_series:
        return
    
    # Find valid indices (where at least one series has valid data)
    valid_mask = np.zeros(len(y_data_series[0]), dtype=bool)
    for series in y_data_series:
        valid_mask |= ~np.isnan(series)
    
    if not np.any(valid_mask):
        return
    
    x_vals = np.arange(len(y_data_series[0]))[valid_mask]
    
    for i in x_vals:
        # Get values from all series at this index
        values = []
        for series in y_data_series:
            val = series.iloc[i] if hasattr(series, 'iloc') else series[i]
            if not np.isnan(val):
                values.append(val)
        
        if values:
            line_max = max(values)
            # Use y_max if provided, otherwise use calculated maximum
            line_end = y_max if y_max is not None else line_max
            
            fig.add_trace(go.Scatter(
                x=[i, i], y=[y_min, line_end],
                mode='lines',
                line=dict(color=color, width=width),
                opacity=opacity,
                showlegend=False,
                hoverinfo='skip'
            ))


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

