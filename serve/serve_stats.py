"""
Serve statistics calculation functions.

This module provides reusable functions for calculating serve statistics
from match data. These functions can be used by charts, tables, and other
analysis tools.
"""

import pandas as pd
import numpy as np


def calculate_match_serve_stats(player_df, player_name, case_sensitive=False):
    """
    Calculate serve statistics for each match in the dataframe.
    
    Args:
        player_df: DataFrame containing match data for the player
        player_name: Name of the player
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        DataFrame: Original dataframe with added columns for serve statistics
    """
    df = player_df.copy()
    
    # Determine if player was winner or loser for each match
    if case_sensitive:
        is_winner = df['winner_name'] == player_name
    else:
        is_winner = df['winner_name'].str.lower() == player_name.lower()
    
    # Calculate 1st Serve %
    df['player_1stIn'] = np.where(
        is_winner,
        np.where(df['w_svpt'] > 0, df['w_1stIn'] / df['w_svpt'] * 100, np.nan),
        np.where(df['l_svpt'] > 0, df['l_1stIn'] / df['l_svpt'] * 100, np.nan)
    )
    
    # Calculate 1st Serve Won %
    df['player_1stWon'] = np.where(
        is_winner,
        np.where((df['w_svpt'] > 0) & (df['w_1stIn'] > 0),
                 df['w_1stWon'] / df['w_1stIn'] * 100, np.nan),
        np.where((df['l_svpt'] > 0) & (df['l_1stIn'] > 0),
                 df['l_1stWon'] / df['l_1stIn'] * 100, np.nan)
    )
    
    # Calculate 2nd Serve Won %
    # 2nd serve points attempted = total serve points - 1st serves in
    second_serve_attempted = np.where(
        is_winner,
        df['w_svpt'] - df['w_1stIn'],
        df['l_svpt'] - df['l_1stIn']
    )
    
    df['player_2ndWon'] = np.where(
        is_winner,
        np.where(second_serve_attempted > 0,
                 df['w_2ndWon'] / second_serve_attempted * 100, np.nan),
        np.where(second_serve_attempted > 0,
                 df['l_2ndWon'] / second_serve_attempted * 100, np.nan)
    )
    
    # Calculate Ace Rate (aces per serve game)
    aces = np.where(is_winner, df['w_ace'], df['l_ace'])
    serve_games = np.where(is_winner, df['w_SvGms'], df['l_SvGms'])
    df['player_ace_rate'] = np.where(serve_games > 0, aces / serve_games * 100, np.nan)
    
    # Calculate Double Fault Rate (double faults per serve game)
    double_faults = np.where(is_winner, df['w_df'], df['l_df'])
    df['player_df_rate'] = np.where(serve_games > 0, double_faults / serve_games * 100, np.nan)
    
    # Calculate opponent and result for hover tooltips
    df['opponent'] = np.where(
        is_winner,
        df['loser_name'],
        df['winner_name']
    )
    df['result'] = np.where(is_winner, 'W', 'L')
    
    return df


def calculate_aggregated_serve_stats(player_df, player_name, case_sensitive=False):
    """
    Calculate aggregated serve statistics across all matches.
    
    Args:
        player_df: DataFrame containing match data for the player
        player_name: Name of the player
        case_sensitive: Whether to use case-sensitive name matching (default: False)
        
    Returns:
        dict: Dictionary containing aggregated serve statistics
    """
    # Calculate match-level stats
    df_with_stats = calculate_match_serve_stats(player_df, player_name, case_sensitive)
    
    # Calculate averages across all matches (excluding NaN values)
    stats = {
        '1st Serve %': np.nanmean(df_with_stats['player_1stIn']),
        '1st Serve Won %': np.nanmean(df_with_stats['player_1stWon']),
        '2nd Serve Won %': np.nanmean(df_with_stats['player_2ndWon']),
        'Ace Rate': np.nanmean(df_with_stats['player_ace_rate']),
        'Double Fault Rate': np.nanmean(df_with_stats['player_df_rate'])
    }
    
    return stats


def get_match_hover_data(player_df, player_name, case_sensitive=False):
    """
    Get hover data for match tooltips (tournament, round, opponent, result).
    
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
    
    return df[['tourney_name', 'round', 'opponent', 'result']].values

