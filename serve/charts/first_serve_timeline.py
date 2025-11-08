import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
import sys
import os

# Add parent directory to path to import serve_stats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from serve_stats import calculate_match_serve_stats, get_match_hover_data

# ============================================================================
# Function Definitions
# ============================================================================

def add_scatter_trace(fig, x_positions, y_data, name, color, hover_label, customdata):
    """Add a scatter plot trace to the figure"""
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_data,
        mode='markers',
        name=name,
        marker=dict(color=color, size=8),
        hovertemplate=f'{hover_label}: %{{y:.2f}}%<br>' +                  
                      'Tournament: %{customdata[0]}<br>' +
                      'Round: %{customdata[1]}<br>' +
                      'Opponent: %{customdata[2]}<br>' +
                      'Result: %{customdata[3]}<extra></extra>',
        customdata=customdata
    ))


def add_trend_line(fig, y_data, name, color):
    """Add a linear trend line to the figure"""
    mask = y_data.notna()
    x = np.arange(len(y_data))[mask]
    y = y_data.loc[mask].values
    
    if len(x) >= 2:
        xc = x - x.mean()
        z = np.polyfit(xc, y, 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=x,
            y=p(xc),
            mode='lines',
            name=f'Trend ({name})',
            line=dict(color=color, dash='dash', width=2),
            opacity=0.8,
            hoverinfo='skip'
        ))


def add_vertical_lines(fig, y_data_series, y_min=0, color='gray', width=0.8, opacity=0.3):
    """
    Draw vertical lines from y_min to the maximum value across multiple y_data series at each x position.
    
    Args:
        fig (go.Figure): Plotly figure object to add lines to
        y_data_series (list): List of pandas Series containing y-values (e.g., [series1, series2])
        y_min (float): Starting y-value for vertical lines (default: 0)
        color (str): Line color (default: 'gray')
        width (float): Line width (default: 0.8)
        opacity (float): Line opacity between 0 and 1 (default: 0.3)
    """
    max_values = np.nanmax([series.values for series in y_data_series], axis=0)
    valid_indices = ~np.isnan(max_values)
    
    if np.any(valid_indices):
        x_vals = np.arange(len(y_data_series[0]))[valid_indices]
        y_vals = max_values[valid_indices]
        for i, val in zip(x_vals, y_vals):
            fig.add_trace(go.Scatter(
                x=[i, i], y=[y_min, val],
                mode='lines',
                line=dict(color=color, width=width),
                opacity=opacity,
                showlegend=False,
                hoverinfo='skip'
            ))


# ============================================================================
# Data Loading and Processing
# ============================================================================

# Example player name
player_name = 'Elena Rybakina'
year = 2024
sql_query = "SELECT * FROM matches WHERE event_year = ? AND (winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)"

with sqlite3.connect("tennis_data_OE_Singles_Rankings_Players.db") as conn:
    df = pd.read_sql_query(sql_query, conn, params=(year, player_name, player_name)).sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)

# Check if dataframe is empty
if df.empty:
    print(f"No matches found for {player_name} in {year}")
    sys.exit(1)

# Calculate serve statistics using shared module
player = calculate_match_serve_stats(df, player_name, case_sensitive=True)
playerdata = get_match_hover_data(df, player_name, case_sensitive=True)

# Create x-axis positions
x_positions = list(range(len(player)))

# ============================================================================
# Plot Creation
# ============================================================================

# Create Plotly figure
fig = go.Figure()

# Add elements in order: background first, then main data, then overlays
# 1. Draw vertical lines (background layer)
add_vertical_lines(fig, [player['player_1stIn'], player['player_1stWon']])

# 2. Add scatter plots (main data layer)
add_scatter_trace(fig, x_positions, player['player_1stIn'], 'First Serves In (%)', 'blue', 'First Serves In', playerdata)
add_scatter_trace(fig, x_positions, player['player_1stWon'], 'First Serves Won (%)', 'orange', 'First Serves Won', playerdata)

# 3. Add trend lines (overlay layer)
add_trend_line(fig, player['player_1stIn'], 'First Serves In', 'blue')
add_trend_line(fig, player['player_1stWon'], 'First Serves Won', 'orange')

# 4. Update layout (final step)
fig.update_layout(
    title=f"{player_name} - First Serve Performance - {year} Season",
    xaxis_title="Matches",
    yaxis_title="(%)",
    hovermode='closest',
    width=1200,
    height=600,
    template='plotly_white',
    showlegend=True
)

# ============================================================================
# Display Plot
# ============================================================================

# Display Plot
try:
    fig.show(renderer='browser')
    print("Plot displayed in browser.")
except Exception:
    print("Error displaying plot in browser. Saving to HTML file.")
    html_file = 'first_serve_timeline_plot.html'
    fig.write_html(html_file)
    print(f"Plot saved to {html_file}.")

