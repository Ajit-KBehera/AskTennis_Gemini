"""
Serve statistics calculation functions.

This module provides reusable functions for calculating serve statistics
from match data. These functions can be used by charts, tables, and other
analysis tools.
"""

import pandas as pd
import numpy as np

# Import utility function from utils
from utils.df_utils import add_player_match_columns


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


def _calculate_player_serve_stats(df):
    """
    Calculate player serve statistics for each match in the dataframe.
    
    Calculates:
    - 1st Serve % (player_1stIn)
    - 1st Serve Won % (player_1stWon)
    - 2nd Serve Won % (player_2ndWon)
    - Ace Rate (player_ace_rate)
    - Double Fault Rate (player_df_rate)
    - Break Points Faced (player_bpFaced)
    - Break Points Saved (player_bpSaved)
    - Break Point Save % (player_bpSavePct)
    
    Args:
        df: DataFrame containing match data with 'is_winner' column
        
    Returns:
        DataFrame: DataFrame with added player serve statistics columns
    """
    # Calculate 1st Serve %
    df['player_1stIn'] = np.where(
        df['is_winner'],
        np.where(df['w_svpt'] > 0, df['w_1stIn'] / df['w_svpt'] * 100, np.nan),
        np.where(df['l_svpt'] > 0, df['l_1stIn'] / df['l_svpt'] * 100, np.nan)
    )
    
    # Calculate 1st Serve Won %
    df['player_1stWon'] = np.where(
        df['is_winner'],
        np.where((df['w_svpt'] > 0) & (df['w_1stIn'] > 0),
                 df['w_1stWon'] / df['w_1stIn'] * 100, np.nan),
        np.where((df['l_svpt'] > 0) & (df['l_1stIn'] > 0),
                 df['l_1stWon'] / df['l_1stIn'] * 100, np.nan)
    )
    
    # Calculate 2nd Serve Won %
    # 2nd serve points attempted = total serve points - 1st serves in
    second_serve_attempted = np.where(
        df['is_winner'],
        df['w_svpt'] - df['w_1stIn'],
        df['l_svpt'] - df['l_1stIn']
    )
    
    df['player_2ndWon'] = np.where(
        df['is_winner'],
        np.where(second_serve_attempted > 0,
                 df['w_2ndWon'] / second_serve_attempted * 100, np.nan),
        np.where(second_serve_attempted > 0,
                 df['l_2ndWon'] / second_serve_attempted * 100, np.nan)
    )
    
    # Calculate Ace Rate (aces per total serve points)
    player_aces = np.where(df['is_winner'], df['w_ace'], df['l_ace'])
    player_serve_points = np.where(df['is_winner'], df['w_svpt'], df['l_svpt'])
    # Use np.divide with where to avoid division by zero warnings
    df['player_ace_rate'] = np.divide(player_aces, player_serve_points, out=np.full_like(player_aces, np.nan, dtype=float), where=player_serve_points > 0) * 100
    
    # Calculate Double Fault Rate (double faults per total serve points)
    player_double_faults = np.where(df['is_winner'], df['w_df'], df['l_df'])
    df['player_df_rate'] = np.divide(player_double_faults, player_serve_points, out=np.full_like(player_double_faults, np.nan, dtype=float), where=player_serve_points > 0) * 100
    
    # Calculate Break Points Faced (when serving)
    df['player_bpFaced'] = np.where(
        df['is_winner'],
        df['w_bpFaced'],
        df['l_bpFaced']
    )
    
    # Calculate Break Points Saved (when serving)
    df['player_bpSaved'] = np.where(
        df['is_winner'],
        df['w_bpSaved'],
        df['l_bpSaved']
    )
    
    # Calculate Break Point Save % (when serving)
    df['player_bpSavePct'] = np.where(
        df['is_winner'],
        np.where(df['w_bpFaced'] > 0, df['w_bpSaved'] / df['w_bpFaced'] * 100, np.nan),
        np.where(df['l_bpFaced'] > 0, df['l_bpSaved'] / df['l_bpFaced'] * 100, np.nan)
    )
    
    return df


