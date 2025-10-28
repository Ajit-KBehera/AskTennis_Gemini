"""
Rankings data loader for AskTennis.
Handles loading and processing of ATP and WTA ranking data.
"""

import pandas as pd
import os
import glob
from typing import List, Optional
from config.paths import DataPaths
from config.settings import VERBOSE_LOGGING, PROGRESS_UPDATE_INTERVAL
from core.progress_tracker import ProgressTracker


class RankingsLoader:
    """
    Loads rankings data from ATP and WTA ranking files.
    
    Handles:
    - Decade-based ranking files (70s, 80s, 90s, etc.)
    - Current rankings files
    - Data cleaning and standardization
    - Tour classification
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the rankings loader.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        
    def load_all_rankings(self) -> pd.DataFrame:
        """
        Load all rankings data from ATP and WTA files.
        
        Returns:
            Combined DataFrame with all ranking data
        """
        if self.verbose:
            print("--- Loading Rankings Data ---")
        
        # Get all ranking files
        ranking_files = self._get_ranking_files()
        
        if not ranking_files:
            if self.verbose:
                print("No rankings data found!")
            return pd.DataFrame()
        
        # Load rankings with progress tracking
        all_rankings = self._load_rankings_with_progress(ranking_files)
        
        if not all_rankings:
            if self.verbose:
                print("No rankings data loaded!")
            return pd.DataFrame()
        
        # Combine and clean data
        rankings_df = self._combine_and_clean_rankings(all_rankings)
        
        if self.verbose:
            print(f"Total rankings loaded: {len(rankings_df)}")
            if not rankings_df.empty:
                print(f"Date range: {rankings_df['ranking_date'].min()} to {rankings_df['ranking_date'].max()}")
        
        return rankings_df
    
    def _get_ranking_files(self) -> List[str]:
        """Get list of all ranking files."""
        ranking_files = []
        
        # ATP ranking files
        atp_files = [
            "atp_rankings_70s.csv",
            "atp_rankings_80s.csv", 
            "atp_rankings_90s.csv",
            "atp_rankings_00s.csv",
            "atp_rankings_10s.csv",
            "atp_rankings_20s.csv",
            "atp_rankings_current.csv"
        ]
        
        # WTA ranking files
        wta_files = [
            "wta_rankings_80s.csv",
            "wta_rankings_90s.csv", 
            "wta_rankings_00s.csv",
            "wta_rankings_10s.csv",
            "wta_rankings_20s.csv",
            "wta_rankings_current.csv"
        ]
        
        # Check ATP files
        for filename in atp_files:
            file_path = os.path.join(self.paths.tennis_atp_dir, filename)
            if self.paths.file_exists(file_path):
                ranking_files.append(file_path)
            elif self.verbose:
                print(f"  File not found: {file_path}")
        
        # Check WTA files
        for filename in wta_files:
            file_path = os.path.join(self.paths.tennis_wta_dir, filename)
            if self.paths.file_exists(file_path):
                ranking_files.append(file_path)
            elif self.verbose:
                print(f"  File not found: {file_path}")
        
        return ranking_files
    
    def _load_rankings_with_progress(self, ranking_files: List[str]) -> List[pd.DataFrame]:
        """Load rankings files with progress tracking."""
        all_rankings = []
        
        # Initialize progress tracker
        progress = ProgressTracker(len(ranking_files), "Rankings Loading")
        
        for file_path in ranking_files:
            progress.update(1, f"Loading {os.path.basename(file_path)}...")
            
            try:
                df = self._load_single_ranking_file(file_path)
                if not df.empty:
                    all_rankings.append(df)
                    if self.verbose:
                        print(f"  Loaded {len(df)} ranking records")
                
            except Exception as e:
                if self.verbose:
                    print(f"  Error loading {file_path}: {e}")
        
        progress.complete("Rankings loading completed")
        return all_rankings
    
    def _load_single_ranking_file(self, file_path: str) -> pd.DataFrame:
        """Load a single ranking file."""
        df = pd.read_csv(file_path, index_col=False)
        
        # Determine tour based on file path
        if 'atp' in file_path.lower():
            df['tour'] = 'ATP'
        elif 'wta' in file_path.lower():
            df['tour'] = 'WTA'
        else:
            df['tour'] = 'Unknown'
        
        # Standardize column names
        if 'tours' in df.columns:
            df = df.rename(columns={'tours': 'tournaments'})
        else:
            df['tournaments'] = None
        
        return df
    
    def _combine_and_clean_rankings(self, all_rankings: List[pd.DataFrame]) -> pd.DataFrame:
        """Combine and clean all rankings data."""
        if not all_rankings:
            return pd.DataFrame()
        
        # Combine all rankings data
        rankings_df = pd.concat(all_rankings, ignore_index=True)
        
        # Clean and standardize data
        rankings_df = self._clean_rankings_data(rankings_df)
        
        return rankings_df
    
    def _clean_rankings_data(self, rankings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize rankings data.
        
        Args:
            rankings_df: Raw rankings data
            
        Returns:
            Cleaned rankings data
        """
        if rankings_df.empty:
            return rankings_df
        
        # Clean date column
        rankings_df['ranking_date'] = pd.to_datetime(
            rankings_df['ranking_date'], format='%Y%m%d', errors='coerce'
        )
        
        # Clean numeric columns
        rankings_df['rank'] = pd.to_numeric(rankings_df['rank'], errors='coerce')
        rankings_df['points'] = pd.to_numeric(rankings_df['points'], errors='coerce')
        rankings_df['player'] = pd.to_numeric(rankings_df['player'], errors='coerce')
        
        # Remove invalid data
        rankings_df = rankings_df.dropna(subset=['ranking_date', 'rank', 'player'])
        
        return rankings_df
    
    def get_rankings_stats(self, rankings_df: pd.DataFrame) -> dict:
        """
        Get statistics about loaded rankings.
        
        Args:
            rankings_df: Rankings data
            
        Returns:
            Dictionary with ranking statistics
        """
        if rankings_df.empty:
            return {
                'total_rankings': 0,
                'atp_rankings': 0,
                'wta_rankings': 0,
                'date_range': None,
                'unique_players': 0
            }
        
        stats = {
            'total_rankings': len(rankings_df),
            'atp_rankings': len(rankings_df[rankings_df['tour'] == 'ATP']),
            'wta_rankings': len(rankings_df[rankings_df['tour'] == 'WTA']),
            'date_range': {
                'start': rankings_df['ranking_date'].min(),
                'end': rankings_df['ranking_date'].max()
            },
            'unique_players': rankings_df['player'].nunique()
        }
        
        return stats
    
    def filter_rankings_by_date(self, rankings_df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter rankings by date range.
        
        Args:
            rankings_df: Rankings data
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Filtered rankings data
        """
        if rankings_df.empty:
            return pd.DataFrame()
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        mask = (
            (rankings_df['ranking_date'] >= start_date) & 
            (rankings_df['ranking_date'] <= end_date)
        )
        
        return rankings_df[mask]
    
    def get_top_rankings(self, rankings_df: pd.DataFrame, top_n: int = 10, tour: str = None) -> pd.DataFrame:
        """
        Get top N rankings.
        
        Args:
            rankings_df: Rankings data
            top_n: Number of top rankings to return
            tour: Filter by tour (ATP/WTA)
            
        Returns:
            Top rankings data
        """
        if rankings_df.empty:
            return pd.DataFrame()
        
        filtered_df = rankings_df.copy()
        
        # Filter by tour if specified
        if tour:
            filtered_df = filtered_df[filtered_df['tour'] == tour.upper()]
        
        # Get top N rankings for each date
        top_rankings = filtered_df[filtered_df['rank'] <= top_n]
        
        return top_rankings.sort_values(['ranking_date', 'rank'])
    
    def __str__(self):
        """String representation."""
        return f"RankingsLoader(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"RankingsLoader(verbose={self.verbose}, paths={self.paths})"
