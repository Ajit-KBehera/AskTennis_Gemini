"""
First serve timeline chart visualization.

This module provides functions to create timeline charts showing first serve
performance over time, including first serves in percentage and first serves won percentage.
"""

# Third-party imports
import plotly.graph_objects as go

# Local application imports
from utils.timeline_chart_utils import add_scatter_trace, add_trend_line, add_vertical_lines, get_match_hover_data


# ============================================================================
# Function Definitions
# ============================================================================


def add_opponent_comparison_traces(fig, x_positions, df, opponent_name=None, hoverdata=None):
    """
    Add opponent comparison traces to timeline chart.
    
    Adds opponent scatter plots and trend lines with lighter colors for comparison.
    
    Args:
        fig: Plotly figure object
        x_positions: List of x-axis positions
        df: DataFrame with opponent stats columns
        opponent_name: Name of opponent for legend
        hoverdata: Hover data for tooltips
    """
    if 'opponent_1stIn' not in df.columns or 'opponent_1stWon' not in df.columns or 'opponent_2ndWon' not in df.columns:
        return
    
    opponent_label = f"{opponent_name}" if opponent_name else "Opponent"
    
    # Add opponent scatter traces with lighter colors (using opacity/markersize to differentiate)
    add_scatter_trace(fig, x_positions, df['opponent_1stIn'], 
                     f'Opponent 1stIn', 
                     '#93C5FD', f'Opponent 1stIn', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # light blue
    add_scatter_trace(fig, x_positions, df['opponent_1stWon'], 
                     f'Opponent 1stWon', 
                     '#FCD34D', f'Opponent 1stWon', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # light orange
    add_scatter_trace(fig, x_positions, df['opponent_2ndWon'], 
                     f'Opponent 2ndWon', 
                     '#86EFAC', f'Opponent 2ndWon', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # light green
    
    # Add opponent trend lines with lighter colors
    add_trend_line(fig, df['opponent_1stIn'], f'Opponent 1stIn', '#93C5FD')
    add_trend_line(fig, df['opponent_1stWon'], f'Opponent 1stWon', '#FCD34D')
    add_trend_line(fig, df['opponent_2ndWon'], f'Opponent 2ndWon', '#86EFAC')

def create_timeline_chart(player_df, player_name, title, show_opponent_comparison=False, opponent_name=None):
    """
    Create the first serve timeline chart with optional opponent comparison.
    
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
    
    # Add elements in order: background first, then main data, then overlays
    # 1. Draw vertical lines (background layer)
    add_vertical_lines(fig, [df['player_1stIn'], df['player_1stWon'], df['player_2ndWon']])
    
    # 2. Add scatter plots (main data layer) - Player stats
    add_scatter_trace(fig, x_positions, df['player_1stIn'], '1stIn', '#2563EB', '1stIn', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # blue
    add_scatter_trace(fig, x_positions, df['player_1stWon'], '1stWon', '#F97316', '1stWon', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # orange
    add_scatter_trace(fig, x_positions, df['player_2ndWon'], '2ndWon', '#10B981', '2ndWon', hoverdata,
                     use_lines=False, secondary_y=False, is_percentage=True)  # green
    
    # 4. Add trend lines (overlay layer) - Player trends (same colors, dashed)
    add_trend_line(fig, df['player_1stIn'], '1stIn', '#2563EB')
    add_trend_line(fig, df['player_1stWon'], '1stWon', '#F97316')
    add_trend_line(fig, df['player_2ndWon'], '2ndWon', '#10B981')
    
    # 5. Add opponent comparison traces if enabled
    if show_opponent_comparison:
        add_opponent_comparison_traces(fig, x_positions, df, opponent_name, hoverdata)
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Matches",
        yaxis_title="(%)",
        yaxis=dict(range=[0, 100]),
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        width=1200,
        height=600
    )
    
    return fig
