"""
Data loading functions for tennis match data.

This module contains functions that load tennis data from CSV files,
including players, rankings, and matches data.
"""

import pandas as pd
import glob
import os

# Import configuration
from .config import (
    PROJECT_ROOT, DATA_DIRS, YEARS_MAIN_TOUR,
    LOAD_ATP_PLAYERS, LOAD_WTA_PLAYERS,
    LOAD_ATP_RANKINGS, LOAD_WTA_RANKINGS,
    LOAD_MAIN_TOUR_MATCHES, LOAD_AMATEUR_MATCHES,
    LOAD_ATP_QUALIFYING, LOAD_ATP_CHALLENGER, LOAD_ATP_CHALLENGER_QUAL,
    LOAD_ATP_FUTURES, LOAD_WTA_QUALIFYING, LOAD_WTA_ITF
)

# Import utilities
from .utils import ProgressTracker


def load_players_data():
    """
    Loads player information from ATP and WTA player files separately.
    Returns tuple of (atp_players_df, wta_players_df) - enrichment happens in transformers.
    """
    print("--- Loading Player Information ---")
    
    # Load ATP players
    atp_players = pd.DataFrame()
    if LOAD_ATP_PLAYERS:
        atp_players_path = os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_players.csv")
        if os.path.exists(atp_players_path):
            print(f"Reading {atp_players_path}...")
            atp_players = pd.read_csv(atp_players_path, index_col=False)
            # Store source info for later enrichment
            atp_players['_source'] = 'ATP'
            print(f"ATP players loaded: {len(atp_players)}")
        else:
            print(f"Warning: {atp_players_path} not found")
    else:
        print("Skipping ATP players (LOAD_ATP_PLAYERS = False)")
    
    # Load WTA players
    wta_players = pd.DataFrame()
    if LOAD_WTA_PLAYERS:
        wta_players_path = os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_players.csv")
        if os.path.exists(wta_players_path):
            print(f"Reading {wta_players_path}...")
            wta_players = pd.read_csv(wta_players_path, index_col=False)
            # Store source info for later enrichment
            wta_players['_source'] = 'WTA'
            print(f"WTA players loaded: {len(wta_players)}")
        else:
            print(f"Warning: {wta_players_path} not found")
    else:
        print("Skipping WTA players (LOAD_WTA_PLAYERS = False)")
    
    total_players = len(atp_players) + len(wta_players)
    print(f"Total players loaded: {total_players} (ATP: {len(atp_players)}, WTA: {len(wta_players)})")
    return atp_players, wta_players

def load_rankings_data():
    """
    Loads rankings data from ATP and WTA ranking files separately.
    Returns tuple of (atp_rankings_df, wta_rankings_df) - enrichment happens in transformers.
    """
    print("--- Loading Rankings Data ---")
    
    # Define ranking file patterns
    atp_ranking_files = [
        os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_rankings_70s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_rankings_80s.csv"), 
        os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_rankings_90s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_rankings_00s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_rankings_10s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_rankings_20s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_rankings_current.csv"),
    ]
    
    wta_ranking_files = [
        os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_rankings_80s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_rankings_90s.csv"), 
        os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_rankings_00s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_rankings_10s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_rankings_20s.csv"),
        os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_rankings_current.csv")
    ]
    
    # Load ATP rankings
    atp_rankings = []
    if LOAD_ATP_RANKINGS:
        existing_atp_files = [f for f in atp_ranking_files if os.path.exists(f)]
        if existing_atp_files:
            progress = ProgressTracker(len(existing_atp_files), "ATP Rankings Loading")
            for file_path in atp_ranking_files:
                if os.path.exists(file_path):
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    try:
                        df = pd.read_csv(file_path, index_col=False)
                        df['_source_file'] = file_path
                        atp_rankings.append(df)
                        print(f"  Loaded {len(df)} ATP ranking records")
                    except Exception as e:
                        print(f"  Error loading {file_path}: {e}")
        else:
            print("No ATP ranking files found!")
    else:
        print("Skipping ATP rankings (LOAD_ATP_RANKINGS = False)")
    
    # Load WTA rankings
    wta_rankings = []
    if LOAD_WTA_RANKINGS:
        existing_wta_files = [f for f in wta_ranking_files if os.path.exists(f)]
        if existing_wta_files:
            progress = ProgressTracker(len(existing_wta_files), "WTA Rankings Loading")
            for file_path in wta_ranking_files:
                if os.path.exists(file_path):
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    try:
                        df = pd.read_csv(file_path, index_col=False)
                        df['_source_file'] = file_path
                        wta_rankings.append(df)
                        print(f"  Loaded {len(df)} WTA ranking records")
                    except Exception as e:
                        print(f"  Error loading {file_path}: {e}")
        else:
            print("No WTA ranking files found!")
    else:
        print("Skipping WTA rankings (LOAD_WTA_RANKINGS = False)")
    
    # Combine ATP rankings
    atp_rankings_df = pd.DataFrame()
    if atp_rankings:
        atp_rankings_df = pd.concat(atp_rankings, ignore_index=True)
        print(f"Total ATP rankings loaded: {len(atp_rankings_df)}")
    
    # Combine WTA rankings
    wta_rankings_df = pd.DataFrame()
    if wta_rankings:
        wta_rankings_df = pd.concat(wta_rankings, ignore_index=True)
        print(f"Total WTA rankings loaded: {len(wta_rankings_df)}")
    
    return atp_rankings_df, wta_rankings_df

