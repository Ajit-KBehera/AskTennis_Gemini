"""
Serve statistics radar chart visualization.

This module provides functions to create radar (polar) charts displaying
comprehensive serve statistics including first serve percentage, first serve won,
second serve won, ace rate, and double fault rate.
"""

# Third-party imports
import numpy as np
import plotly.graph_objects as go

# Local application imports
# (No imports needed - stats dictionary passed directly)


# ============================================================================
# Function Definitions
# ============================================================================


def create_radar_chart(stats, player_name, year, title=None):
    """
    Create a radar chart for serve statistics.
    
    Args:
        stats: Dictionary containing serve statistics
        player_name: Name of the player (used in trace name)
        year: Year(s) for the chart (kept for API compatibility)
        title: Optional chart title. If None, a default title will be generated.
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Prepare data for radar chart
    categories = list(stats.keys())
    values = list(stats.values())
    
    # Handle NaN values by setting them to 0
    values = [v if not np.isnan(v) else 0 for v in values]
    
    # Create radar chart (polar plot)
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=player_name,
        line=dict(color='blue', width=2),
        marker=dict(size=8, color='blue')
    ))
    
    # Configure layout
    fig.update_layout(
        title=title if title else f"{player_name} - Serve Statistics Radar Chart",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                gridcolor='lightgray',
                gridwidth=1
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                rotation=90,
                direction='counterclockwise'
            )
        ),
        template='plotly_white',
        showlegend=True,
        width=800,
        height=800
    )
    
    return fig

