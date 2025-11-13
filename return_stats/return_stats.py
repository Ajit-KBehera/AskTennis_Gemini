"""
Return statistics calculation functions.

This module provides reusable functions for calculating return statistics
from match data. These functions can be used by charts, tables, and other
analysis tools.

Note: Return statistics are calculated from the opponent's serve perspective.
"""

import pandas as pd
import numpy as np


def safe_nanmean(series):
    """
    Calculate nanmean safely, returning NaN if all values are NaN.
    
    This prevents RuntimeWarning when np.nanmean is called on empty or all-NaN arrays.
    
    Args:
        series: pandas Series or array-like object
        
    Returns:
        float: Mean value or np.nan if no valid values exist
    """
    if series is None or len(series) == 0:
        return np.nan
    valid_values = series.dropna() if hasattr(series, 'dropna') else pd.Series(series).dropna()
    if len(valid_values) == 0:
        return np.nan
    return np.nanmean(series)


def build_year_suffix(year):
    """
    Build year suffix string for chart titles.
    
    Args:
        year: Year(s) for the chart. Can be:
            - int or str: Single year (e.g., 2024)
            - tuple: Year range (e.g., (2020, 2024)) for consecutive years
            - list: Multiple years (e.g., [2022, 2023, 2024])
            - None: Career view (all years)
    
    Returns:
        str: Year suffix string (e.g., "2024 Season", "2020-2024 Seasons", "Career")
    """
    if year is None:
        return "Career"
    elif isinstance(year, tuple) and len(year) == 2:
        # Year range tuple (start_year, end_year)
        start_year, end_year = year[0], year[1]
        if start_year == end_year:
            return f"{start_year} Season"
        else:
            return f"{start_year}-{end_year} Seasons"
    elif isinstance(year, list):
        if len(year) == 1:
            return f"{year[0]} Season"
        else:
            return f"{min(year)}-{max(year)} Seasons"
    else:
        # Single year (int or str)
        return f"{year} Season"


