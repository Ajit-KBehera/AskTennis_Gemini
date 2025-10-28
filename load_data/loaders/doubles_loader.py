"""
Doubles data loader for AskTennis.
Handles loading and processing of ATP doubles match data.
"""

import pandas as pd
import os
import glob
from typing import List, Optional
from config.paths import DataPaths
from config.settings import VERBOSE_LOGGING
from core.progress_tracker import ProgressTracker


class DoublesLoader:
    """
    Loads doubles match data from ATP doubles files.
    
    Handles:
    - ATP doubles matches by year
    - Data cleaning and standardization
    - Match type classification
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the doubles loader.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        
    def load_all_doubles(self) -> pd.DataFrame:
        """
        Load all doubles match data from ATP files.
        
        Returns:
            Combined DataFrame with all doubles match data
        """
        if self.verbose:
            print("\n--- Loading Doubles Match Data ---")
        
        # Find all ATP doubles files
        doubles_files = glob.glob(os.path.join(self.paths.tennis_atp_dir, "atp_matches_doubles_*.csv"))
        
        if not doubles_files:
            if self.verbose:
                print("No doubles match files found.")
            return pd.DataFrame()
        
        if self.verbose:
            print(f"Loading ATP Doubles data ({len(doubles_files)} files)...")
        
        # Load doubles files with progress tracking
        doubles_dfs = self._load_doubles_with_progress(doubles_files)
        
        if not doubles_dfs:
            if self.verbose:
                print("No doubles data could be loaded.")
            return pd.DataFrame()
        
        # Combine all doubles data
        doubles_df = pd.concat(doubles_dfs, ignore_index=True)
        
        # Clean and standardize data
        doubles_df = self._clean_doubles_data(doubles_df)
        
        if self.verbose:
            print(f"ATP Doubles matches loaded: {len(doubles_df)}")
        
        return doubles_df
    
    def _load_doubles_with_progress(self, doubles_files: List[str]) -> List[pd.DataFrame]:
        """Load doubles files with progress tracking."""
        doubles_dfs = []
        
        # Initialize progress tracker
        progress = ProgressTracker(len(doubles_files), "Doubles Loading")
        
        for file_path in sorted(doubles_files):
            progress.update(1, f"Loading {os.path.basename(file_path)}...")
            
            try:
                df = self._load_single_doubles_file(file_path)
                if not df.empty:
                    doubles_dfs.append(df)
            except Exception as e:
                if self.verbose:
                    print(f"Error loading {file_path}: {e}")
        
        progress.complete("Doubles loading completed")
        return doubles_dfs
    
    def _load_single_doubles_file(self, file_path: str) -> pd.DataFrame:
        """Load a single doubles file."""
        df = pd.read_csv(file_path, low_memory=False, index_col=False)
        
        # Clean and standardize data
        df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
        df['match_type'] = 'Doubles'
        df['tour'] = 'ATP'  # Doubles data is from ATP source
        
        return df
    
    def _clean_doubles_data(self, doubles_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize doubles data.
        
        Args:
            doubles_df: Raw doubles data
            
        Returns:
            Cleaned doubles data
        """
        if doubles_df.empty:
            return doubles_df
        
        # Ensure required columns exist
        if 'match_type' not in doubles_df.columns:
            doubles_df['match_type'] = 'Doubles'
        
        if 'tour' not in doubles_df.columns:
            doubles_df['tour'] = 'ATP'
        
        # Clean date column
        doubles_df['tourney_date'] = pd.to_datetime(
            doubles_df['tourney_date'], format='%Y%m%d', errors='coerce'
        )
        
        # Remove rows with invalid dates
        doubles_df = doubles_df.dropna(subset=['tourney_date'])
        
        return doubles_df
    
    def get_doubles_stats(self, doubles_df: pd.DataFrame) -> dict:
        """
        Get statistics about loaded doubles matches.
        
        Args:
            doubles_df: Doubles data
            
        Returns:
            Dictionary with doubles statistics
        """
        if doubles_df.empty:
            return {
                'total_doubles_matches': 0,
                'date_range': None,
                'unique_tournaments': 0,
                'unique_players': 0
            }
        
        stats = {
            'total_doubles_matches': len(doubles_df),
            'date_range': {
                'start': doubles_df['tourney_date'].min(),
                'end': doubles_df['tourney_date'].max()
            },
            'unique_tournaments': doubles_df['tourney_name'].nunique() if 'tourney_name' in doubles_df.columns else 0,
            'unique_players': 0  # Would need to count unique players from winner/loser columns
        }
        
        # Count unique players if columns exist
        if 'winner_name' in doubles_df.columns and 'loser_name' in doubles_df.columns:
            all_players = pd.concat([
                doubles_df['winner_name'].dropna(),
                doubles_df['loser_name'].dropna()
            ])
            stats['unique_players'] = all_players.nunique()
        
        return stats
    
    def filter_doubles_by_year(self, doubles_df: pd.DataFrame, year: int) -> pd.DataFrame:
        """
        Filter doubles matches by year.
        
        Args:
            doubles_df: Doubles data
            year: Year to filter by
            
        Returns:
            Filtered doubles data
        """
        if doubles_df.empty:
            return pd.DataFrame()
        
        return doubles_df[doubles_df['tourney_date'].dt.year == year]
    
    def filter_doubles_by_tournament(self, doubles_df: pd.DataFrame, tournament_name: str) -> pd.DataFrame:
        """
        Filter doubles matches by tournament name.
        
        Args:
            doubles_df: Doubles data
            tournament_name: Tournament name to filter by
            
        Returns:
            Filtered doubles data
        """
        if doubles_df.empty or 'tourney_name' not in doubles_df.columns:
            return pd.DataFrame()
        
        return doubles_df[
            doubles_df['tourney_name'].str.contains(tournament_name, case=False, na=False)
        ]
    
    def get_doubles_by_player(self, doubles_df: pd.DataFrame, player_name: str) -> pd.DataFrame:
        """
        Get doubles matches for a specific player.
        
        Args:
            doubles_df: Doubles data
            player_name: Player name to search for
            
        Returns:
            Doubles matches involving the player
        """
        if doubles_df.empty:
            return pd.DataFrame()
        
        player_name = player_name.lower()
        
        # Search in winner and loser columns
        mask = (
            doubles_df['winner_name'].str.lower().str.contains(player_name, na=False) |
            doubles_df['loser_name'].str.lower().str.contains(player_name, na=False)
        )
        
        return doubles_df[mask]
    
    def __str__(self):
        """String representation."""
        return f"DoublesLoader(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"DoublesLoader(verbose={self.verbose}, paths={self.paths})"
