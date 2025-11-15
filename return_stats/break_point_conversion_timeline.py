"""
Break point conversion timeline chart visualization.

This module provides functions to create timeline charts showing break points converted
and break point conversion percentage over time for a player when returning.
"""

# Third-party imports
import numpy as np
from plotly.subplots import make_subplots

# Local application imports
from .return_stats import calculate_match_return_stats
from utils.timeline_chart_utils import add_scatter_trace, add_trend_line, add_vertical_lines, get_match_hover_data


def add_opponent_comparison_traces(fig, x_positions, df, opponent_name=None, hoverdata=None):
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
    if 'opponent_bpConverted' not in df.columns or 'opponent_bpConversion_pct' not in df.columns:
        return
    
    opponent_label = f"{opponent_name}" if opponent_name else "Opponent"
    
    # Add opponent scatter traces with lighter colors
    add_scatter_trace(fig, x_positions, df['opponent_bpConverted'], 
                     'Opponent BPs Converted', 
                     '#86EFAC', 'Opponent Break Points Converted', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=False)  # light green
    
    add_scatter_trace(fig, x_positions, df['opponent_bpConversion_pct'], 
                     'Opponent BP Conversion %', 
                     '#93C5FD', 'Opponent Break Point Conversion %', hoverdata, 
                     use_lines=False, secondary_y=True, is_percentage=True)  # light blue
    
    # Add opponent trend lines with lighter colors
    add_trend_line(fig, df['opponent_bpConverted'], 'Opponent BPs Converted', '#86EFAC', secondary_y=False)
    add_trend_line(fig, df['opponent_bpConversion_pct'], 'Opponent BP Conversion %', '#93C5FD', secondary_y=True)


def create_break_point_conversion_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create break point conversion timeline chart showing break points converted and conversion percentage.
    
    Args:
        player_df: DataFrame with match data (should have w_bpFaced, l_bpFaced, w_bpSaved, l_bpSaved columns)
        player_name: Name of the player
        title: Chart title
        show_opponent_comparison: If True, show opponent stats overlay (default: False)
        opponent_name: Name of opponent for comparison (optional, for legend)
        
    Returns:
        go.Figure: Plotly figure object for timeline chart
    """
    # Calculate return statistics (includes break point conversion stats)
    # Note: player_df should already have is_winner column pre-calculated
    df = calculate_match_return_stats(player_df)
    
    # Sort by date and match number for chronological timeline display
    if 'tourney_date' in df.columns and 'match_num' in df.columns:
        df = df.sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
    # Get hover data for tooltips
    hoverdata = get_match_hover_data(df, player_name, case_sensitive=True)
    
    x_positions = list(range(len(df)))
    
    # Create figure with secondary y-axis for percentage
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Collect all series for y-axis range calculation and vertical lines
    all_series = []
    
    # Add elements in order: background first, then main data, then overlays
    # 1. Prepare series list for vertical lines
    series_for_lines = [df['player_bpConverted'], df['player_bpConversion_pct']]
    
    # 2. Add scatter plots (main data layer) - Player stats
    # Break Points Converted (count) - primary y-axis
    add_scatter_trace(fig, x_positions, df['player_bpConverted'], 
                     'BPs Converted', 
                     '#10B981', 'Break Points Converted', hoverdata, 
                     use_lines=False, secondary_y=False, is_percentage=False)  # green-500
    
    # Break Point Conversion % - secondary y-axis
    add_scatter_trace(fig, x_positions, df['player_bpConversion_pct'], 
                     'BP Conversion %', 
                     '#3B82F6', 'Break Point Conversion %', hoverdata, 
                     use_lines=False, secondary_y=True, is_percentage=True)  # blue-500
    
    all_series.extend([df['player_bpConverted'], df['player_bpConversion_pct']])
    
    # 3. Draw vertical lines (background layer) - after we know all series
    # Note: Vertical lines work best with single y-axis, so we'll skip for dual-axis chart
    
    # 4. Add trend lines (overlay layer) - Player trends
    add_trend_line(fig, df['player_bpConverted'], 'BPs Converted', '#10B981', secondary_y=False)
    add_trend_line(fig, df['player_bpConversion_pct'], 'BP Conversion %', '#3B82F6', secondary_y=True)
    
    # 5. Add opponent comparison traces if enabled
    if show_opponent_comparison:
        add_opponent_comparison_traces(fig, x_positions, df, opponent_name, hoverdata)
        # Update all_series to include opponent stats for y-axis range calculation
        if 'opponent_bpConverted' in df.columns:
            all_series.append(df['opponent_bpConverted'])
        if 'opponent_bpConversion_pct' in df.columns:
            all_series.append(df['opponent_bpConversion_pct'])
    
    # Calculate appropriate y-axis ranges
    # Primary y-axis (counts)
    max_values_count = []
    for series in [df['player_bpConverted']]:
        if series is not None and len(series) > 0:
            max_val = series.max()
            if not np.isnan(max_val):
                max_values_count.append(max_val)
    
    if max_values_count:
        max_value_count = max(max_values_count)
        y_max_count = max_value_count * 1.15
    else:
        y_max_count = 10  # Default to 10 if no valid data
    
    # Secondary y-axis (percentage)
    max_values_pct = []
    for series in [df['player_bpConversion_pct']]:
        if series is not None and len(series) > 0:
            max_val = series.max()
            if not np.isnan(max_val):
                max_values_pct.append(max_val)
    
    if max_values_pct:
        max_value_pct = max(max_values_pct)
        y_max_pct = min(max_value_pct * 1.15, 100)  # Cap at 100%
    else:
        y_max_pct = 100
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Matches",
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        width=1200,
        height=600
    )
    
    # Configure y-axes
    fig.update_yaxes(title_text="Break Points Converted (Count)", range=[0, y_max_count], secondary_y=False)
    fig.update_yaxes(title_text="Break Point Conversion (%)", range=[0, y_max_pct], secondary_y=True)
    
    return fig