def _calculate_opponent_serve_stats(df):
    """
    Calculate opponent serve statistics for each match in the dataframe.
    
    Opponent stats are the opposite of player stats:
    - If player was winner, opponent was loser (use l_* columns)
    - If player was loser, opponent was winner (use w_* columns)
    
    Args:
        df: DataFrame containing match data with 'is_winner' column
        
    Returns:
        DataFrame: DataFrame with added opponent serve statistics columns
    """
    # Calculate Opponent 1st Serve %
    df['opponent_1stIn'] = np.where(
        ~df['is_winner'],
        np.where(df['w_svpt'] > 0, df['w_1stIn'] / df['w_svpt'] * 100, np.nan),
        np.where(df['l_svpt'] > 0, df['l_1stIn'] / df['l_svpt'] * 100, np.nan)
    )
    
    # Calculate Opponent 1st Serve Won %
    df['opponent_1stWon'] = np.where(
        ~df['is_winner'],
        np.where((df['w_svpt'] > 0) & (df['w_1stIn'] > 0),
                 df['w_1stWon'] / df['w_1stIn'] * 100, np.nan),
        np.where((df['l_svpt'] > 0) & (df['l_1stIn'] > 0),
                 df['l_1stWon'] / df['l_1stIn'] * 100, np.nan)
    )
    
    # Calculate Opponent 2nd Serve Won %
    opponent_second_serve_attempted = np.where(
        ~df['is_winner'],
        df['w_svpt'] - df['w_1stIn'],
        df['l_svpt'] - df['l_1stIn']
    )
    
    df['opponent_2ndWon'] = np.where(
        ~df['is_winner'],
        np.where(opponent_second_serve_attempted > 0,
                 df['w_2ndWon'] / opponent_second_serve_attempted * 100, np.nan),
        np.where(opponent_second_serve_attempted > 0,
                 df['l_2ndWon'] / opponent_second_serve_attempted * 100, np.nan)
    )
    
    # Calculate Opponent Ace Rate (aces per total serve points)
    opponent_aces = np.where(~df['is_winner'], df['w_ace'], df['l_ace'])
    opponent_serve_points = np.where(~df['is_winner'], df['w_svpt'], df['l_svpt'])
    # Use np.divide with where to avoid division by zero warnings
    df['opponent_ace_rate'] = np.divide(opponent_aces, opponent_serve_points, out=np.full_like(opponent_aces, np.nan, dtype=float), where=opponent_serve_points > 0) * 100
    
    # Calculate Opponent Double Fault Rate (double faults per total serve points)
    opponent_double_faults = np.where(~df['is_winner'], df['w_df'], df['l_df'])
    df['opponent_df_rate'] = np.divide(opponent_double_faults, opponent_serve_points, out=np.full_like(opponent_double_faults, np.nan, dtype=float), where=opponent_serve_points > 0) * 100
    
    return df


def calculate_match_serve_stats(df):
    """
    Calculate serve statistics for each match in the dataframe.
    
    Args:
        player_df: DataFrame containing match data for the player
        player_name: Name of the player
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        DataFrame: Original dataframe with added columns for serve statistics
    """
    df = df.copy()
    
    # Calculate player serve statistics
    df = _calculate_player_serve_stats(df)
    
    # Calculate opponent serve statistics
    df = _calculate_opponent_serve_stats(df)
    
    return df


def calculate_aggregated_player_serve_stats(df, player_name=None, case_sensitive=False):
    """
    Calculate aggregated player serve statistics across all matches.
    
    Args:
        df: DataFrame containing match data. If stats columns already exist
                   (player_1stIn, player_1stWon, etc.), they will be used directly.
                   Otherwise, player_name must be provided to calculate them.
        player_name: Name of the player (optional if stats columns already exist)
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        dict: Dictionary containing aggregated player serve statistics
    """
    # Check if stats columns already exist
    required_stats_columns = ['player_1stIn', 'player_1stWon', 'player_2ndWon', 
                               'player_ace_rate', 'player_df_rate']
    
    if all(col in df.columns for col in required_stats_columns):
        # Stats already calculated, use them directly
        df_with_stats = df
    else:
        # Calculate match-level stats
        if player_name is None:
            raise ValueError("player_name is required when stats columns are not present in the DataFrame")
        # Pre-calculate is_winner, opponent, result columns before calling calculate_match_serve_stats
        df = add_player_match_columns(df, player_name, case_sensitive)
        df_with_stats = calculate_match_serve_stats(df)
    
    # Calculate averages across all matches (excluding NaN values)
    stats = {
        '1st Serve %': np.nanmean(df_with_stats['player_1stIn']),
        '1st Serve Won %': np.nanmean(df_with_stats['player_1stWon']),
        '2nd Serve Won %': np.nanmean(df_with_stats['player_2ndWon']),
        'Ace Rate': np.nanmean(df_with_stats['player_ace_rate']),
        'Double Fault Rate': np.nanmean(df_with_stats['player_df_rate'])
    }
    
    return stats


def calculate_aggregated_opponent_serve_stats(df, opponent_name=None):
    """
    Calculate aggregated opponent serve statistics across all matches.
    
    Handles "All Opponents" case by checking if multiple opponents exist.
    Aggregation is only meaningful when filtering by a specific opponent.
    
    Args:
        df: DataFrame containing match data with opponent stats columns already calculated
            (opponent_1stIn, opponent_1stWon, etc.)
        opponent_name: Optional opponent name. If provided, only aggregates matches vs this opponent.
                      If None, checks if single opponent exists in data.
        
    Returns:
        dict: Dictionary containing aggregated opponent serve statistics, or None if:
              - Multiple opponents exist and no specific opponent_name provided
              - Specified opponent_name not found in data
              - Required opponent stats columns are missing
    """
    # Check if opponent stats columns exist
    required_stats_columns = ['opponent_1stIn', 'opponent_1stWon', 'opponent_2ndWon', 
                               'opponent_ace_rate', 'opponent_df_rate', 'opponent']
    
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
        '1st Serve %': np.nanmean(df_filtered['opponent_1stIn']),
        '1st Serve Won %': np.nanmean(df_filtered['opponent_1stWon']),
        '2nd Serve Won %': np.nanmean(df_filtered['opponent_2ndWon']),
        'Ace Rate': np.nanmean(df_filtered['opponent_ace_rate']),
        'Double Fault Rate': np.nanmean(df_filtered['opponent_df_rate'])
    }
    
    return stats