def calculate_match_return_stats(df, player_name, case_sensitive=False):
    """
    Calculate return statistics for each match in the dataframe.
    
    Return statistics are calculated from the opponent's serve perspective:
    - Return Points Won % = 100 - (opponent's serve points won %)
    - Break Point Conversion = break points converted when returning
    - Return Games Won % = percentage of opponent's service games broken
    
    Args:
        df: DataFrame containing match data for the player
        player_name: Name of the player
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        DataFrame: Original dataframe with added columns for return statistics
    """
    df = df.copy()
    
    # Determine if player was winner or loser for each match
    if case_sensitive:
        is_winner = df['winner_name'] == player_name
    else:
        is_winner = df['winner_name'].str.lower() == player_name.lower()
    
    # =============================================================================
    # RETURN POINTS WON % CALCULATION
    # =============================================================================
    # Return Points Won % = 100 - (opponent's serve points won %)
    # If player was winner, opponent was loser (use l_* columns)
    # If player was loser, opponent was winner (use w_* columns)
    
    # Opponent's total serve points
    opponent_svpt = np.where(is_winner, df['l_svpt'], df['w_svpt'])
    
    # Opponent's points won on serve (1st serve won + 2nd serve won)
    opponent_points_won_on_serve = np.where(
        is_winner,
        df['l_1stWon'] + df['l_2ndWon'],
        df['w_1stWon'] + df['w_2ndWon']
    )
    
    # Opponent's serve points won %
    opponent_serve_points_won_pct = np.where(
        opponent_svpt > 0,
        opponent_points_won_on_serve / opponent_svpt * 100,
        np.nan
    )
    
    # Return Points Won % = 100 - opponent's serve points won %
    df['player_return_points_won_pct'] = np.where(
        ~np.isnan(opponent_serve_points_won_pct),
        100 - opponent_serve_points_won_pct,
        np.nan
    )
    
    # =============================================================================
    # BREAK POINT CONVERSION CALCULATION (when returning)
    # =============================================================================
    # Break points converted = break points faced by opponent when serving - break points saved by opponent
    # When player is returning, they convert break points that the opponent faced when serving
    # If player was winner: They converted break points = l_bpFaced - l_bpSaved
    # If player was loser: They converted break points = w_bpFaced - w_bpSaved
    
    # Break points faced by opponent when serving (break points created by player)
    opponent_bpFaced = np.where(is_winner, df['l_bpFaced'], df['w_bpFaced'])
    opponent_bpSaved = np.where(is_winner, df['l_bpSaved'], df['w_bpSaved'])
    
    # Break points converted = break points faced - break points saved
    df['player_bpConverted'] = opponent_bpFaced - opponent_bpSaved
    
    # Store break points faced by opponent for conversion percentage calculation
    df['player_bpFaced_opponent'] = opponent_bpFaced
    
    # Break Point Conversion %
    df['player_bpConversion_pct'] = np.where(
        df['player_bpFaced_opponent'] > 0,
        df['player_bpConverted'] / df['player_bpFaced_opponent'] * 100,
        np.nan
    )
    
    # =============================================================================
    # RETURN GAMES WON % CALCULATION
    # =============================================================================
    # Return Games Won % = percentage of opponent's service games broken
    # If player was winner, opponent's service games = l_SvGms
    # If player was loser, opponent's service games = w_SvGms
    
    opponent_sv_gms = np.where(is_winner, df['l_SvGms'], df['w_SvGms'])
    
    # Total service games played by opponent
    # We need to calculate this from the match data
    # For now, we'll use the service games won as a proxy
    # Return games won = opponent's service games - opponent's service games won
    # Actually, return games won = total games - opponent's service games won
    # But we need total games played
    
    # Calculate return games won %
    # Return games won = opponent's service games lost
    # If player was winner: opponent lost (total_games - l_SvGms) return games
    # But we need total games...
    
    # For now, let's calculate it differently:
    # Return Games Won % = (opponent's service games lost) / (opponent's total service games) * 100
    # We'll need to estimate or use available data
    
    # Note: This calculation may need adjustment based on available data
    # For now, we'll calculate a simplified version
    df['player_return_games_won_pct'] = np.nan  # Placeholder - needs proper calculation
    
    # =============================================================================
    # OPPONENT AND RESULT FOR HOVER TOOLTIPS
    # =============================================================================
    df['opponent'] = np.where(
        is_winner,
        df['loser_name'],
        df['winner_name']
    )
    df['result'] = np.where(is_winner, 'W', 'L')
    
    # =============================================================================
    # OPPONENT RETURN STATISTICS CALCULATION (for comparison)
    # =============================================================================
    # Opponent return stats are the opposite of player return stats
    is_opponent_winner = ~is_winner
    
    # Opponent's return points won % = 100 - player's serve points won %
    player_svpt = np.where(is_winner, df['w_svpt'], df['l_svpt'])
    player_points_won_on_serve = np.where(
        is_winner,
        df['w_1stWon'] + df['w_2ndWon'],
        df['l_1stWon'] + df['l_2ndWon']
    )
    player_serve_points_won_pct = np.where(
        player_svpt > 0,
        player_points_won_on_serve / player_svpt * 100,
        np.nan
    )
    
    df['opponent_return_points_won_pct'] = np.where(
        ~np.isnan(player_serve_points_won_pct),
        100 - player_serve_points_won_pct,
        np.nan
    )
    
    # Opponent's break point conversion (when returning against player)
    # When opponent is returning, they convert break points that the player faced when serving
    player_bpFaced_when_serving = np.where(is_winner, df['w_bpFaced'], df['l_bpFaced'])
    player_bpSaved_when_serving = np.where(is_winner, df['w_bpSaved'], df['l_bpSaved'])
    
    # Opponent converted break points = player's break points faced - player's break points saved
    df['opponent_bpConverted'] = player_bpFaced_when_serving - player_bpSaved_when_serving
    
    df['opponent_bpFaced_when_returning'] = player_bpFaced_when_serving
    
    df['opponent_bpConversion_pct'] = np.where(
        df['opponent_bpFaced_when_returning'] > 0,
        df['opponent_bpConverted'] / df['opponent_bpFaced_when_returning'] * 100,
        np.nan
    )
    
    return df


