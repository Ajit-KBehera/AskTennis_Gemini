"""
Timeline chart utility functions for creating consistent visualizations.

This module provides shared utility functions for creating timeline charts
across serve and return statistics modules, eliminating code duplication.
"""

# Third-party imports
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def add_scatter_trace(fig, x_positions, y_data, name, color, hover_label, customdata, 
                      use_lines=True, secondary_y=False, is_percentage=False):
    """
    Add a scatter plot trace to the figure with optional lines and formatting.
    
    Args:
        fig: Plotly figure object
        x_positions: List/array of x-axis positions
        y_data: Series or array of y-axis data
        name: Trace name for legend
        color: Color string (hex code or color name)
        hover_label: Label for hover tooltip
        customdata: Custom data array for hover tooltips
        use_lines: If True, connect markers with lines (default: True)
        secondary_y: If True, add trace to secondary y-axis (default: False)
        is_percentage: If True, format hover value as percentage with 2 decimals (default: False)
        
    Returns:
        None (modifies fig in place)
    """
    mode = 'markers+lines' if use_lines else 'markers'
    
    # Format hover value based on whether it's a percentage or count
    if is_percentage:
        hover_format = f'{hover_label}: %{{y:.2f}}%<br>'
    else:
        hover_format = f'{hover_label}: %{{y:.0f}}<br>'
    
    trace_kwargs = {
        'x': x_positions,
        'y': y_data,
        'mode': mode,
        'name': name,
        'marker': dict(color=color, size=8),
        'hovertemplate': hover_format +                  
                      'Year: %{customdata[0]}<br>' +
                      'Tournament: %{customdata[1]}<br>' +
                      'Round: %{customdata[2]}<br>' +
                      'Opponent: %{customdata[3]}<br>' +
                      'Result: %{customdata[4]}<extra></extra>',
        'customdata': customdata
    }
    
    if use_lines:
        trace_kwargs['line'] = dict(color=color, width=2)
    
    if secondary_y:
        fig.add_trace(go.Scatter(**trace_kwargs), secondary_y=True)
    else:
        fig.add_trace(go.Scatter(**trace_kwargs))


def add_trend_line(fig, y_data, name, color, secondary_y=False):
    """
    Add a linear trend line to the figure.
    
    Args:
        fig: Plotly figure object
        y_data: Series or array of y-axis data
        name: Trend line name for legend
        color: Color string (hex code or color name)
        secondary_y: If True, add trend line to secondary y-axis (default: False)
        
    Returns:
        None (modifies fig in place)
    """
    mask = y_data.notna()
    x = np.arange(len(y_data))[mask]
    y = y_data.loc[mask].values
    
    if len(x) >= 2:
        xc = x - x.mean()
        z = np.polyfit(xc, y, 1)
        p = np.poly1d(z)
        trend_trace = go.Scatter(
            x=x,
            y=p(xc),
            mode='lines',
            name=f'{name}',
            line=dict(color=color, dash='dash', width=2),
            opacity=0.8,
            hoverinfo='skip'
        )
        
        if secondary_y:
            fig.add_trace(trend_trace, secondary_y=True)
        else:
            fig.add_trace(trend_trace)


def add_vertical_lines(fig, y_data_series, y_min=0, y_max=None, color='gray', width=0.8, opacity=0.3):
    """
    Draw vertical lines from y_min to the highest value between the series at each x position.
    
    This function creates background vertical lines connecting the bottom of the chart (y_min)
    to the maximum value across all provided series at each x position. Useful for visualizing
    the range of values across multiple metrics at each data point.
    
    Args:
        fig (go.Figure): Plotly figure object to add lines to
        y_data_series (list): List of pandas Series containing y-values (e.g., [series1, series2])
        y_min (float): Starting y-value for vertical lines (default: 0)
        y_max (float): Ending y-value for vertical lines. If None, uses max of all series per match (default: None)
        color (str): Line color (default: 'gray')
        width (float): Line width (default: 0.8)
        opacity (float): Line opacity between 0 and 1 (default: 0.3)
        
    Returns:
        None (modifies fig in place)
    """
    if not y_data_series:
        return
    
    # Find valid indices (where at least one series has valid data)
    valid_mask = np.zeros(len(y_data_series[0]), dtype=bool)
    for series in y_data_series:
        valid_mask |= ~np.isnan(series)
    
    if not np.any(valid_mask):
        return
    
    x_vals = np.arange(len(y_data_series[0]))[valid_mask]
    
    for i in x_vals:
        # Get values from all series at this index
        values = []
        for series in y_data_series:
            val = series.iloc[i] if hasattr(series, 'iloc') else series[i]
            if not np.isnan(val):
                values.append(val)
        
        if values:
            line_max = max(values)
            # Use y_max if provided, otherwise use calculated maximum
            line_end = y_max if y_max is not None else line_max
            
            fig.add_trace(go.Scatter(
                x=[i, i], y=[y_min, line_end],
                mode='lines',
                line=dict(color=color, width=width),
                opacity=opacity,
                showlegend=False,
                hoverinfo='skip'
            ))


def get_match_hover_data(player_df, player_name, case_sensitive=False):
    """
    Get hover data for match tooltips (tournament, round, opponent, result, year).
    
    This function extracts match metadata for use in timeline chart tooltips.
    It expects the DataFrame to have pre-calculated 'is_winner', 'opponent', and 'result' columns.
    
    Args:
        player_df: DataFrame containing match data for the player
        player_name: Name of the player (for backward compatibility, not currently used)
        case_sensitive: Whether to use case-sensitive name matching (for backward compatibility, not currently used)
        
    Returns:
        numpy.ndarray: Array of hover data for each match with columns:
            [year, tourney_name, round, opponent, result]
            where result is "W" for wins and "L" for losses
            
    Raises:
        ValueError: If 'is_winner' column is missing from the DataFrame
    """
    df = player_df.copy()
    
    # Use pre-calculated columns if available (is_winner, opponent, result should be calculated before calling this function)
    if 'is_winner' not in df.columns:
        raise ValueError("is_winner column must be pre-calculated. Use add_player_match_columns() from utils.df_utils before calling this function.")
    
    # opponent and result should also exist if is_winner exists (they're calculated together)
    
    # Extract year from tourney_date or use event_year if available
    if 'event_year' in df.columns:
        df['year'] = df['event_year'].fillna('')
    elif 'tourney_date' in df.columns:
        df['year'] = pd.to_datetime(df['tourney_date'], errors='coerce').dt.year.fillna('')
    else:
        df['year'] = ''
    
    # Convert to string for display
    df['year'] = df['year'].astype(str)
    # Replace string representations of NaN/None with empty string
    df['year'] = df['year'].replace('nan', '').replace('None', '')
    
    return df[['year', 'tourney_name', 'round', 'opponent', 'result']].values

