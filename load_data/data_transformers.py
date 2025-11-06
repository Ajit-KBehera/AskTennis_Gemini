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


def standardize_tourney_level(level, tour=None, era=None):
    """
    Replace old tourney levels with new standardized levels.
    Uses TOURNEY_LEVEL_MAPPINGS to convert historical and variant level codes
    to standardized values.
    
    Args:
        level: The original tourney_level value
        tour: The tour (ATP or WTA) for context
        era: The era for historical context (optional)
    
    Returns:
        Standardized tourney_level value
    
    Examples:
        >>> standardize_tourney_level('T1', tour='WTA')
        'PM'
        >>> standardize_tourney_level('G', tour='ATP')
        'G'
        >>> standardize_tourney_level('D', tour='WTA')
        'BJK_Cup'
    """
    if pd.isna(level) or level == '':
        return level
    
    level_str = str(level).strip()
    
    # Special case: WTA D level → BJK_Cup
    if level_str == 'D' and tour == 'WTA':
        return 'BJK_Cup'
    
    # Direct mapping using TOURNEY_LEVEL_MAPPINGS
    if level_str in TOURNEY_LEVEL_MAPPINGS:
        return TOURNEY_LEVEL_MAPPINGS[level_str]
    
    # Handle unknown levels
    print(f"Warning: Unknown tourney_level '{level_str}' for tour '{tour}'")
    return level_str  # Keep as-is if unknown


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

