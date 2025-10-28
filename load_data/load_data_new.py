"""
New modular data loading system for AskTennis.
Replaces the original load_data.py with a clean, modular architecture.

This file demonstrates how to use the new modular components to achieve
the same functionality as the original load_data.py but with better
organization, maintainability, and testability.

Usage:
    python load_data_new.py

Features:
    - Complete tennis data loading (players, rankings, matches, doubles)
    - Data processing and transformation
    - Database creation with indexes and views
    - Data verification and quality assessment
    - Progress tracking and verbose logging
"""

import os
import sys
from typing import Optional, Dict, Any

# Add the parent directory to Python path to import tennis module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all modular components
from load_data import (
    DataLoader, ProgressTracker,
    DataPaths, YEARS, RECENT_YEARS, LOAD_RECENT_ONLY,
    PlayersLoader, RankingsLoader, MatchesLoader, DoublesLoader,
    DateProcessor, ScoreProcessor, SurfaceProcessor, LevelProcessor,
    DatabaseCreator, DatabaseVerifier, DatabaseManager
)


def main():
    """
    Main function that orchestrates the complete data loading process.
    Replicates the functionality of the original create_database_with_players().
    """
    print("=== AskTennis Modular Data Loading System ===")
    print("Using new modular architecture for better maintainability")
    print("=" * 60)
    
    # Initialize configuration
    paths = DataPaths()
    print(f"Project root: {paths.project_root}")
    print(f"Database file: {paths.main_database_file}")
    print(f"Years to load: {YEARS[0]}-{YEARS[-1]}")
    print(f"Load recent only: {LOAD_RECENT_ONLY}")
    
    try:
        # Initialize the main data loader
        print("\n--- Initializing DataLoader ---")
        data_loader = DataLoader(verbose=True)
        
        # Load all data using the modular system
        print("\n--- Loading All Data ---")
        results = data_loader.load_all_data(recent_only=LOAD_RECENT_ONLY)
        
        if results['status'] != 'success':
            print("❌ Data loading failed!")
            return False
        
        print(f"\n✅ Data loading completed successfully!")
        print(f"  - Players loaded: {results['players_count']:,}")
        print(f"  - Rankings loaded: {results['rankings_count']:,}")
        print(f"  - Matches loaded: {results['matches_count']:,}")
        print(f"  - Doubles loaded: {results['doubles_count']:,}")
        
        # Process the loaded data
        print("\n--- Processing Data ---")
        processed_matches = data_loader._process_matches_data()
        processed_doubles = data_loader._process_doubles_data()
        
        print(f"✅ Data processing completed!")
        print(f"  - Processed matches: {len(processed_matches):,}")
        print(f"  - Processed doubles: {len(processed_doubles):,}")
        
        # Create database
        print("\n--- Creating Database ---")
        data_loader._create_database()
        
        # Verify database
        print("\n--- Verifying Database ---")
        verification_results = data_loader._verify_database()
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE DATA LOADING PROCESS FINISHED!")
        print("=" * 60)
        
        # Print final summary
        print_final_summary(verification_results)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during data loading: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_final_summary(verification_results: Dict[str, Any]):
    """Print a comprehensive summary of the loaded data."""
    if 'error' in verification_results:
        print(f"❌ Verification failed: {verification_results['error']}")
        return
    
    print("\n📊 FINAL SUMMARY:")
    print("-" * 40)
    
    # Data counts
    counts = verification_results.get('data_counts', {})
    print(f"📈 Data Loaded:")
    print(f"  • Players: {counts.get('players', 0):,}")
    print(f"  • Rankings: {counts.get('rankings', 0):,}")
    print(f"  • Matches: {counts.get('matches', 0):,}")
    print(f"  • Doubles: {counts.get('doubles_matches', 0):,}")
    
    # Historical coverage
    coverage = verification_results.get('historical_coverage', {})
    if coverage.get('start_year') and coverage.get('end_year'):
        print(f"\n📅 Historical Coverage:")
        print(f"  • Period: {coverage['start_year']} - {coverage['end_year']}")
        print(f"  • Total years: {coverage['total_years']}")
    
    # Era distribution
    era_dist = verification_results.get('era_distribution', {})
    if era_dist:
        print(f"\n🏆 Era Distribution:")
        for era, count in era_dist.items():
            print(f"  • {era}: {count:,} matches")
    
    # Tournament types
    type_dist = verification_results.get('tournament_type_distribution', {})
    if type_dist:
        print(f"\n🎾 Tournament Types:")
        for tournament_type, count in list(type_dist.items())[:5]:  # Top 5
            print(f"  • {tournament_type}: {count:,} matches")
    
    # Data quality
    quality = verification_results.get('data_quality', {})
    if quality:
        completeness = quality.get('data_completeness', {})
        print(f"\n✅ Data Quality:")
        print(f"  • Surface completeness: {completeness.get('surface_completeness', 0):.1f}%")
        print(f"  • Score completeness: {completeness.get('score_completeness', 0):.1f}%")
        print(f"  • Level completeness: {completeness.get('level_completeness', 0):.1f}%")
    
    print(f"\n🎯 Database ready for AskTennis AI queries!")


