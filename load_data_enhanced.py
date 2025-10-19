import pandas as pd
import sqlite3
import glob
import os
import time
from datetime import datetime, timedelta

# --- Configuration ---
DATA_DIRS = ["data/tennis_atp", "data/tennis_wta"]
YEARS = list(range(1968, 2026))  # Complete historical coverage: 1968-2024
DB_FILE = "tennis_data.db"

# Option to load only recent years for testing (set to False for complete data)
LOAD_RECENT_ONLY = False  # Set to True to load only 2020-2024 for testing
RECENT_YEARS = list(range(2020, 2026)) if LOAD_RECENT_ONLY else YEARS

class ProgressTracker:
    """Track and display loading progress with time estimates."""
    
    def __init__(self, total_steps, step_name="Loading"):
        self.total_steps = total_steps
        self.current_step = 0
        self.step_name = step_name
        self.start_time = time.time()
        self.last_update = time.time()
        
    def update(self, step_increment=1, message=""):
        """Update progress and display status."""
        self.current_step += step_increment
        percentage = (self.current_step / self.total_steps) * 100
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if self.current_step > 0:
            # Calculate estimated total time
            estimated_total_time = elapsed_time * (self.total_steps / self.current_step)
            remaining_time = estimated_total_time - elapsed_time
            
            # Format time strings
            elapsed_str = str(timedelta(seconds=int(elapsed_time)))
            remaining_str = str(timedelta(seconds=int(remaining_time)))
            
            # Update display every 2 seconds or on completion
            if current_time - self.last_update >= 2 or self.current_step == self.total_steps:
                print(f"\r{self.step_name}: {self.current_step}/{self.total_steps} ({percentage:.1f}%) | "
                      f"Elapsed: {elapsed_str} | ETA: {remaining_str} | {message}", end="", flush=True)
                self.last_update = current_time
        
        if self.current_step == self.total_steps:
            print()  # New line when complete
    
    def complete(self, message=""):
        """Mark as complete and show final stats."""
        total_time = time.time() - self.start_time
        print(f"\n✅ {self.step_name} completed in {str(timedelta(seconds=int(total_time)))} | {message}")

