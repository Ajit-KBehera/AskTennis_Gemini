"""
Ace and Double Fault timeline chart visualization.

This module provides functions to create timeline charts showing ace rate
and double fault rate over time for both player and opponent.
"""

# Third-party imports
import numpy as np
import plotly.graph_objects as go

# Local application imports
from utils.timeline_chart_utils import add_scatter_trace, add_trend_line, add_vertical_lines, get_match_hover_data


# ============================================================================
# Function Definitions
# ============================================================================


def add_opponent_comparison_traces(fig, x_positions, df, opponent_name=None, hoverdata=None):
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
    
    # Add opponent scatter traces with lighter colors
    add_scatter_trace(fig, x_positions, df['opponent_ace_rate'], 
                     'Opponent Ace Rate', 
                     '#86EFAC', 'Opponent Ace Rate', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=True)  # light green
    add_scatter_trace(fig, x_positions, df['opponent_df_rate'], 
                     'Opponent DF Rate', 
                     '#FCA5A5', 'Opponent Double Fault Rate', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=True)  # light red
    
    # Add opponent trend lines with lighter colors
    add_trend_line(fig, df['opponent_ace_rate'], 'Opponent Ace Rate', '#86EFAC')
    add_trend_line(fig, df['opponent_df_rate'], 'Opponent DF Rate', '#FCA5A5')


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
    
    # Add elements in order: background first, then main data, then overlays
    # 1. Prepare series list for vertical lines
    series_for_lines = [df['player_ace_rate'], df['player_df_rate']]
    
    # 2. Add scatter plots (main data layer) - Player stats
    add_scatter_trace(fig, x_positions, df['player_ace_rate'], 
                     'Ace Rate', 
                     '#10B981',' Ace Rate', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=True)  # green-500
    add_scatter_trace(fig, x_positions, df['player_df_rate'], 
                     'DF Rate', 
                     '#EF4444', 'Double Fault Rate', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=True)  # red-500
    
    all_series.extend([df['player_ace_rate'], df['player_df_rate']])
    
    # 4. Draw vertical lines (background layer) - after we know all series
    add_vertical_lines(fig, series_for_lines)
    
    # 5. Add trend lines (overlay layer) - Player trends
    add_trend_line(fig, df['player_ace_rate'], 'Ace Rate', '#10B981')
    add_trend_line(fig, df['player_df_rate'], 'DF Rate', '#EF4444')
    
    # 6. Add opponent comparison traces if enabled
    if show_opponent_comparison:
        add_opponent_comparison_traces(fig, x_positions, df, opponent_name, hoverdata)
        # Update all_series to include opponent stats for y-axis range calculation
        if 'opponent_ace_rate' in df.columns:
            all_series.append(df['opponent_ace_rate'])
        if 'opponent_df_rate' in df.columns:
            all_series.append(df['opponent_df_rate'])
    
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

