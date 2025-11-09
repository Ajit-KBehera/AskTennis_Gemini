import numpy as np
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path for serve_stats import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from serve_stats import build_year_suffix

# ============================================================================
# Function Definitions
# ============================================================================


def create_radar_chart(stats, player_name, year):
    """
    Create a radar chart for serve statistics.
    
    Args:
        stats: Dictionary containing serve statistics
        player_name: Name of the player
        year: Year(s) for the chart. Can be:
            - int or str: Single year (e.g., 2024)
            - list: Multiple years (e.g., [2022, 2023, 2024])
            - None: Career view (all years)
        
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
    
    # Update layout for polar chart
    fig.update_layout(
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
        title=f"{player_name} - Serve Statistics Radar Chart - {build_year_suffix(year)}",
        font=dict(size=14),
        width=800,
        height=800,
        template='plotly_white',
        showlegend=True
    )
    
    return fig