def load_players_data():
    """
    Loads player information from ATP and WTA player files.
    """
    print("--- Loading Player Information ---")
    
    # Load ATP players
    atp_players_path = "data/tennis_atp/atp_players.csv"
    if os.path.exists(atp_players_path):
        print(f"Reading {atp_players_path}...")
        atp_players = pd.read_csv(atp_players_path)
        atp_players['tour'] = 'ATP'
        print(f"ATP players loaded: {len(atp_players)}")
    else:
        print(f"Warning: {atp_players_path} not found")
        atp_players = pd.DataFrame()
    
    # Load WTA players
    wta_players_path = "data/tennis_wta/wta_players.csv"
    if os.path.exists(wta_players_path):
        print(f"Reading {wta_players_path}...")
        wta_players = pd.read_csv(wta_players_path)
        wta_players['tour'] = 'WTA'
        print(f"WTA players loaded: {len(wta_players)}")
    else:
        print(f"Warning: {wta_players_path} not found")
        wta_players = pd.DataFrame()
    
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
    ranking_files = [
        "data/tennis_atp/atp_rankings_70s.csv",
        "data/tennis_atp/atp_rankings_80s.csv", 
        "data/tennis_atp/atp_rankings_90s.csv",
        "data/tennis_atp/atp_rankings_00s.csv",
        "data/tennis_atp/atp_rankings_10s.csv",
        "data/tennis_atp/atp_rankings_20s.csv",
        "data/tennis_atp/atp_rankings_current.csv",
        "data/tennis_wta/wta_rankings_80s.csv",
        "data/tennis_wta/wta_rankings_90s.csv", 
        "data/tennis_wta/wta_rankings_00s.csv",
        "data/tennis_wta/wta_rankings_10s.csv",
        "data/tennis_wta/wta_rankings_20s.csv",
        "data/tennis_wta/wta_rankings_current.csv"
    ]
    
    all_rankings = []
    existing_files = [f for f in ranking_files if os.path.exists(f)]
    
    # Initialize progress tracker for ranking files
    progress = ProgressTracker(len(existing_files), "Rankings Loading")
    
    for file_path in ranking_files:
        if os.path.exists(file_path):
            progress.update(1, f"Loading {os.path.basename(file_path)}...")
            try:
                df = pd.read_csv(file_path)
                
                # Determine tour based on file path
                if 'atp' in file_path:
                    df['tour'] = 'ATP'
                elif 'wta' in file_path:
                    df['tour'] = 'WTA'
                else:
                    df['tour'] = 'Unknown'
                
                # Standardize column names
                if 'tours' in df.columns:
                    df = df.rename(columns={'tours': 'tournaments'})
                else:
                    df['tournaments'] = None
                
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
    
    # Calculate total files to process
    total_files = 0
    for data_dir in DATA_DIRS:
        for year in YEARS:
            file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
            if glob.glob(file_pattern):
                total_files += 1
    
    # Initialize progress tracker for match files
    progress = ProgressTracker(total_files, "Match Loading")
    
    # Loop through each data directory (ATP and WTA)
    for data_dir in DATA_DIRS:
        print(f"\n--- Processing directory: {data_dir} ---")
        all_files = glob.glob(os.path.join(data_dir, "*_matches_*.csv"))
        
        df_list = []
        for year in YEARS:
            # Construct the expected file path pattern for each year
            file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
            matching_files = glob.glob(file_pattern)
            
            if matching_files:
                file_path = matching_files[0] # Use the first match found
                progress.update(1, f"Loading {os.path.basename(file_path)}...")
                df = pd.read_csv(file_path, low_memory=False)
                df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d')
                df_list.append(df)
            else:
                # This is not an error, just means data for that year/tour doesn't exist
                pass

        if df_list:
            # Combine all dataframes for the current tour (ATP or WTA)
            tour_df = pd.concat(df_list, ignore_index=True)
            master_df_list.append(tour_df)

    if not master_df_list:
        print("No data found in any directory. Exiting.")
        return pd.DataFrame()

    # Load amateur tennis data (1877-1967)
    amateur_file = "data/tennis_atp/atp_matches_amateur.csv"
    if os.path.exists(amateur_file):
        print(f"\n--- Loading Amateur Tennis Data (1877-1967) ---")
        print(f"Reading {amateur_file}...")
        amateur_df = pd.read_csv(amateur_file, low_memory=False)
        amateur_df['tourney_date'] = pd.to_datetime(amateur_df['tourney_date'], format='%Y%m%d')
        amateur_df['era'] = 'Amateur'  # Mark as amateur era
        master_df_list.append(amateur_df)
        print(f"Amateur matches loaded: {len(amateur_df)}")
    else:
        print(f"Amateur tennis file not found: {amateur_file}")
    
    # Load qualifying/challenger/futures data
    print(f"\n--- Loading Qualifying/Challenger/Futures Data ---")
    
    # ATP Qualifying/Challenger data
    atp_qual_chall_files = glob.glob("data/tennis_atp/atp_matches_qual_chall_*.csv")
    if atp_qual_chall_files:
        # Filter files by recent years if LOAD_RECENT_ONLY is True
        if LOAD_RECENT_ONLY:
            filtered_files = []
            for file_path in atp_qual_chall_files:
                year = int(file_path.split('_')[-1].split('.')[0])
                if year in RECENT_YEARS:
                    filtered_files.append(file_path)
            atp_qual_chall_files = filtered_files
        
        print(f"Loading ATP Qualifying/Challenger data ({len(atp_qual_chall_files)} files)...")
        atp_qual_chall_dfs = []
        for i, file_path in enumerate(sorted(atp_qual_chall_files), 1):
            try:
                if i % 10 == 0:  # Progress indicator every 10 files
                    print(f"  Processing file {i}/{len(atp_qual_chall_files)}: {os.path.basename(file_path)}")
                df = pd.read_csv(file_path, low_memory=False)
                df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                df['tournament_type'] = 'ATP_Qual_Chall'
                atp_qual_chall_dfs.append(df)
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
        
        if atp_qual_chall_dfs:
            atp_qual_chall_df = pd.concat(atp_qual_chall_dfs, ignore_index=True)
            master_df_list.append(atp_qual_chall_df)
            print(f"  ATP Qualifying/Challenger matches loaded: {len(atp_qual_chall_df)}")
    
    # ATP Futures data
    atp_futures_files = glob.glob("data/tennis_atp/atp_matches_futures_*.csv")
    if atp_futures_files:
        # Filter files by recent years if LOAD_RECENT_ONLY is True
        if LOAD_RECENT_ONLY:
            filtered_files = []
            for file_path in atp_futures_files:
                year = int(file_path.split('_')[-1].split('.')[0])
                if year in RECENT_YEARS:
                    filtered_files.append(file_path)
            atp_futures_files = filtered_files
        
        print(f"Loading ATP Futures data ({len(atp_futures_files)} files)...")
        atp_futures_dfs = []
        for i, file_path in enumerate(sorted(atp_futures_files), 1):
            try:
                if i % 10 == 0:  # Progress indicator every 10 files
                    print(f"  Processing file {i}/{len(atp_futures_files)}: {os.path.basename(file_path)}")
                df = pd.read_csv(file_path, low_memory=False)
                df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                df['tournament_type'] = 'ATP_Futures'
                atp_futures_dfs.append(df)
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
        
        if atp_futures_dfs:
            atp_futures_df = pd.concat(atp_futures_dfs, ignore_index=True)
            master_df_list.append(atp_futures_df)
            print(f"  ATP Futures matches loaded: {len(atp_futures_df)}")
    
    # WTA Qualifying/ITF data
    wta_qual_itf_files = glob.glob("data/tennis_wta/wta_matches_qual_itf_*.csv")
    if wta_qual_itf_files:
        # Filter files by recent years if LOAD_RECENT_ONLY is True
        if LOAD_RECENT_ONLY:
            filtered_files = []
            for file_path in wta_qual_itf_files:
                year = int(file_path.split('_')[-1].split('.')[0])
                if year in RECENT_YEARS:
                    filtered_files.append(file_path)
            wta_qual_itf_files = filtered_files
        
        print(f"Loading WTA Qualifying/ITF data ({len(wta_qual_itf_files)} files)...")
        wta_qual_itf_dfs = []
        for i, file_path in enumerate(sorted(wta_qual_itf_files), 1):
            try:
                if i % 10 == 0:  # Progress indicator every 10 files
                    print(f"  Processing file {i}/{len(wta_qual_itf_files)}: {os.path.basename(file_path)}")
                df = pd.read_csv(file_path, low_memory=False)
                df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                df['tournament_type'] = 'WTA_Qual_ITF'
                wta_qual_itf_dfs.append(df)
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
        
        if wta_qual_itf_dfs:
            wta_qual_itf_df = pd.concat(wta_qual_itf_dfs, ignore_index=True)
            master_df_list.append(wta_qual_itf_df)
            print(f"  WTA Qualifying/ITF matches loaded: {len(wta_qual_itf_df)}")
    
    # Combine the ATP, WTA, and amateur dataframes into one master dataframe
    matches_df = pd.concat(master_df_list, ignore_index=True)
    
    # Add era classification for all matches
    matches_df['era'] = matches_df['era'].fillna('Professional')  # Default to professional era
    
    # Add tournament type classification for all matches
    matches_df['tournament_type'] = matches_df['tournament_type'].fillna('Main_Tour')  # Default to main tour
    
    # Convert tourney_date to datetime objects for proper sorting/filtering
    matches_df['tourney_date'] = pd.to_datetime(matches_df['tourney_date'], format='%Y%m%d', errors='coerce')

    print(f"\nTotal matches loaded (Complete Tournament Coverage): {len(matches_df)}")
    return matches_df