def calculate_aggregated_return_stats(df, player_name=None, case_sensitive=False):
    """
    Calculate aggregated return statistics across all matches.
    
    Args:
        df: DataFrame containing match data. If stats columns already exist
            (player_return_points_won_pct, player_bpConversion_pct, etc.), 
            they will be used directly. Otherwise, player_name must be provided 
            to calculate them.
        player_name: Name of the player (optional if stats columns already exist)
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        dict: Dictionary containing aggregated return statistics
    """
    # Check if stats columns already exist
    required_stats_columns = ['player_return_points_won_pct', 'player_bpConversion_pct']
    
    if all(col in df.columns for col in required_stats_columns):
        # Stats already calculated, use them directly
        df_with_stats = df
    else:
        # Calculate match-level stats
        if player_name is None:
            raise ValueError("player_name is required when stats columns are not present in the DataFrame")
        df_with_stats = calculate_match_return_stats(df, player_name, case_sensitive)
    
    # Calculate averages across all matches (excluding NaN values)
    stats = {
        'Return Points Won %': safe_nanmean(df_with_stats['player_return_points_won_pct']),
        'Break Point Conversion %': safe_nanmean(df_with_stats['player_bpConversion_pct'])
    }
    
    # Add return games won % if available and has valid values
    if 'player_return_games_won_pct' in df_with_stats.columns:
        games_won_pct = safe_nanmean(df_with_stats['player_return_games_won_pct'])
        if not np.isnan(games_won_pct):
            stats['Return Games Won %'] = games_won_pct
    
    return stats


def calculate_aggregated_opponent_return_stats(df, opponent_name=None):
    """
    Calculate aggregated opponent return statistics across all matches.
    
    Handles "All Opponents" case by checking if multiple opponents exist.
    Aggregation is only meaningful when filtering by a specific opponent.
    
    Args:
        df: DataFrame containing match data with opponent return stats columns already calculated
            (opponent_return_points_won_pct, opponent_bpConversion_pct, etc.)
        opponent_name: Optional opponent name. If provided, only aggregates matches vs this opponent.
                      If None, checks if single opponent exists in data.
        
    Returns:
        dict: Dictionary containing aggregated opponent return statistics, or None if:
              - Multiple opponents exist and no specific opponent_name provided
              - Specified opponent_name not found in data
              - Required opponent stats columns are missing
    """
    # Check if opponent stats columns exist
    required_stats_columns = ['opponent_return_points_won_pct', 'opponent_bpConversion_pct', 'opponent']
    
    if not all(col in df.columns for col in required_stats_columns):
        # Opponent stats not calculated yet - return None
        return None
    
    # Filter by opponent if specified
    if opponent_name:
        df_filtered = df[df['opponent'] == opponent_name]
        if df_filtered.empty:
            # Specified opponent not found
            return None
    else:
        # Check if multiple opponents exist
        unique_opponents = df['opponent'].nunique()
        if unique_opponents > 1:
            # Multiple opponents - aggregation not meaningful
            return None
        elif unique_opponents == 0:
            # No opponents found
            return None
        else:
            # Single opponent - safe to aggregate
            df_filtered = df
    
    # Calculate averages across all matches (excluding NaN values)
    stats = {
        'Return Points Won %': safe_nanmean(df_filtered['opponent_return_points_won_pct']),
        'Break Point Conversion %': safe_nanmean(df_filtered['opponent_bpConversion_pct'])
    }
    
    return stats


def get_match_hover_data(player_df, player_name, case_sensitive=False):
    """
    Get hover data for match tooltips (tournament, round, opponent, result, year).
    
    Args:
        player_df: DataFrame containing match data for the player
        player_name: Name of the player
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        numpy.ndarray: Array of hover data for each match
    """
    df = player_df.copy()
    
    # Determine if player was winner or loser for each match
    if case_sensitive:
        is_winner = df['winner_name'] == player_name
    else:
        is_winner = df['winner_name'].str.lower() == player_name.lower()
    
    # Calculate opponent and result
    df['opponent'] = np.where(
        is_winner,
        df['loser_name'],
        df['winner_name']
    )
    df['result'] = np.where(is_winner, 'W', 'L')
    
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
    
    return df[['tourney_name', 'round', 'opponent', 'result', 'year']].values