def load_players_data():
    """
    Load player data using the modular PlayersLoader.
    Replicates the original load_players_data() function.
    """
    print("\n--- Loading Player Data (Modular) ---")
    loader = PlayersLoader(verbose=True)
    return loader.load_all_players()


def load_rankings_data():
    """
    Load rankings data using the modular RankingsLoader.
    Replicates the original load_rankings_data() function.
    """
    print("\n--- Loading Rankings Data (Modular) ---")
    loader = RankingsLoader(verbose=True)
    return loader.load_all_rankings()


def load_matches_data():
    """
    Load match data using the modular MatchesLoader.
    Replicates the original load_matches_data() function.
    """
    print("\n--- Loading Match Data (Modular) ---")
    loader = MatchesLoader(verbose=True)
    return loader.load_all_matches(YEARS)


def load_doubles_data():
    """
    Load doubles data using the modular DoublesLoader.
    Replicates the original load_doubles_data() function.
    """
    print("\n--- Loading Doubles Data (Modular) ---")
    loader = DoublesLoader(verbose=True)
    return loader.load_all_doubles()


def parse_date_components(df):
    """
    Parse date components using the modular DateProcessor.
    Replicates the original parse_date_components() function.
    """
    print("\n--- Parsing Date Components (Modular) ---")
    processor = DateProcessor(verbose=True)
    return processor.parse_date_components(df)


def parse_score_data(df):
    """
    Parse score data using the modular ScoreProcessor.
    Replicates the original parse_score_data() function.
    """
    print("\n--- Parsing Score Data (Modular) ---")
    processor = ScoreProcessor(verbose=True)
    return processor.parse_score_data(df)


def fix_missing_surface_data(df):
    """
    Fix missing surface data using the modular SurfaceProcessor.
    Replicates the original fix_missing_surface_data() function.
    """
    print("\n--- Fixing Surface Data (Modular) ---")
    processor = SurfaceProcessor(verbose=True)
    return processor.fix_missing_surface_data(df)


def standardize_tourney_levels(df, tour_name):
    """
    Standardize tournament levels using the modular LevelProcessor.
    Replicates the original standardize_tourney_levels() function.
    """
    print(f"\n--- Standardizing Tournament Levels (Modular) ---")
    processor = LevelProcessor(verbose=True)
    return processor.standardize_tourney_levels(df, tour_name)


