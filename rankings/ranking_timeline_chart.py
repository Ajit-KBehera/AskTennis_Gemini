"""
Ranking timeline chart visualization.

This module provides functions to create timeline charts showing player ranking
progression over time from ATP and WTA rankings data.
"""

# Third-party imports
import plotly.graph_objects as go
import pandas as pd


def create_ranking_timeline_chart(player_name, ranking_df, title=None):
    """
    Create a ranking timeline chart showing player's ranking over time.
    
    Args:
        player_name: Name of the player
        ranking_df: DataFrame containing ranking data with columns:
                   - ranking_date: Date of ranking
                   - rank: Ranking position (lower is better)
                   - tour: 'ATP' or 'WTA' (optional)
        title: Optional chart title. If None, generates default title.
        
    Returns:
        go.Figure: Plotly figure object for ranking timeline chart
    """
    if ranking_df.empty:
        return None
    
    # Sort by date
    df = ranking_df.copy()
    if 'ranking_date' in df.columns:
        df['ranking_date'] = pd.to_datetime(df['ranking_date'])
        df = df.sort_values('ranking_date').reset_index(drop=True)
    
    # Generate title if not provided
    if title is None:
        title = f"{player_name} - Ranking Timeline"
    
    # Create figure
    fig = go.Figure()
    
    # Determine if we have ATP/WTA separation
    if 'tour' in df.columns and df['tour'].nunique() > 1:
        # Separate traces for ATP and WTA
        for tour in df['tour'].unique():
            tour_df = df[df['tour'] == tour]
            fig.add_trace(go.Scatter(
                x=tour_df['ranking_date'],
                y=tour_df['rank'],
                mode='lines+markers',
                name=f'{tour} Ranking',
                line=dict(width=2),
                marker=dict(size=4),
                hovertemplate=f'{tour} Rank: %{{y}}<br>' +
                              'Date: %{x|%Y-%m-%d}<extra></extra>'
            ))
    else:
        # Single trace for all rankings
        fig.add_trace(go.Scatter(
            x=df['ranking_date'],
            y=df['rank'],
            mode='lines+markers',
            name='Ranking',
            line=dict(width=2, color='#2563EB'),
            marker=dict(size=4, color='#2563EB'),
            hovertemplate='Rank: %{y}<br>' +
                          'Date: %{x|%Y-%m-%d}<extra></extra>'
        ))
    
    # Configure layout
    # Note: Lower rank number is better, so we invert the y-axis
    max_rank = df['rank'].max() if not df.empty else 100
    min_rank = df['rank'].min() if not df.empty else 1
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Ranking",
        yaxis=dict(
            range=[max_rank + 10, max(1, min_rank - 5)],  # Inverted: higher rank number at bottom
            autorange='reversed'  # Reverse y-axis so rank 1 is at top
        ),
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        width=1200,
        height=600
    )
    
    return fig

