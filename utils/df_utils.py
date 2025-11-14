"""
DataFrame utilities for tennis data processing.

This module provides general utilities for manipulating DataFrames containing tennis match data,
usable across serve stats, return stats, and other analysis modules.
"""

import pandas as pd
import numpy as np


def add_player_match_columns(df, player_name, case_sensitive=False):
    """
    Add is_winner, opponent, and result columns to dataframe.
    
    Utility function to add player match columns before calling statistics calculation functions.
    This avoids code duplication and ensures consistency across serve and return stats.
    
    Args:
        df: DataFrame containing match data with 'winner_name' and 'loser_name' columns
        player_name: Name of the player
        case_sensitive: Whether to use case-sensitive name matching (default: False)
    
    Returns:
        DataFrame: DataFrame with added columns: is_winner, opponent, result
    """
    df = df.copy()
    
    # Calculate is_winner boolean Series
    if case_sensitive:
        df['is_winner'] = df['winner_name'] == player_name
    else:
        df['is_winner'] = df['winner_name'].str.lower() == player_name.lower()
    
    # Add opponent column (loser_name if player won, winner_name if player lost)
    df['opponent'] = np.where(
        df['is_winner'],
        df['loser_name'],
        df['winner_name']
    )
    
    # Add result column ('W' if player won, 'L' if player lost)
    df['result'] = np.where(df['is_winner'], 'W', 'L')
    
    return df

