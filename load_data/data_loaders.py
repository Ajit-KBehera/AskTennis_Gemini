"""
Data loading functions for tennis match data.

This module contains functions that load tennis data from CSV files,
including players, rankings, matches, and doubles data.
"""

import pandas as pd
import glob
import os

# Import configuration
from load_data.config import (
    PROJECT_ROOT, DATA_DIRS, YEARS_MAIN_TOUR,
    LOAD_ATP_PLAYERS, LOAD_WTA_PLAYERS,
    LOAD_ATP_RANKINGS, LOAD_WTA_RANKINGS,
    LOAD_MAIN_TOUR_MATCHES, LOAD_AMATEUR_MATCHES,
    LOAD_ATP_QUALIFYING, LOAD_ATP_CHALLENGER, LOAD_ATP_CHALLENGER_QUAL,
    LOAD_ATP_FUTURES, LOAD_WTA_QUALIFYING, LOAD_WTA_ITF,
    LOAD_DAVIS_CUP, LOAD_FED_CUP, LOAD_DOUBLES_MATCHES
)

# Import utilities
from load_data.utils import ProgressTracker


def load_players_data():
    """
    Loads player information from ATP and WTA player files.
    """
    print("--- Loading Player Information ---")
    
    # Load ATP players
    atp_players = pd.DataFrame()
    if LOAD_ATP_PLAYERS:
        atp_players_path = os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_players.csv")
        if os.path.exists(atp_players_path):
            print(f"Reading {atp_players_path}...")
            atp_players = pd.read_csv(atp_players_path, index_col=False)
            atp_players['tour'] = 'ATP'
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
            wta_players['tour'] = 'WTA'
            print(f"WTA players loaded: {len(wta_players)}")
        else:
            print(f"Warning: {wta_players_path} not found")
    else:
        print("Skipping WTA players (LOAD_WTA_PLAYERS = False)")
    
    # Combine ATP and WTA players
    if not atp_players.empty and not wta_players.empty:
        all_players = pd.concat([atp_players, wta_players], ignore_index=True)
    elif not atp_players.empty:
        all_players = atp_players
    elif not wta_players.empty:
        all_players = wta_players
    else:
        print("No player data found!")
        return pd.DataFrame()
    
    # Clean and standardize player data
    all_players['dob'] = pd.to_datetime(all_players['dob'], format='%Y%m%d', errors='coerce')
    all_players['height'] = pd.to_numeric(all_players['height'], errors='coerce')
    
    # Create full name for easier searching
    all_players['full_name'] = all_players['name_first'] + ' ' + all_players['name_last']
    
    print(f"Total players loaded: {len(all_players)}")
    return all_players

