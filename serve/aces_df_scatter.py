"""
Aces vs Double Faults scatter plot visualization.

This module provides functions to create scatter plots showing the relationship
between aces and double faults per match, with color coding by surface and
size coding by match importance.
"""

# Third-party imports
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Local application imports
from .serve_stats import get_match_hover_data


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_match_importance(round_value):
    """
    Calculate match importance score based on round.
    
    Args:
        round_value: Round string (e.g., 'F', 'SF', 'QF', 'R16', etc.)
        
    Returns:
        int: Importance score (higher = more important)
    """
    if pd.isna(round_value) or round_value == '':
        return 1
    
    round_str = str(round_value).upper()
    
    # Round-based importance scoring
    importance_map = {
        'F': 10,      # Final
        'SF': 8,      # Semi-Final
        'QF': 6,      # Quarter-Final
        'R16': 4,     # Round of 16
        'R32': 3,     # Round of 32
        'R64': 2,     # Round of 64
        'R128': 1,    # Round of 128
        'RR': 5,      # Round Robin
    }
    
    # Check for qualifying rounds
    if round_str.startswith('Q'):
        return 1
    
    return importance_map.get(round_str, 1)


def get_surface_color(surface):
    """
    Get color for surface type.
    
    Args:
        surface: Surface string (e.g., 'Hard', 'Clay', 'Grass', 'Carpet')
        
    Returns:
        str: Hex color code
    """
    if pd.isna(surface) or surface == '':
        return '#808080'  # Gray for unknown
    
    surface_str = str(surface).strip()
    
    color_map = {
        'Hard': '#2563EB',    # blue-600
        'Clay': '#F97316',    # orange-500
        'Grass': '#10B981',   # green-500
        'Carpet': '#8B5CF6',  # violet-500
    }
    
    return color_map.get(surface_str, '#808080')  # Gray for other surfaces


def prepare_scatter_data(df, player_name, case_sensitive=False):
    """
    Prepare data for scatter plot: calculate aces, double faults, and match importance.
    
    Args:
        df: DataFrame containing match data
        player_name: Name of the player
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        pd.DataFrame: DataFrame with columns: aces, double_faults, surface, importance, 
                     and all original columns
    """
    df = df.copy()
    
    # Determine if player was winner or loser for each match
    if case_sensitive:
        is_winner = df['winner_name'] == player_name
    else:
        is_winner = df['winner_name'].str.lower() == player_name.lower()
    
    # Get aces and double faults for the player
    df['aces'] = np.where(is_winner, df['w_ace'], df['l_ace'])
    df['double_faults'] = np.where(is_winner, df['w_df'], df['l_df'])
    
    # Fill NaN values with 0 (matches without stats)
    df['aces'] = df['aces'].fillna(0)
    df['double_faults'] = df['double_faults'].fillna(0)
    
    # Calculate match importance based on round
    df['importance'] = df['round'].apply(calculate_match_importance)
    
    # Ensure surface column exists
    if 'surface' not in df.columns:
        df['surface'] = 'Unknown'
    df['surface'] = df['surface'].fillna('Unknown')
    
    return df


# ============================================================================
# Chart Creation Functions
# ============================================================================