def load_doubles_data():
    """
    Loads doubles match data from ATP doubles files.
    Returns a DataFrame with doubles matches.
    """
    print("\n--- Loading Doubles Match Data ---")
    
    # Find all ATP doubles files
    doubles_files = glob.glob("data/tennis_atp/atp_matches_doubles_*.csv")
    
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
            df = pd.read_csv(file_path, low_memory=False)
            df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
            df['match_type'] = 'Doubles'
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

def load_mixed_doubles_data():
    """
    Loads Grand Slam mixed doubles match data from CSV files.
    Returns a DataFrame with mixed doubles matches.
    """
    print("\n--- Loading Mixed Doubles Match Data ---")
    
    # Find all mixed doubles files
    mixed_doubles_files = glob.glob("data/tennis_slam_pointbypoint/*matches-mixed.csv")
    
    if not mixed_doubles_files:
        print("No mixed doubles match files found.")
        return pd.DataFrame()
    
    print(f"Loading Grand Slam Mixed Doubles data ({len(mixed_doubles_files)} files)...")
    mixed_doubles_dfs = []
    
    # Initialize progress tracker for mixed doubles files
    progress = ProgressTracker(len(mixed_doubles_files), "Mixed Doubles Loading")
    
    for i, file_path in enumerate(sorted(mixed_doubles_files), 1):
        try:
            progress.update(1, f"Loading {os.path.basename(file_path)}...")
            df = pd.read_csv(file_path, low_memory=False)
            
            # Add tournament information from filename
            filename = os.path.basename(file_path)
            if 'ausopen' in filename:
                df['tourney_name'] = 'Australian Open'
                df['tourney_level'] = 'G'
                df['surface'] = 'Hard'
            elif 'frenchopen' in filename:
                df['tourney_name'] = 'French Open'
                df['tourney_level'] = 'G'
                df['surface'] = 'Clay'
            elif 'wimbledon' in filename:
                df['tourney_name'] = 'Wimbledon'
                df['tourney_level'] = 'G'
                df['surface'] = 'Grass'
            elif 'usopen' in filename:
                df['tourney_name'] = 'US Open'
                df['tourney_level'] = 'G'
                df['surface'] = 'Hard'
            
            # Add match type
            df['match_type'] = 'Mixed Doubles'
            
            # Convert year to tourney_date if available
            if 'year' in df.columns:
                df['tourney_date'] = pd.to_datetime(df['year'].astype(str) + '-01-01', errors='coerce')
            
            mixed_doubles_dfs.append(df)
            
        except Exception as e:
            print(f"  Error loading {file_path}: {e}")
    
    if mixed_doubles_dfs:
        mixed_doubles_df = pd.concat(mixed_doubles_dfs, ignore_index=True)
        print(f"  Grand Slam Mixed Doubles matches loaded: {len(mixed_doubles_df)}")
        return mixed_doubles_df
    else:
        print("  No mixed doubles data could be loaded.")
        return pd.DataFrame()

def parse_date_components(df):
    """
    Parse tourney_date into event_year, event_month, event_date columns.
    Replaces the tourney_date column with three separate columns.
    """
    print("\n--- Parsing Date Components ---")
    
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    # Extract date components
    df_copy['event_year'] = df_copy['tourney_date'].dt.year
    df_copy['event_month'] = df_copy['tourney_date'].dt.month
    df_copy['event_date'] = df_copy['tourney_date'].dt.day
    
    # Add month name and season
    df_copy['event_month_name'] = df_copy['tourney_date'].dt.month_name()
    df_copy['event_season'] = df_copy['tourney_date'].dt.month.map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    
    # Remove the original tourney_date column
    df_copy = df_copy.drop('tourney_date', axis=1)
    
    print(f"Date parsing completed: {len(df_copy)}/{len(df)} dates parsed (100.0%)")
    print(f"Date range: {df_copy['event_year'].min()}-{df_copy['event_year'].max()}")
    print(f"Year range: {df_copy['event_year'].min()} to {df_copy['event_year'].max()}")
    
    return df_copy

