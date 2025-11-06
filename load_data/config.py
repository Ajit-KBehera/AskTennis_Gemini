"""
Configuration settings for tennis data loading.

This module contains all configuration constants and data loading switches
that control which data sources are loaded into the database.
"""

import os

# --- Project Configuration ---
# Get the project root directory (parent of load_data)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIRS = [os.path.join(PROJECT_ROOT, "data/tennis_atp"), os.path.join(PROJECT_ROOT, "data/tennis_wta")]
YEARS_MAIN_TOUR = list(range(1968, 2026))  # Years for main tour matches (Open Era: 1968-2024)
                                              # Note: Amateur matches (1877-1967) are loaded separately from atp_matches_amateur.csv
DB_FILE = os.path.join(PROJECT_ROOT, "tennis_data_OE_Singles_Rankings_Players.db")

# --- Data Loading Switches ---
# Control which data sources are loaded into the database
# Set to True to load, False to skip

# Players Data Switches
LOAD_ATP_PLAYERS = True              # ATP players data
LOAD_WTA_PLAYERS = True              # WTA players data

# Rankings Data Switches
LOAD_ATP_RANKINGS = True             # ATP rankings data
LOAD_WTA_RANKINGS = True             # WTA rankings data

# Matches Data Switches
LOAD_MAIN_TOUR_MATCHES = True      # Main tour ATP/WTA matches (1968-2024)
LOAD_AMATEUR_MATCHES = False        # Amateur tennis data (1877-1967)
LOAD_ATP_QUALIFYING = True          # ATP Qualifying matches
LOAD_ATP_CHALLENGER = True          # ATP Challenger matches
LOAD_ATP_CHALLENGER_QUAL = True     # ATP Challenger Qualifying matches
LOAD_ATP_FUTURES = True             # ATP Futures matches
LOAD_WTA_QUALIFYING = True          # WTA Qualifying matches
LOAD_WTA_ITF = True                # WTA ITF matches
LOAD_DAVIS_CUP = True              # Davis Cup matches
LOAD_FED_CUP = True                # Fed Cup (BJK Cup) matches

# Doubles Data Switches
LOAD_DOUBLES_MATCHES = False         # ATP Doubles matches

# --- Database Creation Switches ---
# Control which database structures are created
# Set to True to create, False to skip

# Table Creation Switches
CREATE_TABLE_MATCHES = True          # Create matches table
CREATE_TABLE_PLAYERS = True          # Create players table
CREATE_TABLE_RANKINGS = True         # Create rankings table
CREATE_TABLE_DOUBLES = False          # Create doubles_matches table

# Index Creation Switches
CREATE_INDEXES_MATCHES = True       # Create indexes for matches table
CREATE_INDEXES_PLAYERS = True       # Create indexes for players table
CREATE_INDEXES_RANKINGS = True      # Create indexes for rankings table
CREATE_INDEXES_DOUBLES = False      # Create indexes for doubles_matches table

# View Creation Switches
CREATE_VIEW_WINNER_INFO = True      # Create matches_with_winner_info view
CREATE_VIEW_LOSER_INFO = True       # Create matches_with_loser_info view
CREATE_VIEW_FULL_INFO = True        # Create matches_with_full_info view
CREATE_VIEW_MATCHES_RANKINGS = True # Create matches_with_rankings view
CREATE_VIEW_RANKINGS_HISTORY = True # Create player_rankings_history view

