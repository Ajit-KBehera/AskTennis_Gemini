"""
Return points won percentage timeline chart visualization.

This module provides functions to create timeline charts showing return points won
percentage over time, tracking return performance progression.
"""

# Third-party imports
import plotly.graph_objects as go

# Local application imports
from .return_stats import get_match_hover_data
from utils.timeline_chart_utils import add_scatter_trace, add_trend_line, add_vertical_lines


# ============================================================================
# Function Definitions
# ============================================================================


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
    if 'opponent_return_points_won_pct' not in df.columns:
        return
    
    opponent_label = f"{opponent_name}" if opponent_name else "Opponent"
    
    # Add opponent scatter trace with lighter color
    add_scatter_trace(fig, x_positions, df['opponent_return_points_won_pct'], 
                     'Opponent Return Points Won %', '#93C5FD', 
                     'Opponent Return Points Won %', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # light blue
    
    # Add opponent trend line with lighter color
    add_trend_line(fig, df['opponent_return_points_won_pct'], 
                  'Opponent Return Points Won %', '#93C5FD')


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
    add_scatter_trace(fig, x_positions, df['player_return_points_won_pct'], 
                     'Return Points Won %', '#2563EB', 'Return Points Won %', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # blue
    
    # 4. Add trend lines (overlay layer) - Player trends
    add_trend_line(fig, df['player_return_points_won_pct'], 'Return Points Won %', '#2563EB')
    
    # 5. Add opponent comparison traces if enabled
    if show_opponent_comparison:
        add_opponent_comparison_traces(fig, x_positions, df, opponent_name, hoverdata)
    
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