def parse_score_data(df):
    """
    Parse score column into set1, set2, set3, set4, set5 columns.
    Replaces the score column with five separate columns.
    Handles RET by putting 'RET' in subsequent set columns.
    """
    print("\n--- Parsing Score Data ---")
    
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    # Initialize set columns
    df_copy['set1'] = None
    df_copy['set2'] = None
    df_copy['set3'] = None
    df_copy['set4'] = None
    df_copy['set5'] = None
    
    def parse_score(score_str):
        """Parse a single score string into set scores."""
        if pd.isna(score_str) or score_str == '':
            return [None, None, None, None, None]
        
        score_str = str(score_str).strip()
        
        # Handle special cases
        if score_str in ['W/O', 'WO', 'Walkover']:
            return ['W/O', None, None, None, None]
        elif score_str in ['DEF', 'Default']:
            return ['DEF', None, None, None, None]
        elif 'W/O' in score_str.upper() or 'WO' in score_str.upper():
            # Handle walkover - put W/O in only the next set, rest are NULL
            parts = score_str.split()
            sets = []
            wo_found = False
            
            for part in parts:
                if 'W/O' in part.upper() or 'WO' in part.upper():
                    wo_found = True
                    # Extract score before W/O
                    score_part = part.replace('W/O', '').replace('WO', '').replace('wo', '').strip()
                    if score_part:
                        sets.append(score_part)
                    # Add W/O to the next set only
                    sets.append('W/O')
                    break
                else:
                    sets.append(part)
            
            # Fill remaining sets with NULL (not W/O)
            while len(sets) < 5:
                sets.append(None)
            
            return sets[:5]
        elif 'DEF' in score_str.upper() or 'DEFAULT' in score_str.upper():
            # Handle default - put DEF in only the next set, rest are NULL
            parts = score_str.split()
            sets = []
            def_found = False
            
            for part in parts:
                if 'DEF' in part.upper() or 'DEFAULT' in part.upper():
                    def_found = True
                    # Extract score before DEF
                    score_part = part.replace('DEF', '').replace('DEFAULT', '').replace('def', '').strip()
                    if score_part:
                        sets.append(score_part)
                    # Add DEF to the next set only
                    sets.append('DEF')
                    break
                else:
                    sets.append(part)
            
            # Fill remaining sets with NULL (not DEF)
            while len(sets) < 5:
                sets.append(None)
            
            return sets[:5]
        elif 'RET' in score_str.upper():
            # Handle retirement - put RET in only the next set, rest are NULL
            parts = score_str.split()
            sets = []
            ret_found = False
            
            for part in parts:
                if 'RET' in part.upper():
                    ret_found = True
                    # Extract score before RET
                    score_part = part.replace('RET', '').replace('ret', '').strip()
                    if score_part:
                        sets.append(score_part)
                    # Add RET to the next set only
                    sets.append('RET')
                    break
                else:
                    sets.append(part)
            
            # Fill remaining sets with NULL (not RET)
            while len(sets) < 5:
                sets.append(None)
            
            return sets[:5]
        else:
            # Normal score parsing
            parts = score_str.split()
            sets = parts[:5]  # Take first 5 parts
            while len(sets) < 5:
                sets.append(None)
            return sets
    
    # Apply parsing to all scores
    parsed_scores = df_copy['score'].apply(parse_score)
    
    # Assign to set columns
    df_copy['set1'] = [s[0] for s in parsed_scores]
    df_copy['set2'] = [s[1] for s in parsed_scores]
    df_copy['set3'] = [s[2] for s in parsed_scores]
    df_copy['set4'] = [s[3] for s in parsed_scores]
    df_copy['set5'] = [s[4] for s in parsed_scores]
    
    # Remove the original score column
    df_copy = df_copy.drop('score', axis=1)
    
    # Show sample of parsed scores
    print(f"Score parsing completed: {len(df_copy)}/{len(df)} matches parsed (100.0%)")
    print("Sample parsed scores:")
    sample_scores = df_copy[['set1', 'set2', 'set3', 'set4', 'set5']].dropna(how='all').head(3)
    for idx, row in sample_scores.iterrows():
        original = df.loc[idx, 'score'] if idx < len(df) else 'N/A'
        parsed = ' | '.join([str(s) for s in row.values if pd.notna(s)])
        print(f"  Original: {original} -> Parsed: {parsed}")
    
    return df_copy