def load_rankings_data():
    """
    Loads rankings data from ATP and WTA ranking files.
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
    
    # Build list of files to load based on switches
    ranking_files = []
    if LOAD_ATP_RANKINGS:
        ranking_files.extend(atp_ranking_files)
    else:
        print("Skipping ATP rankings (LOAD_ATP_RANKINGS = False)")
    
    if LOAD_WTA_RANKINGS:
        ranking_files.extend(wta_ranking_files)
    else:
        print("Skipping WTA rankings (LOAD_WTA_RANKINGS = False)")
    
    if not ranking_files:
        print("No rankings files selected for loading!")
        return pd.DataFrame()
    
    all_rankings = []
    existing_files = [f for f in ranking_files if os.path.exists(f)]
    
    # Initialize progress tracker for ranking files
    progress = ProgressTracker(len(existing_files), "Rankings Loading")
    
    for file_path in ranking_files:
        if os.path.exists(file_path):
            progress.update(1, f"Loading {os.path.basename(file_path)}...")
            try:
                df = pd.read_csv(file_path, index_col=False)
                
                # Determine tour based on file path
                if 'atp' in file_path:
                    df['tour'] = 'ATP'
                elif 'wta' in file_path:
                    df['tour'] = 'WTA'
                else:
                    df['tour'] = 'Unknown'
                
                # Standardize column names (WTA files have 'tours' column)
                if 'tours' in df.columns:
                    df = df.rename(columns={'tours': 'tournaments'})
                # Note: ATP files don't have tournaments column, and it's not used in queries
                
                all_rankings.append(df)
                print(f"  Loaded {len(df)} ranking records")
                
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
        else:
            print(f"  File not found: {file_path}")
    
    if not all_rankings:
        print("No rankings data found!")
        return pd.DataFrame()
    
    # Combine all rankings data
    rankings_df = pd.concat(all_rankings, ignore_index=True)
    
    # Clean and standardize rankings data
    rankings_df['ranking_date'] = pd.to_datetime(rankings_df['ranking_date'], format='%Y%m%d', errors='coerce')
    rankings_df['rank'] = pd.to_numeric(rankings_df['rank'], errors='coerce')
    rankings_df['points'] = pd.to_numeric(rankings_df['points'], errors='coerce')
    rankings_df['player'] = pd.to_numeric(rankings_df['player'], errors='coerce')
    
    # Remove invalid data
    rankings_df = rankings_df.dropna(subset=['ranking_date', 'rank', 'player'])
    
    print(f"Total rankings loaded: {len(rankings_df)}")
    print(f"Date range: {rankings_df['ranking_date'].min()} to {rankings_df['ranking_date'].max()}")
    
    return rankings_df

def load_matches_data():
    """
    Loads match data from ATP and WTA files.
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
            all_files = glob.glob(os.path.join(data_dir, "*_matches_*.csv"))
            
            # Determine tour based on directory
            if 'atp' in data_dir.lower():
                tour_name = 'ATP'
            elif 'wta' in data_dir.lower():
                tour_name = 'WTA'
            else:
                tour_name = 'Unknown'
            
            df_list = []
            for year in YEARS_MAIN_TOUR:
                # Construct the expected file path pattern for each year
                file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
                matching_files = glob.glob(file_pattern)
                
                if matching_files:
                    file_path = matching_files[0] # Use the first match found
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d')
                    df['tour'] = tour_name  # Add tour column
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
            amateur_df['tourney_date'] = pd.to_datetime(amateur_df['tourney_date'], format='%Y%m%d')
            amateur_df['tour'] = 'ATP'  # Amateur data is from ATP source
            # Era will be classified later as 'Closed Era' (pre-1968)
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
    # Categorize based on tourney_level and round columns:
    #   - tourney_level == 'C' and round starts with 'Q': ATP_Challenger_Qualifying
    #   - tourney_level == 'C' and round doesn't start with 'Q': ATP_Challenger
    #   - tourney_level != 'C' and round starts with 'Q': ATP_Qualifying
    if LOAD_ATP_QUALIFYING or LOAD_ATP_CHALLENGER or LOAD_ATP_CHALLENGER_QUAL:
        atp_qual_chall_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_matches_qual_chall_*.csv"))
        if atp_qual_chall_files:
            print(f"Loading ATP Qualifying/Challenger data ({len(atp_qual_chall_files)} files)...")
            atp_qual_dfs = []
            atp_chall_dfs = []
            atp_chall_qual_dfs = []
            
            # Initialize progress tracker for qual/chall files
            progress = ProgressTracker(len(atp_qual_chall_files), "ATP Qual/Chall Loading")
            
            for i, file_path in enumerate(sorted(atp_qual_chall_files), 1):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tour'] = 'ATP'  # Add tour column
                    
                    # Categorize matches based on tourney_level and round
                    # Ensure round column exists and is string type for checking
                    if 'round' not in df.columns:
                        df['round'] = ''
                    df['round'] = df['round'].astype(str)
                    
                    # Check if tourney_level column exists
                    if 'tourney_level' not in df.columns:
                        df['tourney_level'] = ''
                    df['tourney_level'] = df['tourney_level'].astype(str)
                    
                    # Identify qualifying rounds (Q1, Q2, Q3, etc.)
                    is_qualifying_round = df['round'].str.startswith('Q', na=False)
                    is_challenger_level = (df['tourney_level'] == 'C')
                    
                    # Split into categories
                    if LOAD_ATP_CHALLENGER_QUAL:
                        chall_qual_mask = is_challenger_level & is_qualifying_round
                        if chall_qual_mask.sum() > 0:
                            chall_qual_df = df[chall_qual_mask].copy()
                            chall_qual_df['tournament_type'] = 'ATP_Challenger_Qualifying'
                            atp_chall_qual_dfs.append(chall_qual_df)
                    
                    if LOAD_ATP_CHALLENGER:
                        chall_mask = is_challenger_level & ~is_qualifying_round
                        if chall_mask.sum() > 0:
                            chall_df = df[chall_mask].copy()
                            chall_df['tournament_type'] = 'ATP_Challenger'
                            atp_chall_dfs.append(chall_df)
                    
                    if LOAD_ATP_QUALIFYING:
                        qual_mask = ~is_challenger_level & is_qualifying_round
                        if qual_mask.sum() > 0:
                            qual_df = df[qual_mask].copy()
                            qual_df['tournament_type'] = 'ATP_Qualifying'
                            atp_qual_dfs.append(qual_df)
                    
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            # Combine and add to master list
            if LOAD_ATP_QUALIFYING and atp_qual_dfs:
                atp_qual_df = pd.concat(atp_qual_dfs, ignore_index=True)
                master_df_list.append(atp_qual_df)
                print(f"  ATP Qualifying matches loaded: {len(atp_qual_df)}")
            
            if LOAD_ATP_CHALLENGER and atp_chall_dfs:
                atp_chall_df = pd.concat(atp_chall_dfs, ignore_index=True)
                master_df_list.append(atp_chall_df)
                print(f"  ATP Challenger matches loaded: {len(atp_chall_df)}")
            
            if LOAD_ATP_CHALLENGER_QUAL and atp_chall_qual_dfs:
                atp_chall_qual_df = pd.concat(atp_chall_qual_dfs, ignore_index=True)
                master_df_list.append(atp_chall_qual_df)
                print(f"  ATP Challenger Qualifying matches loaded: {len(atp_chall_qual_df)}")
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
            
            for i, file_path in enumerate(sorted(atp_futures_files), 1):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'ATP_Futures'
                    df['tour'] = 'ATP'  # Add tour column
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
    
    # WTA Qualifying data
    if LOAD_WTA_QUALIFYING:
        wta_qual_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_matches_qual_itf_*.csv"))
        if wta_qual_files:
            print(f"Loading WTA Qualifying data ({len(wta_qual_files)} files)...")
            wta_qual_dfs = []
            
            # Initialize progress tracker for WTA qualifying files
            progress = ProgressTracker(len(wta_qual_files), "WTA Qualifying Loading")
            
            for i, file_path in enumerate(sorted(wta_qual_files), 1):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'WTA_Qualifying'
                    df['tour'] = 'WTA'  # Add tour column
                    wta_qual_dfs.append(df)
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            if wta_qual_dfs:
                wta_qual_df = pd.concat(wta_qual_dfs, ignore_index=True)
                master_df_list.append(wta_qual_df)
                print(f"  WTA Qualifying matches loaded: {len(wta_qual_df)}")
    else:
        print("Skipping WTA Qualifying (LOAD_WTA_QUALIFYING = False)")
    
    # WTA ITF data
    if LOAD_WTA_ITF:
        wta_itf_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_matches_itf_*.csv"))
        if wta_itf_files:
            print(f"Loading WTA ITF data ({len(wta_itf_files)} files)...")
            wta_itf_dfs = []
            
            # Initialize progress tracker for WTA ITF files
            progress = ProgressTracker(len(wta_itf_files), "WTA ITF Loading")
            
            for i, file_path in enumerate(sorted(wta_itf_files), 1):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'WTA_ITF'
                    df['tour'] = 'WTA'  # Add tour column
                    wta_itf_dfs.append(df)
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            if wta_itf_dfs:
                wta_itf_df = pd.concat(wta_itf_dfs, ignore_index=True)
                master_df_list.append(wta_itf_df)
                print(f"  WTA ITF matches loaded: {len(wta_itf_df)}")
    else:
        print("Skipping WTA ITF (LOAD_WTA_ITF = False)")
    
    # Load Davis Cup data
    if LOAD_DAVIS_CUP:
        print(f"\n--- Loading Davis Cup Data ---")
        davis_cup_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_matches_davis_cup_*.csv"))
        if davis_cup_files:
            print(f"Loading Davis Cup data ({len(davis_cup_files)} files)...")
            davis_cup_dfs = []
            
            # Initialize progress tracker for Davis Cup files
            progress = ProgressTracker(len(davis_cup_files), "Davis Cup Loading")
            
            for i, file_path in enumerate(sorted(davis_cup_files), 1):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'Davis_Cup'
                    df['tour'] = 'ATP'  # Davis Cup is men's competition
                    davis_cup_dfs.append(df)
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            if davis_cup_dfs:
                davis_cup_df = pd.concat(davis_cup_dfs, ignore_index=True)
                master_df_list.append(davis_cup_df)
                print(f"  Davis Cup matches loaded: {len(davis_cup_df)}")
    else:
        print("\nSkipping Davis Cup (LOAD_DAVIS_CUP = False)")
    
    # Load Fed Cup (BJK Cup) data
    if LOAD_FED_CUP:
        print(f"\n--- Loading Fed Cup (BJK Cup) Data ---")
        fed_cup_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_wta/wta_matches_fed_cup_*.csv"))
        if fed_cup_files:
            print(f"Loading Fed Cup (BJK Cup) data ({len(fed_cup_files)} files)...")
            fed_cup_dfs = []
            
            # Initialize progress tracker for Fed Cup files
            progress = ProgressTracker(len(fed_cup_files), "Fed Cup Loading")
            
            for i, file_path in enumerate(sorted(fed_cup_files), 1):
                try:
                    progress.update(1, f"Loading {os.path.basename(file_path)}...")
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'Fed_Cup'
                    df['tour'] = 'WTA'  # Fed Cup is women's competition
                    fed_cup_dfs.append(df)
                except Exception as e:
                    print(f"  Error loading {file_path}: {e}")
            
            progress.complete()
            
            if fed_cup_dfs:
                fed_cup_df = pd.concat(fed_cup_dfs, ignore_index=True)
                master_df_list.append(fed_cup_df)
                print(f"  Fed Cup (BJK Cup) matches loaded: {len(fed_cup_df)}")
    else:
        print("\nSkipping Fed Cup (LOAD_FED_CUP = False)")
    
    # Check if any data was loaded
    if not master_df_list:
        print("No match data found. Exiting.")
        return pd.DataFrame()
    
    # Combine the ATP, WTA, and amateur dataframes into one master dataframe
    matches_df = pd.concat(master_df_list, ignore_index=True)
    
    # Add era classification for all matches
    # Classify based on year: 1968+ = Open Era, <1968 = Closed Era
    def classify_era(row):
        if pd.isna(row.get('tourney_date')):
            return 'Unknown'
        year = row['tourney_date'].year
        if year >= 1968:
            return 'Open Era'
        else:
            return 'Closed Era'
    
    # Apply era classification
    matches_df['era'] = matches_df.apply(classify_era, axis=1)
    
    # Add tournament type classification for all matches
    # Set main tour matches (currently NULL) to "Main Tour"
    matches_df['tournament_type'] = matches_df['tournament_type'].fillna('Main Tour')
    
    # Add tour classification for all matches
    matches_df['tour'] = matches_df['tour'].fillna('Unknown')  # Default to Unknown for any missing tour data
    
    # Convert tourney_date to datetime objects for proper sorting/filtering
    matches_df['tourney_date'] = pd.to_datetime(matches_df['tourney_date'], format='%Y%m%d', errors='coerce')

    print(f"\nTotal matches loaded (Complete Tournament Coverage): {len(matches_df)}")
    return matches_df