def load_matches_data():
    """
    Loads match data from ATP and WTA files.
    Returns raw DataFrames - enrichment happens in transformers.
    """
    print("--- Loading Match Data ---")
    master_df_list = []
    
    # Load main tour matches (ATP/WTA year files)
    if LOAD_MAIN_TOUR_MATCHES:
        # Calculate total files to process
        total_files = 0
        for data_dir in DATA_DIRS:
            for year in YEARS_MAIN_TOUR:
                file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
                if glob.glob(file_pattern):
                    total_files += 1
        
        # Initialize progress tracker for match files
        progress = ProgressTracker(total_files, "Match Loading")
        
        # Loop through each data directory (ATP and WTA)
        for data_dir in DATA_DIRS:
            print(f"\n--- Processing directory: {data_dir} ---")
            
            # Determine tour based on directory
            if 'atp' in data_dir.lower():
                tour = 'ATP'
            elif 'wta' in data_dir.lower():
                tour = 'WTA'
            else:
                tour = 'Unknown'
            
            df_list = []
            for year in YEARS_MAIN_TOUR:
                # Construct the expected file path pattern for each year
                file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
                matching_files = glob.glob(file_pattern)
                
                if matching_files:
                    file_path = matching_files[0] # Use the first match found
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    # Add tour column directly (CSV files don't have tour column)
                    df['tour'] = tour
                    df['_source_file'] = file_path
                    df_list.append(df)
                else:
                    # This is not an error, just means data for that year/tour doesn't exist
                    pass

            if df_list:
                # Combine all dataframes for the current tour (ATP or WTA)
                tour_df = pd.concat(df_list, ignore_index=True)
                master_df_list.append(tour_df)
    else:
        print("Skipping main tour matches (LOAD_MAIN_TOUR_MATCHES = False)")

    # Load amateur tennis data (1877-1967)
    if LOAD_AMATEUR_MATCHES:
        amateur_file = os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_matches_amateur.csv")
        if os.path.exists(amateur_file):
            print(f"\n--- Loading Amateur Tennis Data (1877-1967) ---")
            print(f"Reading {amateur_file}...")
            amateur_df = pd.read_csv(amateur_file, low_memory=False, index_col=False)
            # Add tour column directly (CSV files don't have tour column)
            amateur_df['tour'] = 'ATP'  # Amateur data is from ATP source
            amateur_df['_source_file'] = amateur_file
            master_df_list.append(amateur_df)
            print(f"Amateur matches loaded: {len(amateur_df)}")
        else:
            print(f"Amateur tennis file not found: {amateur_file}")
    else:
        print("\nSkipping amateur matches (LOAD_AMATEUR_MATCHES = False)")
    
    # Load qualifying/challenger/futures data
    print(f"\n--- Loading Qualifying/Challenger/Futures Data ---")
    
    # ATP Qualifying/Challenger data (combined files)
    # Files are named: atp_matches_qual_chall_*.csv
    # They contain: ATP Qualifying, ATP Challenger, and ATP Challenger Qualifying matches
    # Categorization will happen in transformers based on tourney_level and round
    if LOAD_ATP_QUALIFYING or LOAD_ATP_CHALLENGER or LOAD_ATP_CHALLENGER_QUAL:
        atp_qual_chall_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_matches_qual_chall_*.csv"))
        if atp_qual_chall_files:
            print(f"Loading ATP Qualifying/Challenger data ({len(atp_qual_chall_files)} files)...")
            atp_qual_chall_dfs = []
            
            # Initialize progress tracker for qual/chall files
            progress = ProgressTracker(len(atp_qual_chall_files), "ATP Qual/Chall Loading")
            
            for file_path in sorted(atp_qual_chall_files):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    # Add tour column directly (CSV files don't have tour column)
                    df['tour'] = 'ATP'
                    df['_source_file'] = file_path
                    atp_qual_chall_dfs.append(df)
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            if atp_qual_chall_dfs:
                atp_qual_chall_df = pd.concat(atp_qual_chall_dfs, ignore_index=True)
                master_df_list.append(atp_qual_chall_df)
                print(f"  ATP Qualifying/Challenger matches loaded: {len(atp_qual_chall_df)}")
        else:
            print("  No ATP Qualifying/Challenger files found (atp_matches_qual_chall_*.csv)")
    else:
        print("Skipping ATP Qualifying/Challenger data (all switches set to False)")
    
    # ATP Futures data
    if LOAD_ATP_FUTURES:
        atp_futures_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_matches_futures_*.csv"))
        if atp_futures_files:
            print(f"Loading ATP Futures data ({len(atp_futures_files)} files)...")
            atp_futures_dfs = []
            
            # Initialize progress tracker for futures files
            progress = ProgressTracker(len(atp_futures_files), "ATP Futures Loading")
            
            for file_path in sorted(atp_futures_files):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    # Add tour column directly (CSV files don't have tour column)
                    df['tour'] = 'ATP'
                    df['_source_file'] = file_path
                    atp_futures_dfs.append(df)
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            if atp_futures_dfs:
                atp_futures_df = pd.concat(atp_futures_dfs, ignore_index=True)
                master_df_list.append(atp_futures_df)
                print(f"  ATP Futures matches loaded: {len(atp_futures_df)}")
    else:
        print("Skipping ATP Futures (LOAD_ATP_FUTURES = False)")
    
    # WTA Qualifying/ITF data
    # Files are named: wta_matches_qual_itf_*.csv
    # They contain: WTA Qualifying and WTA ITF matches
    # Categorization will happen in transformers based on round column
    if LOAD_WTA_QUALIFYING or LOAD_WTA_ITF:
        wta_qual_itf_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_matches_qual_itf_*.csv"))
        if wta_qual_itf_files:
            print(f"Loading WTA Qualifying/ITF data ({len(wta_qual_itf_files)} files)...")
            wta_qual_itf_dfs = []
            
            # Initialize progress tracker for WTA qual/itf files
            progress = ProgressTracker(len(wta_qual_itf_files), "WTA Qual/ITF Loading")
            
            for file_path in sorted(wta_qual_itf_files):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    # Add tour column directly (CSV files don't have tour column)
                    df['tour'] = 'WTA'
                    df['_source_file'] = file_path
                    wta_qual_itf_dfs.append(df)
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            if wta_qual_itf_dfs:
                wta_qual_itf_df = pd.concat(wta_qual_itf_dfs, ignore_index=True)
                master_df_list.append(wta_qual_itf_df)
                print(f"  WTA Qualifying/ITF matches loaded: {len(wta_qual_itf_df)}")
        else:
            print("  No WTA Qualifying/ITF files found (wta_matches_qual_itf_*.csv)")
    else:
        print("Skipping WTA Qualifying/ITF data (all switches set to False)")
    
    # Check if any data was loaded
    if not master_df_list:
        print("No match data found. Exiting.")
        return pd.DataFrame()
    
    # Combine all dataframes (raw data only - transformations happen in transformers)
    matches_df = pd.concat(master_df_list, ignore_index=True)

    print(f"\nTotal matches loaded (Complete Tournament Coverage): {len(matches_df)}")
    return matches_df