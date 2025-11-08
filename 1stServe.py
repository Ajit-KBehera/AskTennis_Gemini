import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
import sys

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

conn = sqlite3.connect("tennis_data_OE_Singles_Rankings_Players.db")
df = pd.read_sql_query("SELECT * FROM matches", conn)
conn.close()  # Close database connection

# Example player name
player_name = 'Carlos Alcaraz'
year = 2024

# Filter matches involving the player
player = df[((df['winner_name'] == player_name) | (df['loser_name'] == player_name)) & (df['event_year'].isin([year]))].copy()

# Sort by tourney date and match number
player = player.sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)

# Compute player's first-serve-in percentage, guarding against zero/NaN serve attempts
player['player_1stIn'] = np.where(
    player['winner_name'] == player_name,
    np.where(player['w_svpt'] > 0, player['w_1stIn'] / player['w_svpt'] * 100, np.nan),
    np.where(player['l_svpt'] > 0, player['l_1stIn'] / player['l_svpt'] * 100, np.nan)
)

# Compute player's first-serve-won percentage, guarding against zero/NaN serve attempts and division by zero
player['player_1stWon'] = np.where(
    player['winner_name'] == player_name,
    np.where((player['w_svpt'] > 0) & (player['w_1stIn'] > 0), 
             player['w_1stWon'] / player['w_1stIn'] * 100, np.nan),
    np.where((player['l_svpt'] > 0) & (player['l_1stIn'] > 0), 
             player['l_1stWon'] / player['l_1stIn'] * 100, np.nan)
)

# Calculate opponent and result for hover tooltips
player['opponent'] = np.where(
    player['winner_name'] == player_name,
    player['loser_name'],
    player['winner_name']
)
player['result'] = np.where(player['winner_name'] == player_name, 'W', 'L')
playerdata = player[['tourney_name', 'round', 'opponent', 'result']].values

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

# Try to show with notebook renderer, fallback to browser or save HTML file
try:
    if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
        from IPython.display import HTML, display  # type: ignore
        display(HTML(fig.to_html(include_plotlyjs='cdn')))
    else:
        # Try browser renderer first (opens in default browser)
        try:
            fig.show(renderer='browser')
        except Exception:
            # Fallback: save to HTML file
            html_file = 'tennis_plot.html'
            fig.write_html(html_file)
            print(f"Plot saved to {html_file}. Open it in your browser to view.")
except Exception as e:
    # Final fallback: save to HTML file
    html_file = 'tennis_plot.html'
    fig.write_html(html_file)
    print(f"Plot saved to {html_file}. Open it in your browser to view.")