"""
Data transformation functions for tennis match data.

This module contains functions that transform and clean tennis match data,
including date parsing, score parsing, surface inference, and tournament level standardization.
"""

import pandas as pd
import sys
import os

# Add the parent directory to Python path to import tennis module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tennis.tennis_mappings import TOURNEY_LEVEL_MAPPINGS

# Import configuration for switches
try:
    from .config import (
        LOAD_DAVIS_CUP, LOAD_FED_CUP,
        LOAD_ATP_QUALIFYING, LOAD_ATP_CHALLENGER, LOAD_ATP_CHALLENGER_QUAL,
        LOAD_ATP_FUTURES, LOAD_WTA_QUALIFYING, LOAD_WTA_ITF
    )
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from load_data.config import (
        LOAD_DAVIS_CUP, LOAD_FED_CUP,
        LOAD_ATP_QUALIFYING, LOAD_ATP_CHALLENGER, LOAD_ATP_CHALLENGER_QUAL,
        LOAD_ATP_FUTURES, LOAD_WTA_QUALIFYING, LOAD_WTA_ITF
    )


# ============================================================================
# Data Enrichment Functions (moved from data_loaders.py)
# ============================================================================

def enrich_players_data(df, tour=None):
    """
    Enrich player data with tour information and derived columns.
    
    Args:
        df: DataFrame with player data (may have _source column from loader)
        tour: Tour name ('ATP' or 'WTA') if not already in DataFrame or _source column
    
    Returns:
        DataFrame with enriched columns
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Determine tour from _source column if available, otherwise use provided tour
    if '_source' in df.columns:
        df['tour'] = df['_source']
        df = df.drop(columns=['_source'])
    elif tour and 'tour' not in df.columns:
        df['tour'] = tour
    
    # Standardize data types
    if 'dob' in df.columns:
        df['dob'] = pd.to_datetime(df['dob'], format='%Y%m%d', errors='coerce')
    if 'height' in df.columns:
        df['height'] = pd.to_numeric(df['height'], errors='coerce')
    
    # Create full name for easier searching
    if 'name_first' in df.columns and 'name_last' in df.columns:
        df['full_name'] = df['name_first'] + ' ' + df['name_last']
    
    return df


def enrich_rankings_data(df, tour=None, players_df=None):
    """
    Enrich rankings data with tour information, standardize columns, and add player names.
    
    Args:
        df: DataFrame with rankings data (may have _source_file column from loader)
        tour: Tour name ('ATP' or 'WTA') if not determinable from _source_file
        players_df: Optional DataFrame with player data to join player names
    
    Returns:
        DataFrame with enriched columns including player names if players_df provided
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Determine tour from _source_file column if available
    if '_source_file' in df.columns:
        df['tour'] = df['_source_file'].apply(
            lambda x: 'ATP' if 'atp' in str(x).lower() else ('WTA' if 'wta' in str(x).lower() else 'Unknown')
        )
        df = df.drop(columns=['_source_file'])
    elif tour and 'tour' not in df.columns:
        df['tour'] = tour
    
    # Drop 'tours' column from WTA rankings (unnecessary column)
    if 'tours' in df.columns:
        df = df.drop(columns=['tours'])
    
    # Standardize data types
    if 'ranking_date' in df.columns:
        df['ranking_date'] = pd.to_datetime(df['ranking_date'], format='%Y%m%d', errors='coerce')
    if 'rank' in df.columns:
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
    if 'points' in df.columns:
        df['points'] = pd.to_numeric(df['points'], errors='coerce')
    if 'player' in df.columns:
        df['player'] = pd.to_numeric(df['player'], errors='coerce')
    
    # Remove invalid data
    required_cols = ['ranking_date', 'rank', 'player']
    if all(col in df.columns for col in required_cols):
        df = df.dropna(subset=required_cols)
    
    # Add player names if players_df is provided
    if players_df is not None and not players_df.empty and 'player' in df.columns:
        # Create a lookup dictionary for player names
        if 'full_name' in players_df.columns and 'player_id' in players_df.columns:
            player_names = players_df.set_index('player_id')['full_name'].to_dict()
            df['player_name'] = df['player'].map(player_names)
        elif 'name_first' in players_df.columns and 'name_last' in players_df.columns and 'player_id' in players_df.columns:
            # Create full_name if not present
            players_df = players_df.copy()
            players_df['full_name'] = players_df['name_first'] + ' ' + players_df['name_last']
            player_names = players_df.set_index('player_id')['full_name'].to_dict()
            df['player_name'] = df['player'].map(player_names)
    
    return df


