"""
Radar chart utility functions for creating consistent visualizations.

This module provides shared utility functions for creating radar (polar) charts
across serve and return statistics modules, eliminating code duplication.
"""

# Third-party imports
import numpy as np
import plotly.graph_objects as go


def create_radar_chart(stats, player_name, title, opponent_stats=None, opponent_name=None):
    """
    Create a radar chart for statistics with optional opponent comparison overlay.
    
    This function creates a polar (radar) chart displaying multiple statistics
    in a circular format. Useful for comparing serve or return statistics across
    different metrics.
    
    Args:
        stats: Dictionary containing player statistics (keys are category names, values are numeric)
        player_name: Name of the player (used in trace name)
        title: Chart title
        opponent_stats: Optional dictionary containing opponent statistics for comparison
        opponent_name: Optional name of opponent for legend (default: "Opponent")
        
    Returns:
        go.Figure: Plotly figure object with radar chart
    """
    # Prepare data for radar chart
    categories = list(stats.keys())
    player_values = list(stats.values())
    
    # Handle NaN values by setting them to 0
    player_values = [v if not np.isnan(v) else 0 for v in player_values]
    
    # Create radar chart (polar plot)
    fig = go.Figure()
    
    # Add player trace
    fig.add_trace(go.Scatterpolar(
        r=player_values,
        theta=categories,
        fill='toself',
        name=player_name,
        line=dict(color='blue', width=2),
        marker=dict(size=8, color='blue'),
        opacity=0.7
    ))
    
    # Add opponent trace if provided
    if opponent_stats:
        opponent_values = [opponent_stats.get(cat, 0) for cat in categories]
        opponent_values = [v if not np.isnan(v) else 0 for v in opponent_values]
        
        opponent_label = opponent_name if opponent_name else "Opponent"
        fig.add_trace(go.Scatterpolar(
            r=opponent_values,
            theta=categories,
            fill='toself',
            name=opponent_label,
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=8, color='red'),
            opacity=0.5
        ))
    
    # Configure layout
    fig.update_layout(
        title=title,
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

