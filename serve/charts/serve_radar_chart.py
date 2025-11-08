import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
import sys
import os

# Add parent directory to path to import serve_stats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from serve_stats import calculate_aggregated_serve_stats

# ============================================================================
# Function Definitions
# ============================================================================


def create_radar_chart(stats, player_name, year):
    """
    Create a radar chart for serve statistics.
    
    Args:
        stats: Dictionary containing serve statistics
        player_name: Name of the player
        year: Year of the season
        
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
        title=f"{player_name} - Serve Statistics Radar Chart - {year} Season",
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

# Example player name
player_name = 'Alex de Minaur'
year = 2024
sql_query = "SELECT * FROM matches WHERE event_year = ? AND (winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)"

with sqlite3.connect("tennis_data_OE_Singles_Rankings_Players.db") as conn:
    df = pd.read_sql_query(sql_query, conn, params=(year, player_name, player_name)).sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)

# Check if dataframe is empty
if df.empty:
    print(f"No matches found for {player_name} in {year}")
    sys.exit(1)

# Calculate aggregated serve statistics using shared module
serve_stats = calculate_aggregated_serve_stats(df, player_name, case_sensitive=False)

# Print statistics for reference
print(f"\nServe Statistics for {player_name} ({year}):")
print("-" * 50)
for stat_name, stat_value in serve_stats.items():
    if not np.isnan(stat_value):
        print(f"{stat_name}: {stat_value:.2f}")
    else:
        print(f"{stat_name}: N/A")
print("-" * 50)

# ============================================================================
# Plot Creation
# ============================================================================

# Create radar chart
fig = create_radar_chart(serve_stats, player_name, year)

# ============================================================================
# Display Plot
# ============================================================================

# Display Plot
try:
    fig.show(renderer='browser')
    print("\nPlot displayed in browser.")
except Exception:
    print("Error displaying plot in browser. Saving to HTML file.")
    html_file = 'serve_radar_chart.html'
    fig.write_html(html_file)
    print(f"Plot saved to {html_file}.")