def create_aces_df_scatter_chart(df, player_name, title, case_sensitive=False, show_trend_line=True):
    """
    Create a scatter plot showing aces vs double faults per match.
    
    Args:
        df: DataFrame containing match data
        player_name: Name of the player
        title: Chart title
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        show_trend_line: Whether to show trend line (default: True)
        
    Returns:
        go.Figure: Plotly figure object for scatter plot
    """
    # Prepare data
    df_prepared = prepare_scatter_data(df, player_name, case_sensitive)
    
    # Filter out rows with invalid data
    df_prepared = df_prepared[
        (df_prepared['aces'].notna()) & 
        (df_prepared['double_faults'].notna())
    ].copy()
    
    if df_prepared.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No match data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            xaxis_title="Aces per Match",
            yaxis_title="Double Faults per Match",
            template='plotly_white',
            width=1200,
            height=600
        )
        return fig
    
    # Reset index to ensure positional alignment with hover data
    df_prepared = df_prepared.reset_index(drop=True)
    
    # Get hover data
    hoverdata = get_match_hover_data(df_prepared, player_name, case_sensitive)
    
    # Create figure
    fig = go.Figure()
    
    # Group by surface to create separate traces for legend
    surfaces = df_prepared['surface'].unique()
    surface_colors = {s: get_surface_color(s) for s in surfaces}
    
    for surface in surfaces:
        surface_mask = df_prepared['surface'] == surface
        surface_df = df_prepared[surface_mask]
        
        if surface_df.empty:
            continue
        
        # Calculate marker sizes (logarithmic scale for importance)
        # Size range: 5 to 25 pixels
        importance_scores = surface_df['importance'].values
        min_size, max_size = 5, 25
        if importance_scores.max() > importance_scores.min():
            # Logarithmic scaling
            log_scores = np.log1p(importance_scores)  # log(1 + score)
            log_min = np.log1p(importance_scores.min())
            log_max = np.log1p(importance_scores.max())
            if log_max > log_min:
                normalized = (log_scores - log_min) / (log_max - log_min)
                marker_sizes = min_size + (max_size - min_size) * normalized
            else:
                marker_sizes = np.full(len(importance_scores), (min_size + max_size) / 2)
        else:
            marker_sizes = np.full(len(importance_scores), (min_size + max_size) / 2)
        
        # Get hover data for this surface using positional indexing
        surface_hoverdata = hoverdata[surface_mask]
        
        # Add scatter trace for this surface
        fig.add_trace(go.Scatter(
            x=surface_df['aces'].values,
            y=surface_df['double_faults'].values,
            mode='markers',
            name=surface,
            marker=dict(
                color=surface_colors[surface],
                size=marker_sizes,
                opacity=0.7,
                line=dict(width=0.5, color='white'),
                sizemode='diameter'
            ),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Aces: %{x}<br>' +
                         'Double Faults: %{y}<br>' +
                         'Tournament: %{customdata[0]}<br>' +
                         'Round: %{customdata[1]}<br>' +
                         'Opponent: %{customdata[2]}<br>' +
                         'Result: %{customdata[3]}<br>' +
                         'Year: %{customdata[4]}<extra></extra>',
            customdata=surface_hoverdata
        ))
    
    # Add trend line if requested
    if show_trend_line and len(df_prepared) >= 2:
        # Filter out zero values for trend line (optional - can include them)
        trend_df = df_prepared[
            (df_prepared['aces'] > 0) | (df_prepared['double_faults'] > 0)
        ]
        
        if len(trend_df) >= 2:
            x_trend = trend_df['aces'].values
            y_trend = trend_df['double_faults'].values
            
            # Calculate linear regression
            if len(x_trend) >= 2 and x_trend.std() > 0:
                z = np.polyfit(x_trend, y_trend, 1)
                p = np.poly1d(z)
                
                x_line = np.linspace(x_trend.min(), x_trend.max(), 100)
                y_line = p(x_line)
                
                fig.add_trace(go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode='lines',
                    name='Trend Line',
                    line=dict(color='gray', dash='dash', width=2),
                    opacity=0.6,
                    hoverinfo='skip'
                ))
    
    # Calculate axis ranges with padding
    max_aces = df_prepared['aces'].max()
    max_df = df_prepared['double_faults'].max()
    
    # Add 10% padding
    x_max = max_aces * 1.1 if max_aces > 0 else 10
    y_max = max_df * 1.1 if max_df > 0 else 10
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Aces per Match",
        yaxis_title="Double Faults per Match",
        xaxis=dict(range=[-1, x_max]),
        yaxis=dict(range=[-1, y_max]),
        template='plotly_white',
        showlegend=True,
        legend=dict(
            title="Surface",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        width=1200,
        height=600,
        hovermode='closest',
        annotations=[
            dict(
                text="Size indicates match importance<br>(larger = more important)",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                align="left",
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
                font=dict(size=10, color="gray")
            )
        ]
    )
    
    return fig