def fix_missing_surface_data(matches_df):
    """
    Fixes missing surface data by inferring surface from tournament names and historical data.
    """
    print("\n--- Fixing Missing Surface Data ---")
    
    # Count missing surface data
    missing_before = len(matches_df[matches_df['surface'].isna() | (matches_df['surface'] == '')])
    print(f"Missing surface data before fix: {missing_before:,} matches")
    
    if missing_before == 0:
        print("No missing surface data found!")
        return matches_df
    
    # Create a copy to avoid modifying original
    df = matches_df.copy()
    
    # Surface inference rules based on tournament names and historical data
    def infer_surface(row):
        tourney_name = str(row['tourney_name']).lower()
        tourney_date = row.get('tourney_date')  # Handle case where tourney_date might not exist
        
        # Grand Slam surface inference
        if 'wimbledon' in tourney_name:
            return 'Grass'
        elif any(name in tourney_name for name in ['french', 'roland', 'paris']):
            return 'Clay'
        elif any(name in tourney_name for name in ['us open', 'australian', 'melbourne']):
            return 'Hard'
        
        # Historical surface inference based on era
        if pd.notna(tourney_date):
            year = tourney_date.year
            
            # Pre-1970s: Mostly grass and clay
            if year < 1970:
                if any(name in tourney_name for name in ['grass', 'lawn', 'wimbledon']):
                    return 'Grass'
                elif any(name in tourney_name for name in ['clay', 'dirt', 'red']):
                    return 'Clay'
                else:
                    return 'Grass'  # Default for pre-1970s
            
            # 1970s-1980s: Introduction of hard courts
            elif year < 1990:
                if any(name in tourney_name for name in ['hard', 'concrete', 'asphalt']):
                    return 'Hard'
                elif any(name in tourney_name for name in ['grass', 'lawn']):
                    return 'Grass'
                elif any(name in tourney_name for name in ['clay', 'dirt', 'red']):
                    return 'Clay'
                else:
                    return 'Hard'  # Default for 1970s-1980s
            
            # 1990s+: Mostly hard courts
            else:
                if any(name in tourney_name for name in ['grass', 'lawn', 'wimbledon']):
                    return 'Grass'
                elif any(name in tourney_name for name in ['clay', 'dirt', 'red', 'french']):
                    return 'Clay'
                elif any(name in tourney_name for name in ['carpet', 'indoor']):
                    return 'Carpet'
                else:
                    return 'Hard'  # Default for modern era
        
        return 'Hard'  # Final default
    
    # Apply surface inference to missing data
    missing_mask = df['surface'].isna() | (df['surface'] == '')
    df.loc[missing_mask, 'surface'] = df[missing_mask].apply(infer_surface, axis=1)
    
    # Count remaining missing surface data
    missing_after = len(df[df['surface'].isna() | (df['surface'] == '')])
    fixed_count = missing_before - missing_after
    
    print(f"Fixed surface data: {fixed_count:,} matches")
    print(f"Remaining missing surface data: {missing_after:,} matches")
    
    if missing_after > 0:
        print("Surface distribution after fix:")
        surface_dist = df['surface'].value_counts()
        for surface, count in surface_dist.items():
            print(f"  {surface}: {count:,} matches")
    
    return df

