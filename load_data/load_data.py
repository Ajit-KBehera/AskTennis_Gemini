"""
Main orchestrator for tennis data loading and database creation.

This module orchestrates the complete data loading pipeline:
1. Load data from CSV files (players, rankings, matches, doubles)
2. Transform data (parse dates, scores, fix surfaces, standardize levels)
3. Build database (create tables, indexes, views)
4. Verify database integrity

Usage:
    python -m load_data.load_data
    or
    python load_data/load_data.py
    or
    from load_data.load_data import create_database_with_players, verify_enhancement
"""

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
    3. Database creation with indexes and views
    """
    print("=== Enhanced Data Loading with COMPLETE Tournament Coverage (1877-2024) ===")
    
    # Initialize progress tracker for main steps
    main_steps = 9  # players, rankings, matches, doubles, surface_fix, date_parsing, score_parsing, tourney_level_standardization, database_creation
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
    
    if players_df.empty or matches_df.empty:
        print("Error: Could not load required data. Exiting.")
        return
    
    # Build database (create tables, indexes, views)
    progress.update(1, "Building database...")
    build_database(matches_df, players_df, rankings_df, doubles_df)
    
    progress.complete("Database creation completed!")
    
    print(f"\n✅ Successfully created enhanced database '{DB_FILE}' with:")
    print(f"   - {len(matches_df)} singles matches (COMPLETE tournament coverage: 1877-2024)")
    if not doubles_df.empty:
        print(f"   - {len(doubles_df)} doubles matches (2000-2020)")
    print(f"   - {len(players_df)} players")
    if not rankings_df.empty:
        print(f"   - {len(rankings_df)} ranking records")
    print(f"   - Player metadata integration")
    print(f"   - Rankings data integration")
    print(f"   - Surface data quality fix (missing surface inference)")
    print(f"   - Closed Era tennis (1877-1967)")
    print(f"   - Open Era tennis (1968-2024)")
    print(f"   - Main tour matches (Grand Slams, Masters, etc.)")
    print(f"   - Qualifying/Challenger/Futures matches")
    print(f"   - Doubles matches (separate table)")
    print(f"   - Performance indexes")
    print(f"   - Enhanced views with rankings")
    print(f"   - COMPLETE tennis tournament database (147 years)")


if __name__ == '__main__':
    create_database_with_players()
    verify_enhancement()
