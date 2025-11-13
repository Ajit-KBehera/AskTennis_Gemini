"""
Return points won percentage timeline chart visualization.

This module provides functions to create timeline charts showing return points won
percentage over time, tracking return performance progression.
"""

# Third-party imports
import numpy as np
import plotly.graph_objects as go

# Local application imports
from .return_stats import get_match_hover_data


# ============================================================================
# Function Definitions
# ============================================================================

def add_scatter_trace(fig, x_positions, y_data, name, color, hover_label, customdata):
    """Add a scatter plot trace to the figure"""
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_data,
        mode='markers',
        name=name,
        marker=dict(color=color, size=8),
        hovertemplate=f'{hover_label}: %{{y:.2f}}%<br>' +                  
                      'Year: %{customdata[4]}<br>' +
                      'Tournament: %{customdata[0]}<br>' +
                      'Round: %{customdata[1]}<br>' +
                      'Opponent: %{customdata[2]}<br>' +
                      'Result: %{customdata[3]}<extra></extra>',
        customdata=customdata
    ))


def add_trend_line(fig, y_data, name, color):
    """Add a linear trend line to the figure"""
    mask = y_data.notna()
    x = np.arange(len(y_data))[mask]
    y = y_data.loc[mask].values
    
    if len(x) >= 2:
        xc = x - x.mean()
        z = np.polyfit(xc, y, 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=x,
            y=p(xc),
            mode='lines',
            name=f'{name}',
            line=dict(color=color, dash='dash', width=2),
            opacity=0.8,
            hoverinfo='skip'
        ))


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


def _add_opponent_comparison_traces(fig, x_positions, df, opponent_name=None, hoverdata=None):
    """
    Add opponent comparison traces to timeline chart.
    
    Reserved for future use - adds opponent scatter plots and trend lines.
    Currently not used in timeline chart to avoid clutter.
    
    Args:
        fig: Plotly figure object
        x_positions: List of x-axis positions
        df: DataFrame with opponent stats columns
        opponent_name: Name of opponent for legend
        hoverdata: Hover data for tooltips
    """
    if 'opponent_return_points_won_pct' not in df.columns:
        return
    
    opponent_label = f"{opponent_name}" if opponent_name else "Opponent"
    
    # Add opponent scatter trace
    add_scatter_trace(fig, x_positions, df['opponent_return_points_won_pct'], 
                     f'{opponent_label} Return Points Won %', '#DC2626', 
                     'Opponent Return Points Won %', hoverdata)  # red
    
    # Add opponent trend line
    add_trend_line(fig, df['opponent_return_points_won_pct'], 
                  f'{opponent_label} Return Points Won %', '#DC2626')


def create_return_points_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create the return points won percentage timeline chart with optional opponent comparison.
    
    Args:
        player_df: DataFrame with calculated return statistics
        player_name: Name of the player
        title: Chart title
        show_opponent_comparison: If True, show opponent stats overlay (default: False)
        opponent_name: Name of opponent for comparison (optional, for legend)
        
    Returns:
        go.Figure: Plotly figure object for timeline chart
    """
    # Sort by date and match number for chronological timeline display
    df = player_df.copy()
    if 'tourney_date' in df.columns and 'match_num' in df.columns:
        df = df.sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
    # Get hover data for tooltips
    hoverdata = get_match_hover_data(df, player_name, case_sensitive=True)
    
    x_positions = list(range(len(df)))
    
    fig = go.Figure()
    
    # Add elements in order: background first, then main data, then overlays
    # 1. Draw vertical lines (background layer)
    add_vertical_lines(fig, [df['player_return_points_won_pct']])
    
    # 2. Add scatter plots (main data layer) - Player stats
    player_label = f"{player_name}" if player_name else "Player"
    add_scatter_trace(fig, x_positions, df['player_return_points_won_pct'], 
                     'Return Points Won %', '#2563EB', 'Return Points Won %', hoverdata)  # blue
    
    # 4. Add trend lines (overlay layer) - Player trends
    add_trend_line(fig, df['player_return_points_won_pct'], 'Return Points Won %', '#2563EB')
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Matches",
        yaxis_title="Return Points Won (%)",
        yaxis=dict(range=[0, 100]),
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        width=1200,
        height=600
    )
    
    return fig

