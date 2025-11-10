"""
Ace and Double Fault timeline chart visualization.

This module provides functions to create timeline charts showing ace rate
and double fault rate over time for both player and opponent.
"""

# Third-party imports
import numpy as np
import plotly.graph_objects as go

# Local application imports
from .serve_stats import get_match_hover_data


# ============================================================================
# Function Definitions
# ============================================================================

def add_scatter_trace(fig, x_positions, y_data, name, color, hover_label, customdata, use_lines=True):
    """Add a scatter plot trace to the figure with optional lines"""
    mode = 'markers+lines' if use_lines else 'markers'
    
    trace_kwargs = {
        'x': x_positions,
        'y': y_data,
        'mode': mode,
        'name': name,
        'marker': dict(color=color, size=8),
        'hovertemplate': f'{hover_label}: %{{y:.2f}}%<br>' +                  
                      'Tournament: %{customdata[0]}<br>' +
                      'Round: %{customdata[1]}<br>' +
                      'Opponent: %{customdata[2]}<br>' +
                      'Result: %{customdata[3]}<extra></extra>',
        'customdata': customdata
    }
    
    if use_lines:
        trace_kwargs['line'] = dict(color=color, width=2)
    
    fig.add_trace(go.Scatter(**trace_kwargs))


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
            hoverinfo='skip',
            showlegend=False
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
    Add opponent comparison traces to ace/DF timeline chart.
    
    Reserved for future use - adds opponent scatter plots and trend lines.
    Currently not used in timeline chart as opponent comparison is handled inline
    in create_ace_df_timeline_chart, but kept for potential future refactoring.
    
    Args:
        fig: Plotly figure object
        x_positions: List of x-axis positions
        df: DataFrame with opponent stats columns (opponent_ace_rate, opponent_df_rate)
        opponent_name: Name of opponent for legend
        hoverdata: Hover data for tooltips
    """
    if 'opponent_ace_rate' not in df.columns or 'opponent_df_rate' not in df.columns:
        return
    
    opponent_label = f"{opponent_name}" if opponent_name else "Opponent"
    
    # Add opponent scatter traces
    add_scatter_trace(fig, x_positions, df['opponent_ace_rate'], 
                     'Ace Rate', 
                     '#34D399', 'Ace Rate', hoverdata, use_lines=False)  # green-300
    add_scatter_trace(fig, x_positions, df['opponent_df_rate'], 
                     'Double Fault Rate', 
                     '#F87171', 'Double Fault Rate', hoverdata, use_lines=False)  # red-400
    
    # Add opponent trend lines
    add_trend_line(fig, df['opponent_ace_rate'], f'{opponent_label} - Ace Rate', '#34D399')
    add_trend_line(fig, df['opponent_df_rate'], f'{opponent_label} - Double Fault Rate', '#F87171')


def create_ace_df_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create ace rate and double fault rate timeline chart.
    
    Args:
        player_df: DataFrame with calculated serve statistics
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
    
    # Collect all series for y-axis range calculation and vertical lines
    all_series = []
    
    player_label = f"{player_name}" if player_name else "Player"
    
    # Add elements in order: background first, then main data, then overlays
    # 1. Prepare series list for vertical lines
    series_for_lines = [df['player_ace_rate'], df['player_df_rate']]
    
    # 2. Add scatter plots (main data layer) - Player stats
    add_scatter_trace(fig, x_positions, df['player_ace_rate'], 
                     'Ace Rate', 
                     '#10B981',' Ace Rate', hoverdata, use_lines=False)  # green-500
    add_scatter_trace(fig, x_positions, df['player_df_rate'], 
                     'Double Fault Rate', 
                     '#EF4444', 'Double Fault Rate', hoverdata, use_lines=False)  # red-500
    
    all_series.extend([df['player_ace_rate'], df['player_df_rate']])
    
    # 4. Draw vertical lines (background layer) - after we know all series
    add_vertical_lines(fig, series_for_lines)
    
    # 5. Add trend lines (overlay layer) - Player trends
    add_trend_line(fig, df['player_ace_rate'], 'Ace Rate', '#10B981')
    add_trend_line(fig, df['player_df_rate'], 'Double Fault Rate', '#EF4444')
    
    # Calculate appropriate y-axis range (0 to max value + 15% padding, but cap at 30%)
    max_values = []
    for series in all_series:
        if series is not None and len(series) > 0:
            max_val = series.max()
            if not np.isnan(max_val):
                max_values.append(max_val)
    
    if max_values:
        max_value = max(max_values)
        # Add 15% padding, but cap at 30% maximum
        y_max = min(30, max_value * 1.15)
    else:
        y_max = 30  # Default to 30% if no valid data
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Matches",
        yaxis_title="Rate (%)",
        yaxis=dict(range=[0, y_max]),
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        width=1200,
        height=600
    )
    
    return fig