def load_doubles_data():
    """
    Loads doubles match data from ATP doubles files.
    Returns a DataFrame with doubles matches.
    """
    if not LOAD_DOUBLES_MATCHES:
        print("\nSkipping doubles matches (LOAD_DOUBLES_MATCHES = False)")
        return pd.DataFrame()
    
    print("\n--- Loading Doubles Match Data ---")
    
    # Find all ATP doubles files
    doubles_files = glob.glob(os.path.join(PROJECT_ROOT, "data/tennis_atp/atp_matches_doubles_*.csv"))
    
    if not doubles_files:
        print("No doubles match files found.")
        return pd.DataFrame()
    
    print(f"Loading ATP Doubles data ({len(doubles_files)} files)...")
    doubles_dfs = []
    
    # Initialize progress tracker for doubles files
    progress = ProgressTracker(len(doubles_files), "Doubles Loading")
    
    for i, file_path in enumerate(sorted(doubles_files), 1):
        try:
            progress.update(1, f"Loading {os.path.basename(file_path)}...")
            df = pd.read_csv(file_path, low_memory=False, index_col=False)
            df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
            df['match_type'] = 'Doubles'
            df['tour'] = 'ATP'  # Doubles data is from ATP source
            doubles_dfs.append(df)
            
        except Exception as e:
            print(f"  Error loading {file_path}: {e}")
    
    if doubles_dfs:
        doubles_df = pd.concat(doubles_dfs, ignore_index=True)
        print(f"  ATP Doubles matches loaded: {len(doubles_df)}")
        return doubles_df
    else:
        print("  No doubles data could be loaded.")
        return pd.DataFrame()

# Transformation functions are now imported from data_transformers module
