import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

# Add parent directories to path to import shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(__file__))

from serve_stats import calculate_aggregated_serve_stats
from data_loader import load_player_matches
from utils.chart_utils import display_chart

# ============================================================================
# Function Definitions
# ============================================================================

def _build_year_suffix(year):
    """Build year suffix string for chart titles."""
    if year is None:
        return "Career"
    elif isinstance(year, list):
        if len(year) == 1:
            return f"{year[0]} Season"
        else:
            return f"{min(year)}-{max(year)} Seasons"
    else:
        return f"{year} Season"


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
        title=f"{player_name} - Serve Statistics Radar Chart - {_build_year_suffix(year)}",
        font=dict(size=14),
        width=800,
        height=800,
        template='plotly_white',
        showlegend=True
    )
    
    return fig


# ============================================================================
# Data Loading and Processing
# ============================================================================

if __name__ == "__main__":
    # Example player name
    player_name = 'Elena Rybakina'
    year = 2024
    
    # Load match data using shared function
    df = load_player_matches(player_name, year)
    
    # Calculate aggregated serve statistics using shared module
    serve_stats = calculate_aggregated_serve_stats(df, player_name, case_sensitive=False)
    
    # ============================================================================
    # Plot Creation
    # ============================================================================
    
    # Create radar chart
    fig = create_radar_chart(serve_stats, player_name, year)
    
    # ============================================================================
    # Display Plot
    # ============================================================================
    
    # Display plot using shared function
    display_chart(fig, html_filename='serve_radar_chart.html')