def create_database_with_players():
    """
    Create database using the modular DatabaseCreator.
    Replicates the original create_database_with_players() function.
    """
    print("\n=== Creating Database with Modular Components ===")
    
    # Load all data
    players_df = load_players_data()
    rankings_df = load_rankings_data()
    matches_df = load_matches_data()
    doubles_df = load_doubles_data()
    
    if players_df.empty or matches_df.empty:
        print("❌ Error: Could not load required data. Exiting.")
        return False
    
    # Process data
    matches_df = fix_missing_surface_data(matches_df)
    matches_df = parse_date_components(matches_df)
    matches_df = parse_score_data(matches_df)
    matches_df = standardize_tourney_levels(matches_df, 'Mixed')
    
    if not doubles_df.empty:
        doubles_df = parse_date_components(doubles_df)
        if 'score' in doubles_df.columns:
            doubles_df = parse_score_data(doubles_df)
        doubles_df = standardize_tourney_levels(doubles_df, 'ATP')
    
    # Create database
    creator = DatabaseCreator(verbose=True)
    success = creator.create_database_with_players(
        players_df=players_df,
        rankings_df=rankings_df,
        matches_df=matches_df,
        doubles_df=doubles_df
    )
    
    if success:
        # Verify database
        verifier = DatabaseVerifier(verbose=True)
        verification_results = verifier.verify_enhancement()
        
        print_final_summary(verification_results)
        return True
    else:
        print("❌ Database creation failed!")
        return False


def verify_enhancement():
    """
    Verify database using the modular DatabaseVerifier.
    Replicates the original verify_enhancement() function.
    """
    print("\n--- Verifying Database Enhancement (Modular) ---")
    verifier = DatabaseVerifier(verbose=True)
    return verifier.verify_enhancement()


def demonstrate_modular_usage():
    """
    Demonstrate how to use individual modular components.
    Shows the flexibility and power of the new architecture.
    """
    print("\n=== Demonstrating Modular Component Usage ===")
    
    # Example 1: Using individual loaders
    print("\n--- Example 1: Individual Loaders ---")
    players_loader = PlayersLoader(verbose=False)
    players_df = players_loader.load_all_players()
    print(f"Players loaded: {len(players_df)}")
    
    # Example 2: Using individual processors
    print("\n--- Example 2: Individual Processors ---")
    if not players_df.empty:
        # Create sample data for processing
        import pandas as pd
        sample_data = pd.DataFrame({
            'tourney_date': pd.to_datetime(['2020-01-15', '2020-06-20']),
            'score': ['6-4 6-2', '6-3 4-6 6-1'],
            'surface': ['Hard', ''],
            'tourney_level': ['G', 'M']
        })
        
        # Process with different processors
        date_processor = DateProcessor(verbose=False)
        processed_dates = date_processor.parse_date_components(sample_data)
        print(f"Date processing: {len(processed_dates)} records processed")
        
        score_processor = ScoreProcessor(verbose=False)
        processed_scores = score_processor.parse_score_data(sample_data)
        print(f"Score processing: {len(processed_scores)} records processed")
        
        surface_processor = SurfaceProcessor(verbose=False)
        processed_surfaces = surface_processor.fix_missing_surface_data(sample_data)
        print(f"Surface processing: {len(processed_surfaces)} records processed")
    
    # Example 3: Using database manager
    print("\n--- Example 3: Database Manager ---")
    manager = DatabaseManager(verbose=False)
    
    # Check if database exists
    if os.path.exists("tennis_data.db"):
        tables = manager.get_all_tables("tennis_data.db")
        print(f"Database tables: {tables}")
        
        if 'matches' in tables:
            match_count = manager.get_table_row_count('matches', "tennis_data.db")
            print(f"Matches in database: {match_count:,}")
    else:
        print("No database found - run main() first to create one")


if __name__ == "__main__":
    """
    Main entry point for the modular data loading system.
    
    This script can be run in different modes:
    1. Full data loading: python load_data_new.py
    2. Individual functions: Import and use specific functions
    3. Demonstration: Call demonstrate_modular_usage()
    """
    
    print("AskTennis Modular Data Loading System")
    print("=====================================")
    print("Choose an option:")
    print("1. Run complete data loading process")
    print("2. Demonstrate modular component usage")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting complete data loading process...")
            success = main()
            if success:
                print("\n✅ Process completed successfully!")
            else:
                print("\n❌ Process failed!")
                
        elif choice == "2":
            print("\n🔧 Demonstrating modular components...")
            demonstrate_modular_usage()
            
        elif choice == "3":
            print("\n👋 Goodbye!")
            
        else:
            print("\n❌ Invalid choice. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
