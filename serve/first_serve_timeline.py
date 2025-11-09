"""
First serve timeline chart visualization.

This module provides functions to create timeline charts showing first serve
performance over time, including first serves in percentage and first serves won percentage.
"""

# Third-party imports
import numpy as np
import plotly.graph_objects as go

# Local application imports
from .serve_stats import get_match_hover_data


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
            name=f'Trend ({name})',
            line=dict(color=color, dash='dash', width=2),
            opacity=0.8,
            hoverinfo='skip'
        ))


def add_vertical_lines(fig, y_data_series, y_min=0, y_max=100, color='gray', width=0.8, opacity=0.3):
    """
    Draw vertical lines from y_min to y_max at each x position.
    
    Args:
        fig (go.Figure): Plotly figure object to add lines to
        y_data_series (list): List of pandas Series containing y-values (e.g., [series1, series2])
        y_min (float): Starting y-value for vertical lines (default: 0)
        y_max (float): Ending y-value for vertical lines (default: 100)
        color (str): Line color (default: 'gray')
        width (float): Line width (default: 0.8)
        opacity (float): Line opacity between 0 and 1 (default: 0.3)
    """
    # Draw vertical lines from y_min to y_max for all valid data points
    valid_indices = ~np.isnan(y_data_series[0])
    
    if np.any(valid_indices):
        x_vals = np.arange(len(y_data_series[0]))[valid_indices]
        for i in x_vals:
            fig.add_trace(go.Scatter(
                x=[i, i], y=[y_min, y_max],
                mode='lines',
                line=dict(color=color, width=width),
                opacity=opacity,
                showlegend=False,
                hoverinfo='skip'
            ))


def create_timeline_chart(player_df, player_name, title):
    """
    Create the first serve timeline chart.
    
    Args:
        player_df: DataFrame with calculated serve statistics
        player_name: Name of the player
        title: Chart title
        
    Returns:
        go.Figure: Plotly figure object for timeline chart
    """
    # Sort by date and match number for chronological timeline display
    df = player_df.copy()
    if 'tourney_date' in df.columns and 'match_num' in df.columns:
        df = df.sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
    # Get hover data for tooltips
    hoverdata = get_match_hover_data(df, player_name, case_sensitive=True)
    
    # Create x-axis positions for matches
    x_positions = list(range(len(df)))
    
    fig = go.Figure()
    
    # Add elements in order: background first, then main data, then overlays
    # 1. Draw vertical lines (background layer)
    add_vertical_lines(fig, [df['player_1stIn'], df['player_1stWon']])
    
    # 2. Add scatter plots (main data layer)
    add_scatter_trace(fig, x_positions, df['player_1stIn'], 'First Serves In (%)', 'blue', 'First Serves In', hoverdata)
    add_scatter_trace(fig, x_positions, df['player_1stWon'], 'First Serves Won (%)', 'orange', 'First Serves Won', hoverdata)
    
    # 3. Add trend lines (overlay layer)
    add_trend_line(fig, df['player_1stIn'], 'First Serves In', 'blue')
    add_trend_line(fig, df['player_1stWon'], 'First Serves Won', 'orange')
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Matches",
        yaxis_title="(%)",
        yaxis=dict(range=[0, 100]),  # Fix y-axis range to 0-100%
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        width=1200,
        height=600
    )
    
    return fig
