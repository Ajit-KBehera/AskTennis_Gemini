"""
Main data loader orchestration for AskTennis.
Coordinates the entire data loading process with progress tracking.
"""

import sys
import os
import pandas as pd
from typing import Optional, Dict, Any

# Add the parent directory to Python path to import tennis module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .progress_tracker import ProgressTracker
from config.settings import (
    YEARS, 
    RECENT_YEARS, 
    LOAD_RECENT_ONLY,
    VERBOSE_LOGGING
)
from config.paths import DataPaths
from loaders import PlayersLoader, RankingsLoader, MatchesLoader, DoublesLoader
from processors import DateProcessor, ScoreProcessor, SurfaceProcessor, LevelProcessor
from database import DatabaseCreator, DatabaseVerifier


class DataLoader:
    """
    Main orchestration class for loading tennis data.
    
    Coordinates the entire data loading process including:
    - Player data loading
    - Rankings data loading  
    - Match data loading
    - Doubles data loading
    - Data processing and transformation
    - Database creation and verification
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the data loader.
        
        Args:
            verbose (bool): Enable verbose logging (defaults to config setting)
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        self.progress: Optional[ProgressTracker] = None
        
        # Data storage
        self.players_df = None
        self.rankings_df = None
        self.matches_df = None
        self.doubles_df = None
        
        # Processing results
        self.processed_matches_df = None
        self.processed_doubles_df = None
        
    def load_all_data(self, recent_only: bool = None) -> Dict[str, Any]:
        """
        Load all tennis data with progress tracking.
        
        Args:
            recent_only (bool): Load only recent years (defaults to config setting)
            
        Returns:
            Dict containing all loaded dataframes and metadata
        """
        if recent_only is None:
            recent_only = LOAD_RECENT_ONLY
            
        years_to_load = RECENT_YEARS if recent_only else YEARS
        
        print(f"=== AskTennis Data Loading ===")
        print(f"Loading data for years: {years_to_load[0]}-{years_to_load[-1]}")
        print(f"Total years: {len(years_to_load)}")
        print(f"Verbose logging: {self.verbose}")
        
        # Initialize progress tracker for main steps
        main_steps = 9  # players, rankings, matches, doubles, surface_fix, date_parsing, score_parsing, tourney_level_standardization, database_creation
        self.progress = ProgressTracker(main_steps, "Data Loading")
        
        try:
            # Load player data
            self.progress.update(1, "Loading player data...")
            self.players_df = self._load_players_data()
            
            # Load rankings data
            self.progress.update(1, "Loading rankings data...")
            self.rankings_df = self._load_rankings_data(years_to_load)
            
            # Load match data
            self.progress.update(1, "Loading match data...")
            self.matches_df = self._load_matches_data(years_to_load)
            
            # Load doubles data
            self.progress.update(1, "Loading doubles data...")
            self.doubles_df = self._load_doubles_data(years_to_load)
            
            # Process data
            self.progress.update(1, "Processing match data...")
            self.processed_matches_df = self._process_matches_data()
            
            self.progress.update(1, "Processing doubles data...")
            self.processed_doubles_df = self._process_doubles_data()
            
            # Create database
            self.progress.update(1, "Creating database...")
            self._create_database()
            
            # Verify database
            self.progress.update(1, "Verifying database...")
            self._verify_database()
            
            self.progress.complete("All data loaded successfully!")
            
            return self._get_results_summary()
            
        except Exception as e:
            if self.progress:
                self.progress.complete(f"Error occurred: {str(e)}")
            raise
    
    def _load_players_data(self):
        """Load player data using PlayersLoader."""
        if self.verbose:
            print("  Loading players data...")
        
        loader = PlayersLoader(verbose=self.verbose)
        return loader.load_all_players()
    
    def _load_rankings_data(self, years):
        """Load rankings data using RankingsLoader."""
        if self.verbose:
            print(f"  Loading rankings data for {len(years)} years...")
        
        loader = RankingsLoader(verbose=self.verbose)
        return loader.load_all_rankings()
    
    def _load_matches_data(self, years):
        """Load match data using MatchesLoader."""
        if self.verbose:
            print(f"  Loading match data for {len(years)} years...")
        
        loader = MatchesLoader(verbose=self.verbose)
        return loader.load_all_matches(years)
    
    def _load_doubles_data(self, years):
        """Load doubles data using DoublesLoader."""
        if self.verbose:
            print(f"  Loading doubles data for {len(years)} years...")
        
        loader = DoublesLoader(verbose=self.verbose)
        return loader.load_all_doubles()
    
    def _process_matches_data(self):
        """Process match data using processor classes."""
        if self.verbose:
            print("  Processing match data...")
        
        if self.matches_df is None or self.matches_df.empty:
            return pd.DataFrame()
        
        # Fix missing surface data
        surface_processor = SurfaceProcessor(verbose=self.verbose)
        processed_matches = surface_processor.fix_missing_surface_data(self.matches_df)
        
        # Parse date components
        date_processor = DateProcessor(verbose=self.verbose)
        processed_matches = date_processor.parse_date_components(processed_matches)
        
        # Parse score data
        score_processor = ScoreProcessor(verbose=self.verbose)
        processed_matches = score_processor.parse_score_data(processed_matches)
        
        # Standardize tournament levels
        level_processor = LevelProcessor(verbose=self.verbose)
        processed_matches = level_processor.standardize_tourney_levels(processed_matches, 'Mixed')
        
        return processed_matches
    
    def _process_doubles_data(self):
        """Process doubles data using processor classes."""
        if self.verbose:
            print("  Processing doubles data...")
        
        if self.doubles_df is None or self.doubles_df.empty:
            return pd.DataFrame()
        
        # Parse date components
        date_processor = DateProcessor(verbose=self.verbose)
        processed_doubles = date_processor.parse_date_components(self.doubles_df)
        
        # Parse score data if score column exists
        if 'score' in processed_doubles.columns:
            score_processor = ScoreProcessor(verbose=self.verbose)
            processed_doubles = score_processor.parse_score_data(processed_doubles)
        elif self.verbose:
            print("  No 'score' column found in doubles data, skipping score parsing.")
        
        # Standardize tournament levels
        level_processor = LevelProcessor(verbose=self.verbose)
        processed_doubles = level_processor.standardize_tourney_levels(processed_doubles, 'ATP')
        
        return processed_doubles
    
    def _create_database(self):
        """Create database using DatabaseCreator."""
        if self.verbose:
            print("  Creating database...")
        
        creator = DatabaseCreator(verbose=self.verbose)
        success = creator.create_database_with_players(
            players_df=self.players_df,
            rankings_df=self.rankings_df,
            matches_df=self.processed_matches_df,
            doubles_df=self.processed_doubles_df
        )
        
        if not success:
            raise Exception("Database creation failed")
    
    def _verify_database(self):
        """Verify database using DatabaseVerifier."""
        if self.verbose:
            print("  Verifying database...")
        
        verifier = DatabaseVerifier(verbose=self.verbose)
        verification_results = verifier.verify_enhancement()
        
        if 'error' in verification_results:
            raise Exception(f"Database verification failed: {verification_results['error']}")
        
        return verification_results
    
    def _get_results_summary(self) -> Dict[str, Any]:
        """Get summary of loaded data."""
        return {
            'players_count': len(self.players_df) if self.players_df is not None else 0,
            'rankings_count': len(self.rankings_df) if self.rankings_df is not None else 0,
            'matches_count': len(self.matches_df) if self.matches_df is not None else 0,
            'doubles_count': len(self.doubles_df) if self.doubles_df is not None else 0,
            'processed_matches_count': len(self.processed_matches_df) if self.processed_matches_df is not None else 0,
            'processed_doubles_count': len(self.processed_doubles_df) if self.processed_doubles_df is not None else 0,
            'database_file': self.paths.main_database_file,
            'success': True
        }
    
    def get_progress_info(self) -> Dict[str, Any]:
        """Get current progress information."""
        if self.progress is None:
            return {'status': 'not_started'}
        
        return {
            'status': 'in_progress',
            'current_step': self.progress.current_step,
            'total_steps': self.progress.total_steps,
            'percentage': self.progress.percentage,
            'elapsed_time': self.progress.elapsed_time,
            'estimated_remaining_time': self.progress.estimated_remaining_time,
            'step_name': self.progress.step_name
        }
    
    def cancel_loading(self):
        """Cancel the current loading process."""
        if self.progress:
            self.progress.complete("Loading cancelled by user")
        print("Data loading cancelled.")
    
    def __str__(self):
        """String representation of the data loader."""
        return f"DataLoader(verbose={self.verbose}, progress={self.progress})"
    
    def __repr__(self):
        """Detailed string representation."""
        return (f"DataLoader(verbose={self.verbose}, "
                f"players_df={'loaded' if self.players_df is not None else 'not_loaded'}, "
                f"rankings_df={'loaded' if self.rankings_df is not None else 'not_loaded'}, "
                f"matches_df={'loaded' if self.matches_df is not None else 'not_loaded'}, "
                f"doubles_df={'loaded' if self.doubles_df is not None else 'not_loaded'})")
