"""
Data loading utilities for serve chart scripts.

This module provides data loading functionality without importing chart functions,
avoiding circular import issues.
"""

import pandas as pd
import sqlite3
import sys
import os


def _sanitize_string(value):
    """Sanitize string input by trimming whitespace and handling empty strings.
    
    Args:
        value: String value to sanitize
        
    Returns:
        Sanitized string or None if value is empty/invalid
    """
    if not value or not isinstance(value, str):
        return None
    sanitized = value.strip()
    return sanitized if sanitized else None


def load_player_matches(player_name, year=None, opponent=None, tournament=None, surfaces=None, db_path="tennis_data_OE_Singles_Rankings_Players.db"):
    """
    Load match data for a specific player from the database with optional filters.
    
    Args:
        player_name: Name of the player (REQUIRED - cannot be None or "All Players")
        year: Optional year(s) to filter matches. Can be:
            - None or "All Years": All years (career view)
            - int or str: Single year (e.g., 2024 or "2024")
            - list: Multiple years (e.g., [2022, 2023, 2024])
        opponent: Optional opponent name to filter matches (can be None or "All Opponents")
        tournament: Optional tournament name to filter matches (can be None or "All Tournaments")
        surfaces: Optional list of surfaces to filter matches (e.g., ['Hard', 'Clay'])
        db_path: Path to the SQLite database file
        
    Returns:
        pandas.DataFrame: DataFrame containing match data, sorted by date and match number
        
    Raises:
        SystemExit: If player_name is None/empty/"All Players" or if no matches are found
    """
    # Constants for filter options
    ALL_PLAYERS = "All Players"
    ALL_OPPONENTS = "All Opponents"
    ALL_TOURNAMENTS = "All Tournaments"
    ALL_YEARS = "All Years"
    MIN_YEAR = 1900
    MAX_YEAR = 2100
    
    # Sanitize inputs
    player_name = _sanitize_string(player_name)
    opponent = _sanitize_string(opponent)
    tournament = _sanitize_string(tournament)
    
    # Handle year: can be None, int, str, or list
    year_list = None
    if year is None:
        year = None
    elif isinstance(year, list):
        # Multiple years provided
        year_list = [int(y) for y in year if y is not None]
        year = None  # Will use year_list for filtering
    elif isinstance(year, (int, str)):
        # Single year - convert to string for comparison
        year = _sanitize_string(str(year))
    else:
        year = None
    
    # Player is REQUIRED - cannot be None or "All Players"
    if not player_name or player_name == ALL_PLAYERS:
        print(f"Error: Player name is required. Cannot use '{ALL_PLAYERS}' for serve/return visualizations.")
        sys.exit(1)
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    # Player filter (always required)
    where_conditions.append("(winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)")
    params.extend([player_name, player_name])
    
    # Opponent filter (optional)
    if opponent and opponent != ALL_OPPONENTS:
        # When both player and opponent are specified, match where both are involved
        # Replace the player-only condition with a combined condition
        where_conditions.pop()  # Remove the player-only condition
        params = params[:-2]  # Remove player params
        where_conditions.append("((winner_name COLLATE NOCASE = ? AND loser_name COLLATE NOCASE = ?) OR (winner_name COLLATE NOCASE = ? AND loser_name COLLATE NOCASE = ?))")
        params.extend([player_name, opponent, opponent, player_name])
    
    # Tournament filter (optional)
    if tournament and tournament != ALL_TOURNAMENTS:
        where_conditions.append("tourney_name COLLATE NOCASE = ?")
        params.append(tournament)
    
    # Year filter (optional)
    # Only add year filter if year is provided and not "All Years"
    # If year is None or "All Years", no year filter is added (all years included)
    if year_list:
        # Multiple years: use IN clause
        valid_years = [y for y in year_list if MIN_YEAR <= y <= MAX_YEAR]
        if valid_years:
            placeholders = ','.join(['?' for _ in valid_years])
            where_conditions.append(f"event_year IN ({placeholders})")
            params.extend(valid_years)
        else:
            print(f"Warning: No valid years in range. Skipping year filter.")
    elif year and year != ALL_YEARS:
        try:
            year_int = int(year)
            # Validate reasonable year range
            if MIN_YEAR <= year_int <= MAX_YEAR:
                where_conditions.append("event_year = ?")
                params.append(year_int)
            else:
                print(f"Warning: Invalid year range: {year_int}. Skipping year filter.")
        except (ValueError, TypeError):
            print(f"Warning: Invalid year format: {year}. Skipping year filter.")
    
    # Surface filter (optional)
    if surfaces:
        # Filter and validate surfaces: remove empty strings, None values, and strip whitespace
        valid_surfaces = [
            s.strip() for s in surfaces 
            if s and isinstance(s, str) and s.strip()
        ]
        
        if valid_surfaces:
            # Handle multiple surface filtering
            placeholders = ','.join(['?' for _ in valid_surfaces])
            where_conditions.append(f"surface IN ({placeholders})")
            params.extend(valid_surfaces)
        elif len(surfaces) > 0:
            # User provided surfaces but all were invalid
            print(f"Warning: Invalid surface values provided. Skipping surface filter.")
    
    # Build final query
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    sql_query = f"SELECT * FROM matches WHERE {where_clause} ORDER BY tourney_date ASC, match_num ASC"
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            sql_query, 
            conn, 
            params=params
        ).sort_values(by=['tourney_date', 'match_num']).reset_index(drop=True)
    
    # Check if dataframe is empty
    if df.empty:
        filter_info = f"{player_name}"
        if year_list:
            if len(year_list) == 1:
                filter_info += f" in {year_list[0]}"
            else:
                filter_info += f" in {year_list}"
        elif year and year != ALL_YEARS:
            filter_info += f" in {year}"
        if opponent and opponent != ALL_OPPONENTS:
            filter_info += f" vs {opponent}"
        if tournament and tournament != ALL_TOURNAMENTS:
            filter_info += f" at {tournament}"
        if surfaces:
            filter_info += f" on {', '.join(surfaces)}"
        print(f"No matches found for {filter_info}")
        sys.exit(1)
    
    return df