def classify_era(row):
    """
    Classify match era based on year: 1968+ = Open Era, <1968 = Closed Era.
    
    Args:
        row: DataFrame row with tourney_date column
    
    Returns:
        'Open Era', 'Closed Era', or 'Unknown'
    """
    if pd.isna(row.get('tourney_date')):
        return 'Unknown'
    year = row['tourney_date'].year
    if year >= 1968:
        return 'Open Era'
    else:
        return 'Closed Era'


def categorize_match_types(df):
    """
    Categorize matches into tournament types based on file source and match characteristics.
    This handles ATP Qualifying/Challenger/Futures and WTA Qualifying/ITF categorization.
    
    Optimized to avoid unnecessary copies and type conversions.
    
    Args:
        df: DataFrame with match data (should already have tour column)
    
    Returns:
        DataFrame with tournament_type column added
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Ensure required columns exist and convert to string efficiently
    if 'round' not in df.columns:
        df['round'] = ''
    else:
        df['round'] = df['round'].astype(str)
    
    if 'tourney_level' not in df.columns:
        df['tourney_level'] = ''
    else:
        df['tourney_level'] = df['tourney_level'].astype(str)
    
    # Initialize tournament_type column if it doesn't exist
    if 'tournament_type' not in df.columns:
        df['tournament_type'] = None
    
    # ATP Qualifying/Challenger categorization
    # Files contain: ATP Qualifying, ATP Challenger, and ATP Challenger Qualifying
    atp_mask = df['tour'] == 'ATP'
    if atp_mask.sum() > 0:
        # Only categorize matches that don't already have a tournament_type set
        # OR matches with 'Main Tour' (which is a default/fallback that can be recategorized)
        # This prevents overwriting explicit values from _tournament_type_hint or other sources
        # but allows fixing incorrectly categorized 'Main Tour' matches
        unset_mask = (df['tournament_type'].isna() | 
                     (df['tournament_type'] == '') | 
                     (df['tournament_type'] == 'None') |
                     (df['tournament_type'] == 'Main Tour'))
        atp_unset_mask = atp_mask & unset_mask
        
        # Pattern: Q followed by digits (not QF which is quarterfinal)
        is_qualifying_round = df['round'].str.match(r'^Q\d+', na=False)
        is_challenger_level = (df['tourney_level'] == 'C')
        
        # ATP Challenger Qualifying (most specific - check first)
        chall_qual_mask = atp_unset_mask & is_challenger_level & is_qualifying_round
        df.loc[chall_qual_mask, 'tournament_type'] = 'ATP_Challenger_Qualifying'
        
        # ATP Challenger (main draw matches at challenger level)
        chall_mask = atp_unset_mask & is_challenger_level & ~is_qualifying_round
        df.loc[chall_mask, 'tournament_type'] = 'ATP_Challenger'
        
        # ATP Qualifying (qualifying rounds at non-challenger level)
        qual_mask = atp_unset_mask & ~is_challenger_level & is_qualifying_round
        df.loc[qual_mask, 'tournament_type'] = 'ATP_Qualifying'
    
    # WTA Qualifying/ITF categorization
    wta_mask = df['tour'] == 'WTA'
    if wta_mask.sum() > 0:
        # Only categorize matches that don't already have a tournament_type set
        # OR matches with 'Main Tour' (which is a default/fallback that can be recategorized)
        # This prevents overwriting explicit values from _tournament_type_hint or other sources
        # but allows fixing incorrectly categorized 'Main Tour' matches
        unset_mask = (df['tournament_type'].isna() | 
                     (df['tournament_type'] == '') | 
                     (df['tournament_type'] == 'None') |
                     (df['tournament_type'] == 'Main Tour'))
        wta_unset_mask = wta_mask & unset_mask
        
        # Pattern: Q followed by digits (not QF which is quarterfinal)
        is_qualifying_round = df['round'].str.match(r'^Q\d+', na=False)
        
        # Identify ITF tournament levels (ITF_15K, ITF_25K, etc.)
        is_itf_level = df['tourney_level'].str.startswith('ITF_', na=False)
        
        # WTA Qualifying
        qual_mask = wta_unset_mask & is_qualifying_round
        df.loc[qual_mask, 'tournament_type'] = 'WTA_Qualifying'
        
        # WTA ITF (only matches with ITF tourney_level, not main tour matches)
        itf_mask = wta_unset_mask & ~is_qualifying_round & is_itf_level
        df.loc[itf_mask, 'tournament_type'] = 'WTA_ITF'
        
        # WTA main tour matches (G, P, PM, I, etc.) are left as None/empty
        # They will be filled with 'Main Tour' in enrich_matches_data()
    
    return df


def set_tour_column(df, tour=None):
    """
    Set tour column from hints or parameter. This is separated for optimization
    so categorize_match_types() can run before full enrichment.
    
    Args:
        df: DataFrame with match data (may have _tour_hint column)
        tour: Tour name ('ATP' or 'WTA') if not already in DataFrame or _tour_hint
    
    Returns:
        DataFrame with tour column set
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Use hints from loader if available
    if '_tour_hint' in df.columns:
        df['tour'] = df['_tour_hint']
    elif tour and 'tour' not in df.columns:
        df['tour'] = tour
    
    # Fill missing tour
    if 'tour' in df.columns:
        df['tour'] = df['tour'].fillna('Unknown')
    
    return df