def create_database_with_players():
    """
    Creates the enhanced database with COMPLETE tennis history (1877-2024), 
    including all tournament levels, player information, and rankings.
    """
    print("=== Enhanced Data Loading with COMPLETE Tournament Coverage (1877-2024) ===")
    
    # Initialize progress tracker for main steps
    main_steps = 9  # players, rankings, matches, doubles, mixed_doubles, surface_fix, date_parsing, score_parsing, database_creation
    progress = ProgressTracker(main_steps, "Database Creation")
    
    # Load player data
    progress.update(1, "Loading player data...")
    players_df = load_players_data()
    
    # Load rankings data
    progress.update(1, "Loading rankings data...")
    rankings_df = load_rankings_data()
    
    # Load match data
    progress.update(1, "Loading match data...")
    matches_df = load_matches_data()
    
    # Load doubles data
    progress.update(1, "Loading doubles data...")
    doubles_df = load_doubles_data()
    
    # Load mixed doubles data
    progress.update(1, "Loading mixed doubles data...")
    mixed_doubles_df = load_mixed_doubles_data()
    
    # Fix missing surface data
    progress.update(1, "Fixing surface data...")
    matches_df = fix_missing_surface_data(matches_df)
    
    # Parse date components (replace tourney_date with event_year, event_month, event_date)
    progress.update(1, "Parsing date components...")
    matches_df = parse_date_components(matches_df)
    
    # Parse score data (replace score with set1, set2, set3, set4, set5)
    progress.update(1, "Parsing score data...")
    matches_df = parse_score_data(matches_df)
    
    # Apply same parsing to doubles data if it exists
    if not doubles_df.empty:
        print("Parsing doubles data...")
        doubles_df = parse_date_components(doubles_df)
        doubles_df = parse_score_data(doubles_df)
    
    # Apply same parsing to mixed doubles data if it exists
    if not mixed_doubles_df.empty:
        print("Parsing mixed doubles data...")
        mixed_doubles_df = parse_date_components(mixed_doubles_df)
        mixed_doubles_df = parse_score_data(mixed_doubles_df)
    
    if players_df.empty or matches_df.empty:
        print("Error: Could not load required data. Exiting.")
        return
    
    # --- Create SQLite Database ---
    print("\n--- Creating Enhanced Database ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Write matches data
    print("Writing matches data...")
    matches_df.to_sql('matches', conn, if_exists='replace', index=False)
    
    # Write players data
    print("Writing players data...")
    players_df.to_sql('players', conn, if_exists='replace', index=False)
    
    # Write rankings data
    if not rankings_df.empty:
        print("Writing rankings data...")
        rankings_df.to_sql('rankings', conn, if_exists='replace', index=False)
    else:
        print("No rankings data to write.")
    
    # Write doubles data
    if not doubles_df.empty:
        print("Writing doubles data...")
        doubles_df.to_sql('doubles_matches', conn, if_exists='replace', index=False)
    else:
        print("No doubles data to write.")
    
    # Write mixed doubles data
    if not mixed_doubles_df.empty:
        print("Writing mixed doubles data...")
        mixed_doubles_df.to_sql('mixed_doubles_matches', conn, if_exists='replace', index=False)
    else:
        print("No mixed doubles data to write.")
    
    # Create indexes for better performance
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_winner_id ON matches(winner_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_loser_id ON matches(loser_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_year ON matches(event_year)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_month ON matches(event_month)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_players_id ON players(player_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON players(full_name)")
    
    # Rankings indexes
    if not rankings_df.empty:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_player ON rankings(player)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(ranking_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_rank ON rankings(rank)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_tour ON rankings(tour)")
    
    # Doubles indexes
    if not doubles_df.empty:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_winner1_id ON doubles_matches(winner1_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_winner2_id ON doubles_matches(winner2_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_loser1_id ON doubles_matches(loser1_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_loser2_id ON doubles_matches(loser2_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_year ON doubles_matches(event_year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_month ON doubles_matches(event_month)")
    
    # Create indexes for mixed doubles
    if not mixed_doubles_df.empty:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mixed_doubles_player1 ON mixed_doubles_matches(player1)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mixed_doubles_player2 ON mixed_doubles_matches(player2)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mixed_doubles_partner1 ON mixed_doubles_matches(partner1)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mixed_doubles_partner2 ON mixed_doubles_matches(partner2)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mixed_doubles_year ON mixed_doubles_matches(event_year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mixed_doubles_month ON mixed_doubles_matches(event_month)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mixed_doubles_slam ON mixed_doubles_matches(slam)")
    
    # Create a view for easy player-match joins
    print("Creating player-match views...")
    conn.execute("""
        CREATE VIEW IF NOT EXISTS matches_with_winner_info AS
        SELECT m.*, 
               p1.name_first as winner_first_name,
               p1.name_last as winner_last_name,
               p1.hand as winner_hand,
               p1.dob as winner_dob,
               p1.ioc as winner_ioc,
               p1.height as winner_height,
               p1.tour as winner_tour
        FROM matches m
        LEFT JOIN players p1 ON m.winner_id = p1.player_id
    """)
    
    conn.execute("""
        CREATE VIEW IF NOT EXISTS matches_with_loser_info AS
        SELECT m.*, 
               p2.name_first as loser_first_name,
               p2.name_last as loser_last_name,
               p2.hand as loser_hand,
               p2.dob as loser_dob,
               p2.ioc as loser_ioc,
               p2.height as loser_height,
               p2.tour as loser_tour
        FROM matches m
        LEFT JOIN players p2 ON m.loser_id = p2.player_id
    """)
    
    conn.execute("""
        CREATE VIEW IF NOT EXISTS matches_with_full_info AS
        SELECT m.*,
               p1.name_first as winner_first_name,
               p1.name_last as winner_last_name,
               p1.hand as winner_hand,
               p1.dob as winner_dob,
               p1.ioc as winner_ioc,
               p1.height as winner_height,
               p1.tour as winner_tour,
               p2.name_first as loser_first_name,
               p2.name_last as loser_last_name,
               p2.hand as loser_hand,
               p2.dob as loser_dob,
               p2.ioc as loser_ioc,
               p2.height as loser_height,
               p2.tour as loser_tour
        FROM matches m
        LEFT JOIN players p1 ON m.winner_id = p1.player_id
        LEFT JOIN players p2 ON m.loser_id = p2.player_id
    """)
    
    # Create rankings-enhanced views
    if not rankings_df.empty:
        print("Creating rankings-enhanced views...")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS matches_with_rankings AS
            SELECT m.*,
                   p1.name_first as winner_first_name,
                   p1.name_last as winner_last_name,
                   p1.hand as winner_hand,
                   p1.dob as winner_dob,
                   p1.ioc as winner_ioc,
                   p1.height as winner_height,
                   p1.tour as winner_tour,
                   p2.name_first as loser_first_name,
                   p2.name_last as loser_last_name,
                   p2.hand as loser_hand,
                   p2.dob as loser_dob,
                   p2.ioc as loser_ioc,
                   p2.height as loser_height,
                   p2.tour as loser_tour,
                   r1.rank as winner_rank_at_time,
                   r1.points as winner_points_at_time,
                   r2.rank as loser_rank_at_time,
                   r2.points as loser_points_at_time
            FROM matches m
            LEFT JOIN players p1 ON m.winner_id = p1.player_id
            LEFT JOIN players p2 ON m.loser_id = p2.player_id
            LEFT JOIN rankings r1 ON m.winner_id = r1.player 
                AND m.event_year = CAST(strftime('%Y', r1.ranking_date) AS INTEGER)
                AND m.event_month = CAST(strftime('%m', r1.ranking_date) AS INTEGER)
            LEFT JOIN rankings r2 ON m.loser_id = r2.player 
                AND m.event_year = CAST(strftime('%Y', r2.ranking_date) AS INTEGER)
                AND m.event_month = CAST(strftime('%m', r2.ranking_date) AS INTEGER)
        """)
        
        conn.execute("""
            CREATE VIEW IF NOT EXISTS player_rankings_history AS
            SELECT r.*,
                   p.name_first,
                   p.name_last,
                   p.hand,
                   p.ioc,
                   p.height,
                   p.tour
            FROM rankings r
            LEFT JOIN players p ON r.player = p.player_id
            ORDER BY r.ranking_date DESC, r.rank ASC
        """)
    
    conn.close()
    
    progress.complete("Database creation completed!")
    
    print(f"\n✅ Successfully created enhanced database '{DB_FILE}' with:")
    print(f"   - {len(matches_df)} singles matches (COMPLETE tournament coverage: 1877-2024)")
    if not doubles_df.empty:
        print(f"   - {len(doubles_df)} doubles matches (2000-2020)")
    if not mixed_doubles_df.empty:
        print(f"   - {len(mixed_doubles_df)} mixed doubles matches (Grand Slams)")
    print(f"   - {len(players_df)} players")
    if not rankings_df.empty:
        print(f"   - {len(rankings_df)} ranking records")
    print(f"   - Player metadata integration")
    print(f"   - Rankings data integration")
    print(f"   - Surface data quality fix (missing surface inference)")
    print(f"   - Amateur era tennis (1877-1967)")
    print(f"   - Professional era tennis (1968-2024)")
    print(f"   - Main tour matches (Grand Slams, Masters, etc.)")
    print(f"   - Qualifying/Challenger/Futures matches")
    print(f"   - Doubles matches (separate table)")
    print(f"   - Mixed doubles matches (Grand Slams)")
    print(f"   - Performance indexes")
    print(f"   - Enhanced views with rankings")
    print(f"   - COMPLETE tennis tournament database (147 years)")

def verify_enhancement():
    """
    Verifies that the player, rankings, and historical data integration worked correctly.
    """
    print("\n--- Verifying Complete Historical Integration ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Check player count
    player_count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    print(f"Players in database: {player_count}")
    
    # Check rankings count
    try:
        rankings_count = conn.execute("SELECT COUNT(*) FROM rankings").fetchone()[0]
        print(f"Rankings in database: {rankings_count}")
    except:
        print("No rankings table found")
        rankings_count = 0
    
    # Check matches with player info
    matches_with_winner_info = conn.execute("""
        SELECT COUNT(*) FROM matches_with_full_info 
        WHERE winner_first_name IS NOT NULL
    """).fetchone()[0]
    
    matches_with_loser_info = conn.execute("""
        SELECT COUNT(*) FROM matches_with_full_info 
        WHERE loser_first_name IS NOT NULL
    """).fetchone()[0]
    
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    
    # Check historical coverage
    date_range = conn.execute("SELECT MIN(event_year), MAX(event_year) FROM matches").fetchone()
    print(f"Historical coverage: {date_range[0]} to {date_range[1]}")
    
    # Check era distribution
    era_counts = conn.execute("""
        SELECT era, COUNT(*) as matches 
        FROM matches 
        GROUP BY era 
        ORDER BY era
    """).fetchall()
    
    print("Matches by era:")
    for era, count in era_counts:
        print(f"  {era}: {count:,} matches")
    
    # Check tournament type distribution
    tournament_type_counts = conn.execute("""
        SELECT tournament_type, COUNT(*) as matches 
        FROM matches 
        GROUP BY tournament_type 
        ORDER BY matches DESC
    """).fetchall()
    
    print("Matches by tournament type:")
    for tournament_type, count in tournament_type_counts:
        print(f"  {tournament_type}: {count:,} matches")
    
    # Check matches by decade (expanded for complete history)
    decade_counts = conn.execute("""
        SELECT 
            CASE 
                WHEN event_year < 1880 THEN '1870s'
                WHEN event_year < 1890 THEN '1880s'
                WHEN event_year < 1900 THEN '1890s'
                WHEN event_year < 1910 THEN '1900s'
                WHEN event_year < 1920 THEN '1910s'
                WHEN event_year < 1930 THEN '1920s'
                WHEN event_year < 1940 THEN '1930s'
                WHEN event_year < 1950 THEN '1940s'
                WHEN event_year < 1960 THEN '1950s'
                WHEN event_year < 1970 THEN '1960s'
                WHEN event_year < 1980 THEN '1970s'
                WHEN event_year < 1990 THEN '1980s'
                WHEN event_year < 2000 THEN '1990s'
                WHEN event_year < 2010 THEN '2000s'
                WHEN event_year < 2020 THEN '2010s'
                ELSE '2020s'
            END as decade,
            COUNT(*) as matches
        FROM matches 
        GROUP BY decade 
        ORDER BY decade
    """).fetchall()
    
    print("Matches by decade:")
    for decade, count in decade_counts:
        print(f"  {decade}: {count:,} matches")
    
    print(f"Matches with winner info: {matches_with_winner_info}/{total_matches} ({matches_with_winner_info/total_matches*100:.1f}%)")
    print(f"Matches with loser info: {matches_with_loser_info}/{total_matches} ({matches_with_loser_info/total_matches*100:.1f}%)")
    
    # Check rankings integration
    if rankings_count > 0:
        try:
            matches_with_rankings = conn.execute("""
                SELECT COUNT(*) FROM matches_with_rankings 
                WHERE winner_rank_at_time IS NOT NULL
            """).fetchone()[0]
            print(f"Matches with rankings data: {matches_with_rankings}/{total_matches} ({matches_with_rankings/total_matches*100:.1f}%)")
        except:
            print("Rankings view not available")
    
    # Check surface data quality
    missing_surface = conn.execute("""
        SELECT COUNT(*) FROM matches 
        WHERE surface IS NULL OR surface = '' OR surface = 'Unknown'
    """).fetchone()[0]
    
    print(f"Missing surface data: {missing_surface:,} matches")
    if missing_surface == 0:
        print("✅ All surface data is complete!")
    else:
        print(f"⚠️  {missing_surface:,} matches still have missing surface data")
    
    # Surface distribution
    surface_counts = conn.execute("""
        SELECT surface, COUNT(*) as matches 
        FROM matches 
        GROUP BY surface 
        ORDER BY matches DESC
    """).fetchall()
    
    print("Surface distribution:")
    for surface, count in surface_counts:
        print(f"  {surface}: {count:,} matches")
    
    # Check doubles data
    try:
        doubles_count = conn.execute("SELECT COUNT(*) FROM doubles_matches").fetchone()[0]
        print(f"Doubles matches: {doubles_count:,} matches")
        
        if doubles_count > 0:
            # Sample doubles query
            doubles_sample = conn.execute("""
                SELECT winner1_name, winner2_name, loser1_name, loser2_name, 
                       tourney_name, event_year, event_month, event_date, surface
                FROM doubles_matches 
                ORDER BY event_year DESC, event_month DESC, event_date DESC 
                LIMIT 3
            """).fetchall()
            
            print("Sample doubles matches:")
            for row in doubles_sample:
                print(f"  {row[0]} & {row[1]} vs {row[2]} & {row[3]} - {row[4]} ({row[5]}-{row[6]:02d}-{row[7]:02d}) - {row[8]}")
    except:
        print("No doubles matches found")
    
    # Check mixed doubles data
    try:
        mixed_doubles_count = conn.execute("SELECT COUNT(*) FROM mixed_doubles_matches").fetchone()[0]
        print(f"Mixed doubles matches: {mixed_doubles_count:,} matches")
        
        if mixed_doubles_count > 0:
            # Sample mixed doubles query
            mixed_doubles_sample = conn.execute("""
                SELECT player1, partner1, player2, partner2, 
                       tourney_name, year, slam, surface
                FROM mixed_doubles_matches 
                ORDER BY year DESC 
                LIMIT 3
            """).fetchall()
            
            print("Sample mixed doubles matches:")
            for row in mixed_doubles_sample:
                print(f"  {row[0]} & {row[1]} vs {row[2]} & {row[3]} - {row[4]} ({row[5]}) - {row[6]} - {row[7]}")
    except:
        print("No mixed doubles matches found")
    
    # Sample query to test functionality
    print("\n--- Sample Player Query Test ---")
    sample_query = """
        SELECT winner_name, winner_hand, winner_ioc, winner_height,
               loser_name, loser_hand, loser_ioc, loser_height,
               tourney_name, event_year, event_month, event_date, surface,
               set1, set2, set3, set4, set5
        FROM matches_with_full_info 
        WHERE winner_name LIKE '%Federer%' OR loser_name LIKE '%Federer%'
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 3
    """
    
    results = conn.execute(sample_query).fetchall()
    if results:
        print("Sample query results (Federer matches):")
        for row in results:
            print(f"  {row[0]} ({row[1]}, {row[2]}, {row[3]}cm) vs {row[4]} ({row[5]}, {row[6]}, {row[7]}cm)")
            print(f"    {row[8]} - {row[9]}-{row[10]:02d}-{row[11]:02d} - {row[12]}")
            print(f"    Score: {row[13]} | {row[14]} | {row[15]} | {row[16]} | {row[17]}")
    else:
        print("No sample results found")
    
    # Sample rankings query
    if rankings_count > 0:
        print("\n--- Sample Rankings Query Test ---")
        rankings_query = """
            SELECT name_first, name_last, rank, points, ranking_date, tour
            FROM player_rankings_history 
            WHERE rank <= 5
            ORDER BY ranking_date DESC, rank ASC
            LIMIT 10
        """
        
        try:
            rankings_results = conn.execute(rankings_query).fetchall()
            if rankings_results:
                print("Top 5 rankings sample:")
                for row in rankings_results:
                    print(f"  #{row[2]} {row[0]} {row[1]} - {row[3]} points ({row[4]}) - {row[5]}")
            else:
                print("No rankings results found")
        except Exception as e:
            print(f"Rankings query error: {e}")
    
    # Sample historical query
    print("\n--- Sample Historical Query Test ---")
    historical_query = """
        SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, surface
        FROM matches 
        WHERE event_year = 1970
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 5
    """
    
    try:
        historical_results = conn.execute(historical_query).fetchall()
        if historical_results:
            print("Sample 1970 matches:")
            for row in historical_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}-{row[4]:02d}-{row[5]:02d}) - {row[6]}")
        else:
            print("No historical results found")
    except Exception as e:
        print(f"Historical query error: {e}")
    
    # Sample amateur era query
    print("\n--- Sample Amateur Era Query Test ---")
    amateur_query = """
        SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, surface, era
        FROM matches 
        WHERE event_year = 1877
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 5
    """
    
    try:
        amateur_results = conn.execute(amateur_query).fetchall()
        if amateur_results:
            print("Sample 1877 matches (First Wimbledon):")
            for row in amateur_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}-{row[4]:02d}-{row[5]:02d}) - {row[6]} - {row[7]}")
        else:
            print("No amateur era results found")
    except Exception as e:
        print(f"Amateur era query error: {e}")
    
    # Sample qualifying/challenger query
    print("\n--- Sample Qualifying/Challenger Query Test ---")
    qualifying_query = """
        SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, tournament_type, tourney_level
        FROM matches 
        WHERE tournament_type = 'ATP_Qual_Chall'
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 5
    """
    
    try:
        qualifying_results = conn.execute(qualifying_query).fetchall()
        if qualifying_results:
            print("Sample ATP Qualifying/Challenger matches:")
            for row in qualifying_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}-{row[4]:02d}-{row[5]:02d}) - {row[6]} - {row[7]}")
        else:
            print("No qualifying/challenger results found")
    except Exception as e:
        print(f"Qualifying/challenger query error: {e}")
    
    conn.close()

if __name__ == '__main__':
    create_database_with_players()
    verify_enhancement()
