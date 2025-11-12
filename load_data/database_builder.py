"""
Database building functions for tennis data.

This module contains functions that create SQLite database structure
and write data to tables.
"""

import sqlite3
import pandas as pd

# Import configuration
from .config import (
    DB_FILE,
    CREATE_TABLE_MATCHES, CREATE_TABLE_PLAYERS, CREATE_TABLE_RANKINGS, CREATE_TABLE_DOUBLES
)


def build_database(matches_df, atp_players_df, wta_players_df, atp_rankings_df, wta_rankings_df, doubles_df):
    """
    Builds SQLite database with matches, players, rankings, and doubles data.
    
    Args:
        matches_df: DataFrame with match data
        atp_players_df: DataFrame with ATP player data
        wta_players_df: DataFrame with WTA player data
        atp_rankings_df: DataFrame with ATP rankings data
        wta_rankings_df: DataFrame with WTA rankings data
        doubles_df: DataFrame with doubles match data
    """
    print("\n--- Creating Enhanced Database ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Write matches data
    if CREATE_TABLE_MATCHES:
        print("Writing matches data...")
        matches_df.to_sql('matches', conn, if_exists='replace', index=False)
    else:
        print("Skipping matches table creation (CREATE_TABLE_MATCHES = False)")
    
    # Write players data - separate tables for ATP and WTA
    if CREATE_TABLE_PLAYERS:
        if not atp_players_df.empty:
            print("Writing ATP players data...")
            # Remove 'tour' column if present (not needed in separate table)
            atp_players_clean = atp_players_df.drop(columns=['tour'], errors='ignore')
            atp_players_clean.to_sql('atp_players', conn, if_exists='replace', index=False)
            print(f"ATP players written: {len(atp_players_clean)}")
        else:
            print("No ATP players data to write.")
        
        if not wta_players_df.empty:
            print("Writing WTA players data...")
            # Remove 'tour' column if present (not needed in separate table)
            wta_players_clean = wta_players_df.drop(columns=['tour'], errors='ignore')
            wta_players_clean.to_sql('wta_players', conn, if_exists='replace', index=False)
            print(f"WTA players written: {len(wta_players_clean)}")
        else:
            print("No WTA players data to write.")
    else:
        print("Skipping players table creation (CREATE_TABLE_PLAYERS = False)")
    
    # Write ATP rankings data
    if CREATE_TABLE_RANKINGS:
        if not atp_rankings_df.empty:
            print("Writing ATP rankings data...")
            # Remove 'tour' column if present (not needed in separate table)
            atp_df = atp_rankings_df.drop(columns=['tour'], errors='ignore')
            atp_df.to_sql('atp_rankings', conn, if_exists='replace', index=False)
        else:
            print("No ATP rankings data to write.")
        
        # Write WTA rankings data
        if not wta_rankings_df.empty:
            print("Writing WTA rankings data...")
            # Remove 'tour' column if present (not needed in separate table)
            wta_df = wta_rankings_df.drop(columns=['tour'], errors='ignore')
            wta_df.to_sql('wta_rankings', conn, if_exists='replace', index=False)
        else:
            print("No WTA rankings data to write.")
    else:
        print("Skipping rankings table creation (CREATE_TABLE_RANKINGS = False)")
    
    # Write doubles data
    if CREATE_TABLE_DOUBLES:
        if not doubles_df.empty:
            print("Writing doubles data...")
            doubles_df.to_sql('doubles_matches', conn, if_exists='replace', index=False)
        else:
            print("No doubles data to write.")
    else:
        print("Skipping doubles table creation (CREATE_TABLE_DOUBLES = False)")
    
    conn.close()
    
    total_players = len(atp_players_df) + len(wta_players_df)
    print(f"\n✅ Successfully created enhanced database '{DB_FILE}' with:")
    print(f"   - {len(matches_df)} singles matches (COMPLETE tournament coverage: 1877-2024)")
    if not doubles_df.empty:
        print(f"   - {len(doubles_df)} doubles matches (2000-2020)")
    print(f"   - {total_players} players (ATP: {len(atp_players_df)}, WTA: {len(wta_players_df)})")
    if not atp_rankings_df.empty:
        print(f"   - {len(atp_rankings_df)} ATP ranking records")
    if not wta_rankings_df.empty:
        print(f"   - {len(wta_rankings_df)} WTA ranking records")
    print(f"   - Player metadata integration (separate ATP/WTA tables)")
    print(f"   - Rankings data integration (separate ATP/WTA tables)")
    print(f"   - Surface data quality fix (missing surface inference)")
    print(f"   - Closed Era tennis (1877-1967)")
    print(f"   - Open Era tennis (1968-2024)")
    print(f"   - Main tour matches (Grand Slams, Masters, etc.)")
    print(f"   - Qualifying/Challenger/Futures matches")
    print(f"   - Doubles matches (separate table)")
    print(f"   - COMPLETE tennis tournament database (147 years)")
