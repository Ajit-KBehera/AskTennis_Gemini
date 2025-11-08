"""
Common utilities for serve chart scripts.

This module provides shared functionality for loading serve match data,
eliminating redundant code across different serve chart visualization scripts.
"""

import pandas as pd
import sqlite3
import sys
import os


def load_player_matches(player_name, year, db_path="tennis_data_OE_Singles_Rankings_Players.db"):
    """
    Load match data for a specific player and year from the database.
    
    Args:
        player_name: Name of the player
        year: Year to filter matches
        db_path: Path to the SQLite database file
        
    Returns:
        pandas.DataFrame: DataFrame containing match data, sorted by date and match number
        
    Raises:
        SystemExit: If no matches are found for the player/year
    """
    sql_query = "SELECT * FROM matches WHERE event_year = ? AND (winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)"
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            sql_query, 
            conn, 
            params=(year, player_name, player_name)
        ).sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
    # Check if dataframe is empty
    if df.empty:
        print(f"No matches found for {player_name} in {year}")
        sys.exit(1)
    
    return df