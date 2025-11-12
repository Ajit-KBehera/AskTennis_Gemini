"""
Main orchestrator for tennis data loading and database creation.

This module orchestrates the complete data loading pipeline:
1. Load data from CSV files (players, rankings, matches, doubles)
2. Transform data (parse dates, scores, fix surfaces, standardize levels)
3. Build database (create tables)
4. Verify database integrity

Usage:
    python -m load_data.load_data
    or
    python load_data/load_data.py
    or
    from load_data.load_data import create_database_with_players, verify_enhancement
"""

import pandas as pd

# Handle imports for both direct execution and module import
try:
    # Try relative imports first (when run as module)
    from .data_loaders import (
        load_players_data,
        load_rankings_data,
        load_matches_data,
        load_doubles_data
    )
    from .data_transformers import (
        enrich_players_data,
        enrich_rankings_data,
        set_tour_column,
        categorize_match_types,
        enrich_matches_data,
        filter_matches_by_switches,
        parse_date_components,
        parse_score_data,
        fix_missing_surface_data,
        standardize_tourney_levels
    )
    from .database_builder import build_database
    from .database_verifier import verify_enhancement
    from .utils import ProgressTracker
    from .config import DB_FILE
except ImportError:
    # Fall back to absolute imports (when run directly)
    import sys
    import os
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from load_data.data_loaders import (
        load_players_data,
        load_rankings_data,
        load_matches_data,
        load_doubles_data
    )
    from load_data.data_transformers import (
        enrich_players_data,
        enrich_rankings_data,
        set_tour_column,
        categorize_match_types,
        enrich_matches_data,
        filter_matches_by_switches,
        parse_date_components,
        parse_score_data,
        fix_missing_surface_data,
        standardize_tourney_levels
    )
    from load_data.database_builder import build_database
    from load_data.database_verifier import verify_enhancement
    from load_data.utils import ProgressTracker
    from load_data.config import DB_FILE


def create_database_with_players():
    """
    Creates the enhanced database with COMPLETE tennis history (1877-2024), 
    including all tournament levels, player information, and rankings.
    
    This is the main orchestrator function that coordinates:
    1. Data loading from CSV files
    2. Data transformation and cleaning
    3. Database creation with tables
    """
    print("=== Enhanced Data Loading with COMPLETE Tournament Coverage (1877-2024) ===")
    
    # Initialize progress tracker for main steps
    main_steps = 12  # players_load, rankings_load, matches_load, doubles_load, players_enrich, rankings_enrich, matches_enrich, doubles_enrich, surface_fix, date_parsing, score_parsing, tourney_level_standardization, database_creation
    progress = ProgressTracker(main_steps, "Database Creation")
    
    # 1. Load raw data
    progress.update(1, "Loading player data...")
    atp_players_df, wta_players_df = load_players_data()
    
    progress.update(1, "Loading rankings data...")
    atp_rankings_df, wta_rankings_df = load_rankings_data()
    
    progress.update(1, "Loading match data...")
    matches_df = load_matches_data()
    
    progress.update(1, "Loading doubles data...")
    doubles_df = load_doubles_data()
    
    # 2. Transform/enrich data
    progress.update(1, "Enriching player data...")
    if not atp_players_df.empty:
        atp_players_df = enrich_players_data(atp_players_df, tour='ATP')
    if not wta_players_df.empty:
        wta_players_df = enrich_players_data(wta_players_df, tour='WTA')
    
    # Combine players temporarily for rankings enrichment (for player name lookup)
    # This is safe because player_id collisions are handled by tour separation in tables
    combined_players_df = pd.DataFrame()
    if not atp_players_df.empty and not wta_players_df.empty:
        combined_players_df = pd.concat([atp_players_df, wta_players_df], ignore_index=True)
    elif not atp_players_df.empty:
        combined_players_df = atp_players_df
    elif not wta_players_df.empty:
        combined_players_df = wta_players_df
    
    progress.update(1, "Enriching rankings data...")
    # Enrich ATP rankings (with player names from ATP players)
    if not atp_rankings_df.empty:
        atp_rankings_df = enrich_rankings_data(atp_rankings_df, tour='ATP', players_df=atp_players_df)
        if 'ranking_date' in atp_rankings_df.columns:
            print(f"ATP rankings date range: {atp_rankings_df['ranking_date'].min()} to {atp_rankings_df['ranking_date'].max()}")
    
    # Enrich WTA rankings (with player names from WTA players)
    if not wta_rankings_df.empty:
        wta_rankings_df = enrich_rankings_data(wta_rankings_df, tour='WTA', players_df=wta_players_df)
        if 'ranking_date' in wta_rankings_df.columns:
            print(f"WTA rankings date range: {wta_rankings_df['ranking_date'].min()} to {wta_rankings_df['ranking_date'].max()}")
    
    progress.update(1, "Enriching match data...")
    if not matches_df.empty:
        # Optimization: Set tour column first (needed for categorization)
        matches_df = set_tour_column(matches_df)
        # Categorize matches into tournament types (needs 'tour' column)
        matches_df = categorize_match_types(matches_df)
        # Then enrich with era, dates, etc. and fill remaining tournament_type with 'Main Tour'
        matches_df = enrich_matches_data(matches_df, fill_missing_tournament_type=True)
        # Filter based on switches
        matches_df = filter_matches_by_switches(matches_df)
    
    progress.update(1, "Enriching doubles data...")
    if not doubles_df.empty:
        doubles_df = enrich_matches_data(doubles_df, match_type='Doubles')
    
    # 3. Continue with existing transformations
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
        # Only parse score data if 'score' column exists
        if 'score' in doubles_df.columns:
            doubles_df = parse_score_data(doubles_df)
        else:
            print("  No 'score' column found in doubles data, skipping score parsing.")
    
    # Standardize tourney levels
    progress.update(1, "Standardizing tourney levels...")
    matches_df = standardize_tourney_levels(matches_df, 'Mixed')  # Mixed ATP/WTA data
    
    if not doubles_df.empty:
        doubles_df = standardize_tourney_levels(doubles_df, 'ATP')  # ATP doubles data
    
    if (atp_players_df.empty and wta_players_df.empty) or matches_df.empty:
        print("Error: Could not load required data. Exiting.")
        return
    
    # Build database (create tables)
    progress.update(1, "Building database...")
    build_database(matches_df, atp_players_df, wta_players_df, atp_rankings_df, wta_rankings_df, doubles_df)
    
    progress.complete("Database creation completed!")
    
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
    print(f"   - Player metadata integration")
    print(f"   - Rankings data integration")
    print(f"   - Surface data quality fix (missing surface inference)")
    print(f"   - Closed Era tennis (1877-1967)")
    print(f"   - Open Era tennis (1968-2024)")
    print(f"   - Main tour matches (Grand Slams, Masters, etc.)")
    print(f"   - Qualifying/Challenger/Futures matches")
    print(f"   - Doubles matches (separate table)")
    print(f"   - COMPLETE tennis tournament database (147 years)")


if __name__ == '__main__':
    create_database_with_players()
    verify_enhancement()
