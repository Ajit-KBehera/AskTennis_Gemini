"""
Serve performance by surface grouped bar chart visualization.

This module provides functions to create grouped bar charts showing serve statistics
(1st Serve In %, 1st Serve Won %, 2nd Serve Won %) across different surfaces.
"""

# Third-party imports
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Local application imports
from .serve_stats import calculate_aggregated_player_serve_stats


# ============================================================================
# Function Definitions
# ============================================================================

def calculate_surface_stats(df, player_name, case_sensitive=False):
    """
    Calculate aggregated serve statistics grouped by surface.
    
    Args:
        df: DataFrame containing match data with serve statistics already calculated
        player_name: Name of the player (optional if stats columns already exist)
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        pd.DataFrame: DataFrame with columns: surface, 1st Serve In %, 1st Serve Won %, 2nd Serve Won %, match_count
    """
    # Ensure stats are calculated
    if 'player_1stIn' not in df.columns:
        # Pre-calculate is_winner, opponent, result columns before calling calculate_match_serve_stats
        from .serve_stats import calculate_match_serve_stats
        from utils.df_utils import add_player_match_columns
        df = add_player_match_columns(df, player_name, case_sensitive)
        df = calculate_match_serve_stats(df, player_name, case_sensitive)
    
    # Filter out rows with missing surface data
    df_filtered = df[df['surface'].notna() & (df['surface'] != '')].copy()
    
    if df_filtered.empty:
        return pd.DataFrame(columns=['surface', '1st Serve In %', '1st Serve Won %', '2nd Serve Won %', 'match_count'])
    
    # Group by surface and calculate aggregated stats
    surface_stats = []
    
    for surface in df_filtered['surface'].unique():
        surface_df = df_filtered[df_filtered['surface'] == surface]
        
        # Calculate aggregated stats for this surface
        stats = calculate_aggregated_player_serve_stats(surface_df, player_name=None, case_sensitive=False)
        
        # Get match count
        match_count = len(surface_df)
        
        surface_stats.append({
            'surface': surface,
            '1st Serve In %': stats.get('1st Serve %', np.nan),
            '1st Serve Won %': stats.get('1st Serve Won %', np.nan),
            '2nd Serve Won %': stats.get('2nd Serve Won %', np.nan),
            'match_count': match_count
        })
    
    result_df = pd.DataFrame(surface_stats)
    
    # Sort surfaces in a standard order: Hard, Clay, Grass, Carpet, then others
    surface_order = ['Hard', 'Clay', 'Grass', 'Carpet']
    custom_order = [s for s in surface_order if s in result_df['surface'].values]
    other_surfaces = [s for s in result_df['surface'].values if s not in surface_order]
    final_order = custom_order + sorted(other_surfaces)
    
    # Reorder DataFrame
    result_df['surface'] = pd.Categorical(result_df['surface'], categories=final_order, ordered=True)
    result_df = result_df.sort_values('surface').reset_index(drop=True)
    
    return result_df


def create_surface_performance_chart(df, player_name, title, case_sensitive=False):
    """
    Create a grouped bar chart showing serve performance by surface.
    
    Args:
        df: DataFrame containing match data with serve statistics
        player_name: Name of the player
        title: Chart title
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        go.Figure: Plotly figure object for grouped bar chart
    """
    # Calculate surface statistics
    surface_stats_df = calculate_surface_stats(df, player_name, case_sensitive)
    
    if surface_stats_df.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No surface data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            xaxis_title="Surface",
            yaxis_title="Percentage (%)",
            template='plotly_white',
            width=1200,
            height=600
        )
        return fig
    
    # Prepare data for grouped bar chart
    surfaces = surface_stats_df['surface'].tolist()
    first_serve_in = surface_stats_df['1st Serve In %'].tolist()
    first_serve_won = surface_stats_df['1st Serve Won %'].tolist()
    second_serve_won = surface_stats_df['2nd Serve Won %'].tolist()
    match_counts = surface_stats_df['match_count'].tolist()
    
    # Create figure
    fig = go.Figure()
    
    # Define colors for each metric
    colors = {
        '1st Serve In %': '#2563EB',  # blue-600
        '1st Serve Won %': '#F97316',  # orange-500
        '2nd Serve Won %': '#10B981'   # green-500
    }
    
    # Add bars for each metric
    fig.add_trace(go.Bar(
        name='1st Serve In %',
        x=surfaces,
        y=first_serve_in,
        marker_color=colors['1st Serve In %'],
        hovertemplate='<b>1st Serve In %</b><br>' +
                      'Surface: %{x}<br>' +
                      'Percentage: %{y:.2f}%<br>' +
                      'Matches: %{customdata}<extra></extra>',
        customdata=match_counts
    ))
    
    fig.add_trace(go.Bar(
        name='1st Serve Won %',
        x=surfaces,
        y=first_serve_won,
        marker_color=colors['1st Serve Won %'],
        hovertemplate='<b>1st Serve Won %</b><br>' +
                      'Surface: %{x}<br>' +
                      'Percentage: %{y:.2f}%<br>' +
                      'Matches: %{customdata}<extra></extra>',
        customdata=match_counts
    ))
    
    fig.add_trace(go.Bar(
        name='2nd Serve Won %',
        x=surfaces,
        y=second_serve_won,
        marker_color=colors['2nd Serve Won %'],
        hovertemplate='<b>2nd Serve Won %</b><br>' +
                      'Surface: %{x}<br>' +
                      'Percentage: %{y:.2f}%<br>' +
                      'Matches: %{customdata}<extra></extra>',
        customdata=match_counts
    ))
    
    # Configure layout
    fig.update_layout(
        title=title,
        xaxis_title="Surface",
        yaxis_title="Percentage (%)",
        yaxis=dict(range=[0, 100]),
        barmode='group',  # Grouped bars
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        width=1200,
        height=600,
        hovermode='closest'
    )
    
    return fig