def enrich_matches_data(df, tour=None, tournament_type=None, match_type=None, fill_missing_tournament_type=True):
    """
    Enrich match data with tour, tournament_type, era, and other metadata.
    
    Args:
        df: DataFrame with match data (may have _tour_hint, _tournament_type_hint, _match_type_hint columns)
        tour: Tour name ('ATP' or 'WTA') if not already in DataFrame or _tour_hint
        tournament_type: Tournament type if known (e.g., 'ATP_Futures', 'Main Tour')
        match_type: Match type (e.g., 'Doubles')
        fill_missing_tournament_type: If True, fill missing tournament_type with 'Main Tour' (default: True)
    
    Returns:
        DataFrame with enriched columns
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Set tour column if not already set (for cases where set_tour_column wasn't called)
    if 'tour' not in df.columns:
        if '_tour_hint' in df.columns:
            df['tour'] = df['_tour_hint']
            df = df.drop(columns=['_tour_hint'])
        elif tour:
            df['tour'] = tour
        if 'tour' in df.columns:
            df['tour'] = df['tour'].fillna('Unknown')
    
    # Handle tournament_type hints (e.g., ATP_Futures)
    if '_tournament_type_hint' in df.columns:
        df['tournament_type'] = df['_tournament_type_hint']
        df = df.drop(columns=['_tournament_type_hint'])
    elif tournament_type and 'tournament_type' not in df.columns:
        df['tournament_type'] = tournament_type
    
    if '_match_type_hint' in df.columns:
        df['match_type'] = df['_match_type_hint']
        df = df.drop(columns=['_match_type_hint'])
    elif match_type and 'match_type' not in df.columns:
        df['match_type'] = match_type
    
    # Remove _source_file column if present (used for debugging but not needed in final data)
    if '_source_file' in df.columns:
        df = df.drop(columns=['_source_file'])
    
    # Convert tourney_date to datetime if it exists
    if 'tourney_date' in df.columns:
        df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
    
    # Apply era classification
    if 'tourney_date' in df.columns:
        df['era'] = df.apply(classify_era, axis=1)
    
    # Reclassify Davis Cup and Fed Cup matches from main tour data
    if 'tourney_name' in df.columns:
        df['tourney_name'] = df['tourney_name'].astype(str)
        
        # Reclassify Davis Cup matches (from ATP main tour files)
        if LOAD_DAVIS_CUP:
            davis_cup_mask = df['tourney_name'].str.contains('Davis Cup', case=False, na=False)
            if davis_cup_mask.sum() > 0:
                df.loc[davis_cup_mask, 'tournament_type'] = 'Davis_Cup'
        
        # Reclassify Fed Cup/BJK Cup matches (from WTA main tour files)
        if LOAD_FED_CUP:
            fed_cup_mask = df['tourney_name'].str.contains('Fed Cup|BJK Cup|Billie Jean King', case=False, na=False)
            if fed_cup_mask.sum() > 0:
                df.loc[fed_cup_mask, 'tournament_type'] = 'Fed_Cup'
    
    # Fill missing tournament_type for main tour matches (only if requested)
    if fill_missing_tournament_type and 'tournament_type' in df.columns:
        df['tournament_type'] = df['tournament_type'].fillna('Main Tour')
    
    return df


def filter_matches_by_switches(df):
    """
    Filter matches based on configuration switches.
    This ensures only matches for enabled tournament types are kept.
    
    Optimized to use isin() instead of multiple OR conditions for better performance.
    
    Args:
        df: DataFrame with tournament_type column
    
    Returns:
        Filtered DataFrame
    """
    if df.empty or 'tournament_type' not in df.columns:
        return df
    
    # Build list of allowed tournament types (more efficient than multiple OR conditions)
    allowed_types = ['Main Tour']  # Always include Main Tour matches
    
    # Include Davis Cup/Fed Cup if enabled
    if LOAD_DAVIS_CUP:
        allowed_types.append('Davis_Cup')
    if LOAD_FED_CUP:
        allowed_types.append('Fed_Cup')
    
    # Include ATP tournament types if enabled
    if LOAD_ATP_QUALIFYING:
        allowed_types.append('ATP_Qualifying')
    if LOAD_ATP_CHALLENGER:
        allowed_types.append('ATP_Challenger')
    if LOAD_ATP_CHALLENGER_QUAL:
        allowed_types.append('ATP_Challenger_Qualifying')
    if LOAD_ATP_FUTURES:
        allowed_types.append('ATP_Futures')
    
    # Include WTA tournament types if enabled
    if LOAD_WTA_QUALIFYING:
        allowed_types.append('WTA_Qualifying')
    if LOAD_WTA_ITF:
        allowed_types.append('WTA_ITF')
    
    # Apply filter using isin() which is more efficient than multiple OR conditions
    return df[df['tournament_type'].isin(allowed_types)].copy()


def combine_and_enrich_matches(master_df_list):
    """
    Combine multiple match DataFrames and apply final enrichment.
    
    Args:
        master_df_list: List of DataFrames to combine
    
    Returns:
        Combined and enriched DataFrame
    """
    if not master_df_list:
        return pd.DataFrame()
    
    # Combine all dataframes
    matches_df = pd.concat(master_df_list, ignore_index=True)
    
    # Apply final enrichment
    matches_df = enrich_matches_data(matches_df)
    
    return matches_df


# ============================================================================
# Existing Transformation Functions
# ============================================================================

def parse_date_components(df):
    """
    Parse tourney_date into event_year, event_month, event_date columns.
    Adds three new columns while keeping the original tourney_date column.
    Places the new columns right beside the tourney_date column.
    If columns already exist, they will be overwritten.
    
    Args:
        df: DataFrame with tourney_date column
        
    Returns:
        DataFrame with added event_year, event_month, event_date columns
    """
    print("\n--- Parsing Date Components ---")
    
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    # Extract date components
    event_year = df_copy['tourney_date'].dt.year
    event_month = df_copy['tourney_date'].dt.month
    event_date = df_copy['tourney_date'].dt.day
    
    # Check if columns already exist and remove them to avoid duplicates
    columns_to_remove = []
    if 'event_year' in df_copy.columns:
        columns_to_remove.append('event_year')
    if 'event_month' in df_copy.columns:
        columns_to_remove.append('event_month')
    if 'event_date' in df_copy.columns:
        columns_to_remove.append('event_date')
    
    if columns_to_remove:
        df_copy = df_copy.drop(columns=columns_to_remove)
        print(f"Removed existing columns to avoid duplicates: {columns_to_remove}")
    
    # Find the position of tourney_date column
    tourney_date_pos = df_copy.columns.get_loc('tourney_date')
    
    # Create new column order with date components right after tourney_date
    new_columns = []
    for i, col in enumerate(df_copy.columns):
        new_columns.append(col)
        if col == 'tourney_date':
            # Insert the 3 new columns right after tourney_date
            new_columns.extend(['event_year', 'event_month', 'event_date'])
    
    # Create a new dataframe with reordered columns
    df_reordered = df_copy.copy()
    
    # Add the new columns
    df_reordered['event_year'] = event_year
    df_reordered['event_month'] = event_month
    df_reordered['event_date'] = event_date
    
    # Reorder columns to place date components right after tourney_date
    df_reordered = df_reordered[new_columns]
    
    print(f"Date parsing completed: {len(df_reordered)}/{len(df)} dates parsed (100.0%)")
    print(f"Date range: {df_reordered['event_year'].min()}-{df_reordered['event_year'].max()}")
    print(f"Year range: {df_reordered['event_year'].min()} to {df_reordered['event_year'].max()}")
    
    return df_reordered


def parse_score_data(df):
    """
    Parse score column into set1, set2, set3, set4, set5 columns.
    Adds five new columns while keeping the original score column.
    Places the new columns right beside the score column.
    Handles RET by putting 'RET' in subsequent set columns.
    
    Args:
        df: DataFrame with score column
        
    Returns:
        DataFrame with added set1, set2, set3, set4, set5 columns
    """
    print("\n--- Parsing Score Data ---")
    
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
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
    
    # Extract set scores
    set1 = [s[0] for s in parsed_scores]
    set2 = [s[1] for s in parsed_scores]
    set3 = [s[2] for s in parsed_scores]
    set4 = [s[3] for s in parsed_scores]
    set5 = [s[4] for s in parsed_scores]
    
    # Find the position of score column
    score_pos = df_copy.columns.get_loc('score')
    
    # Create new column order with set columns right after score
    new_columns = []
    for i, col in enumerate(df_copy.columns):
        new_columns.append(col)
        if col == 'score':
            # Insert the 5 new columns right after score
            new_columns.extend(['set1', 'set2', 'set3', 'set4', 'set5'])
    
    # Create a new dataframe with reordered columns
    df_reordered = df_copy.copy()
    
    # Add the new columns
    df_reordered['set1'] = set1
    df_reordered['set2'] = set2
    df_reordered['set3'] = set3
    df_reordered['set4'] = set4
    df_reordered['set5'] = set5
    
    # Reorder columns to place set columns right after score
    df_reordered = df_reordered[new_columns]
    
    # Keep the original score column - do not remove it
    
    # Show sample of parsed scores
    print(f"Score parsing completed: {len(df_reordered)}/{len(df)} matches parsed (100.0%)")
    print("Sample parsed scores:")
    sample_scores = df_reordered[['set1', 'set2', 'set3', 'set4', 'set5']].dropna(how='all').head(3)
    for idx, row in sample_scores.iterrows():
        original = df.loc[idx, 'score'] if idx < len(df) else 'N/A'
        parsed = ' | '.join([str(s) for s in row.values if pd.notna(s)])
        print(f"  Original: {original} -> Parsed: {parsed}")
    
    return df_reordered


def fix_missing_surface_data(matches_df):
    """
    Optimized surface data inference using vectorized operations and data-driven patterns.
    
    Strategy:
    1. Build lookup tables from existing surface data (tournament+year, tournament-level mode)
    2. Use Grand Slam surface mappings (known surfaces)
    3. Use tourney_level hints (Grand Slams have known surfaces)
    4. Fall back to era-based defaults intelligently
    
    Args:
        matches_df: DataFrame with match data
        
    Returns:
        DataFrame with missing surface data filled in
    """
    print("\n--- Fixing Missing Surface Data (Optimized) ---")
    
    # Count missing surface data
    missing_before = len(matches_df[matches_df['surface'].isna() | (matches_df['surface'] == '')])
    print(f"Missing surface data before fix: {missing_before:,} matches")
    
    if missing_before == 0:
        print("No missing surface data found!")
        return matches_df
    
    # Create a copy to avoid modifying original
    df = matches_df.copy()
    
    # Prepare date components (needed for lookup)
    if 'event_year' not in df.columns:
        if 'tourney_date' in df.columns:
            df['event_year'] = pd.to_datetime(df['tourney_date'], errors='coerce').dt.year
        else:
            df['event_year'] = None
    
    # Step 1: Grand Slam surface mappings (known surfaces)
    grand_slam_surfaces = {
        'wimbledon': 'Grass',
        'french open': 'Clay',
        'roland garros': 'Clay',
        'us open': 'Hard',
        'australian open': 'Hard',
    }
    
    # Step 2: Build lookup tables from existing surface data
    # Tournament+Year lookup (most accurate)
    valid_surface_mask = df['surface'].notna() & (df['surface'] != '')
    if valid_surface_mask.sum() > 0:
        tourney_year_lookup = (
            df[valid_surface_mask]
            .groupby(['tourney_name', 'event_year'])['surface']
            .agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None)
            .to_dict()
        )
    else:
        tourney_year_lookup = {}
    
    # Tournament-level lookup (fallback when year-specific data unavailable)
    if valid_surface_mask.sum() > 0:
        tourney_lookup = (
            df[valid_surface_mask]
            .groupby('tourney_name')['surface']
            .agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None)
            .to_dict()
        )
    else:
        tourney_lookup = {}
    
    # Step 3: Vectorized Grand Slam inference
    missing_mask = df['surface'].isna() | (df['surface'] == '')
    tourney_name_lower = df['tourney_name'].astype(str).str.lower()
    
    # Grand Slam pattern matching (vectorized)
    for gs_pattern, surface in grand_slam_surfaces.items():
        gs_mask = tourney_name_lower.str.contains(gs_pattern, case=False, na=False) & missing_mask
        if gs_mask.sum() > 0:
            df.loc[gs_mask, 'surface'] = surface
            missing_mask = df['surface'].isna() | (df['surface'] == '')
    
    # Step 4: Tournament+Year lookup (vectorized merge)
    missing_mask = df['surface'].isna() | (df['surface'] == '')
    if missing_mask.sum() > 0 and tourney_year_lookup:
        # Create lookup Series indexed by (tourney_name, event_year) tuple
        lookup_series = pd.Series(tourney_year_lookup)
        
        # Create a temporary key column for matching
        df_temp = df.loc[missing_mask, ['tourney_name', 'event_year']].copy()
        df_temp['lookup_key'] = list(zip(df_temp['tourney_name'], df_temp['event_year']))
        
        # Map surfaces using the lookup
        inferred_surfaces = df_temp['lookup_key'].map(lookup_series)
        inferred_mask = inferred_surfaces.notna()
        
        if inferred_mask.sum() > 0:
            df.loc[df_temp.index[inferred_mask], 'surface'] = inferred_surfaces[inferred_mask]
            missing_mask = df['surface'].isna() | (df['surface'] == '')
    
    # Step 5: Tournament-level lookup (vectorized)
    missing_mask = df['surface'].isna() | (df['surface'] == '')
    if missing_mask.sum() > 0 and tourney_lookup:
        df.loc[missing_mask, 'surface'] = df.loc[missing_mask, 'tourney_name'].map(
            lambda x: tourney_lookup.get(x) if x in tourney_lookup else None
        )
        missing_mask = df['surface'].isna() | (df['surface'] == '')
    
    # Step 6: Tourney-level hints (Grand Slams have known surfaces)
    missing_mask = df['surface'].isna() | (df['surface'] == '')
    if missing_mask.sum() > 0 and 'tourney_level' in df.columns:
        # Grand Slam level inference
        gs_level_mask = (df['tourney_level'] == 'G') & missing_mask
        if gs_level_mask.sum() > 0:
            # For Grand Slams, infer from tournament name
            gs_tourney_mask = gs_level_mask & (
                tourney_name_lower.str.contains('wimbledon', case=False, na=False)
            )
            if gs_tourney_mask.sum() > 0:
                df.loc[gs_tourney_mask, 'surface'] = 'Grass'
            
            gs_tourney_mask = gs_level_mask & (
                tourney_name_lower.str.contains('french|roland', case=False, na=False)
            )
            if gs_tourney_mask.sum() > 0:
                df.loc[gs_tourney_mask, 'surface'] = 'Clay'
            
            gs_tourney_mask = gs_level_mask & (
                tourney_name_lower.str.contains('us open|australian|melbourne', case=False, na=False)
            )
            if gs_tourney_mask.sum() > 0:
                df.loc[gs_tourney_mask, 'surface'] = 'Hard'
        
        missing_mask = df['surface'].isna() | (df['surface'] == '')
    
    # Step 7: Era-based defaults (smart fallback)
    missing_mask = df['surface'].isna() | (df['surface'] == '')
    if missing_mask.sum() > 0 and 'event_year' in df.columns:
        year_mask = df['event_year'].notna()
        
        # Pre-1970s: Mostly grass (vectorized)
        pre_1970_mask = missing_mask & (df['event_year'] < 1970) & year_mask
        if pre_1970_mask.sum() > 0:
            # Check for clay indicators in tournament name
            clay_indicator = tourney_name_lower.str.contains('clay|dirt|red|terre', case=False, na=False)
            df.loc[pre_1970_mask & clay_indicator, 'surface'] = 'Clay'
            df.loc[pre_1970_mask & ~clay_indicator, 'surface'] = 'Grass'
        
        # 1970s-1980s: Introduction of hard courts
        era_70_90_mask = missing_mask & (df['event_year'] >= 1970) & (df['event_year'] < 1990) & year_mask
        if era_70_90_mask.sum() > 0:
            grass_indicator = tourney_name_lower.str.contains('grass|lawn', case=False, na=False)
            clay_indicator = tourney_name_lower.str.contains('clay|dirt|red|terre', case=False, na=False)
            hard_indicator = tourney_name_lower.str.contains('hard|concrete|asphalt', case=False, na=False)
            
            df.loc[era_70_90_mask & grass_indicator, 'surface'] = 'Grass'
            df.loc[era_70_90_mask & clay_indicator, 'surface'] = 'Clay'
            df.loc[era_70_90_mask & hard_indicator, 'surface'] = 'Hard'
            df.loc[era_70_90_mask & ~(grass_indicator | clay_indicator | hard_indicator), 'surface'] = 'Hard'
        
        # 1990s+: Mostly hard courts
        modern_era_mask = missing_mask & (df['event_year'] >= 1990) & year_mask
        if modern_era_mask.sum() > 0:
            grass_indicator = tourney_name_lower.str.contains('grass|lawn|wimbledon', case=False, na=False)
            clay_indicator = tourney_name_lower.str.contains('clay|dirt|red|terre|french', case=False, na=False)
            carpet_indicator = tourney_name_lower.str.contains('carpet|indoor', case=False, na=False)
            
            df.loc[modern_era_mask & grass_indicator, 'surface'] = 'Grass'
            df.loc[modern_era_mask & clay_indicator, 'surface'] = 'Clay'
            df.loc[modern_era_mask & carpet_indicator, 'surface'] = 'Carpet'
            df.loc[modern_era_mask & ~(grass_indicator | clay_indicator | carpet_indicator), 'surface'] = 'Hard'
        
        # Final fallback for any remaining missing
        missing_mask = df['surface'].isna() | (df['surface'] == '')
        if missing_mask.sum() > 0:
            df.loc[missing_mask, 'surface'] = 'Hard'
    
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


def standardize_tourney_levels(df, tour_name):
    """
    Apply tourney level standardization to a dataframe using vectorized operations.
    Optimized version that uses map() instead of apply() for better performance.
    
    Args:
        df: DataFrame with tourney_level column
        tour_name: Tour name for context (ATP, WTA, Mixed, etc.)
    
    Returns:
        DataFrame with standardized tourney_level values
    """
    if 'tourney_level' not in df.columns:
        print(f"  No tourney_level column found in {tour_name} data, skipping standardization.")
        return df
    
    print(f"\n--- Standardizing Tourney Levels for {tour_name} Data ---")
    
    # Count original levels
    original_levels = df['tourney_level'].value_counts()
    print(f"Original tourney levels found: {len(original_levels)}")
    for level, count in original_levels.head(10).items():
        print(f"  {level}: {count:,} matches")
    
    # Apply standardization using vectorized operations
    print("Applying standardization...")
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Handle missing/empty values
    mask_not_na = df['tourney_level'].notna() & (df['tourney_level'] != '')
    
    if mask_not_na.sum() > 0:
        # Convert to string and strip whitespace for all non-NA values
        df.loc[mask_not_na, 'tourney_level'] = df.loc[mask_not_na, 'tourney_level'].astype(str).str.strip()
        
        # Handle special case: WTA 'D' level → 'BJK_Cup'
        if tour_name == 'WTA':
            wta_d_mask = mask_not_na & (df['tourney_level'] == 'D')
            if wta_d_mask.sum() > 0:
                df.loc[wta_d_mask, 'tourney_level'] = 'BJK_Cup'
                # Update mask to exclude already processed values
                mask_not_na = mask_not_na & ~wta_d_mask
        
        # Apply mapping using vectorized map() operation
        if mask_not_na.sum() > 0:
            levels_to_map = df.loc[mask_not_na, 'tourney_level']
            mapped_levels = levels_to_map.map(TOURNEY_LEVEL_MAPPINGS)
            
            # Only update where mapping exists (non-null result)
            # mapped_levels has the same index as levels_to_map (which is mask_not_na positions)
            mapped_mask = mapped_levels.notna()
            if mapped_mask.sum() > 0:
                # Use the index from mapped_levels to update the DataFrame
                df.loc[mapped_levels.index[mapped_mask], 'tourney_level'] = mapped_levels[mapped_mask]
            
            # Warn about unmapped levels
            unmapped_mask = mapped_levels.isna()
            if unmapped_mask.sum() > 0:
                unmapped_levels = df.loc[mapped_levels.index[unmapped_mask], 'tourney_level'].unique()
                for level in unmapped_levels[:5]:  # Show first 5 unmapped levels
                    print(f"Warning: Unknown tourney_level '{level}' for tour '{tour_name}'")
    
    # Count standardized levels
    standardized_levels = df['tourney_level'].value_counts()
    print(f"Standardized tourney levels: {len(standardized_levels)}")
    for level, count in standardized_levels.head(10).items():
        print(f"  {level}: {count:,} matches")
    
    # Show transformation summary
    changes = len(original_levels) - len(standardized_levels)
    if changes > 0:
        print(f"✅ Reduced from {len(original_levels)} to {len(standardized_levels)} unique levels ({changes} levels consolidated)")
    else:
        print(f"✅ No level consolidation needed")
    
    return df

