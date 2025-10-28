"""
Tournament level processing utilities for AskTennis data loading.
Handles standardization of tournament levels across different tours.
"""

import pandas as pd
import sys
import os
from typing import Dict, Optional
from config.settings import VERBOSE_LOGGING

# Add the parent directory to Python path to import tennis module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tennis.tennis_core import standardize_tourney_level
except ImportError:
    # Fallback function if tennis module is not available
    def standardize_tourney_level(level, tour_name):
        """Fallback tournament level standardization."""
        if pd.isna(level):
            return 'Unknown'
        
        level_str = str(level).upper()
        
        # Basic standardization rules
        if level_str in ['G', 'GRAND SLAM', 'GRAND_SLAM']:
            return 'Grand Slam'
        elif level_str in ['M', 'MASTERS', 'MASTER']:
            return 'Masters'
        elif level_str in ['A', 'ATP', 'ATP250', '250']:
            return 'ATP 250'
        elif level_str in ['D', 'ATP500', '500']:
            return 'ATP 500'
        elif level_str in ['C', 'CHALLENGER']:
            return 'Challenger'
        elif level_str in ['F', 'FUTURES']:
            return 'Futures'
        else:
            return level_str


class LevelProcessor:
    """
    Processes tournament level data by standardizing levels across different tours.
    
    Handles:
    - Standardizing tournament levels for ATP, WTA, and Mixed tours
    - Level consolidation and mapping
    - Level distribution analysis
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the level processor.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        
    def standardize_tourney_levels(self, df: pd.DataFrame, tour_name: str) -> pd.DataFrame:
        """
        Apply tournament level standardization to a dataframe.
        
        Args:
            df: DataFrame with tourney_level column
            tour_name: Tour name for context (ATP, WTA, Mixed, etc.)
            
        Returns:
            DataFrame with standardized tourney_level values
        """
        if df.empty:
            return df
            
        if 'tourney_level' not in df.columns:
            if self.verbose:
                print(f"No tourney_level column found in {tour_name} data, skipping standardization.")
            return df
        
        if self.verbose:
            print(f"\n--- Standardizing Tourney Levels for {tour_name} Data ---")
        
        # Count original levels
        original_levels = df['tourney_level'].value_counts()
        
        if self.verbose:
            print(f"Original tourney levels found: {len(original_levels)}")
            for level, count in original_levels.head(10).items():
                print(f"  {level}: {count:,} matches")
        
        # Apply standardization
        if self.verbose:
            print("Applying standardization...")
        
        df['tourney_level'] = df.apply(
            lambda row: standardize_tourney_level(row['tourney_level'], tour_name), 
            axis=1
        )
        
        # Count standardized levels
        standardized_levels = df['tourney_level'].value_counts()
        
        if self.verbose:
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
    
    def get_level_statistics(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Get tournament level distribution statistics.
        
        Args:
            df: DataFrame with tourney_level column
            
        Returns:
            Dictionary with level distribution
        """
        if df.empty or 'tourney_level' not in df.columns:
            return {}
        
        return df['tourney_level'].value_counts().to_dict()
    
    def get_level_by_tour(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        """
        Get tournament level distribution by tour.
        
        Args:
            df: DataFrame with tourney_level and tour columns
            
        Returns:
            Dictionary with level distribution by tour
        """
        if df.empty or 'tourney_level' not in df.columns or 'tour' not in df.columns:
            return {}
        
        tour_level = df.groupby('tour')['tourney_level'].value_counts()
        result = {}
        
        for tour in df['tour'].unique():
            if pd.notna(tour):
                result[tour] = tour_level[tour].to_dict()
        
        return result
    
    def get_level_by_year(self, df: pd.DataFrame, year: int) -> Dict[str, int]:
        """
        Get tournament level distribution for a specific year.
        
        Args:
            df: DataFrame with tourney_level and event_year columns
            year: Year to filter by
            
        Returns:
            Dictionary with level distribution for the year
        """
        if df.empty or 'tourney_level' not in df.columns or 'event_year' not in df.columns:
            return {}
        
        year_data = df[df['event_year'] == year]
        return year_data['tourney_level'].value_counts().to_dict()
    
    def filter_by_level(self, df: pd.DataFrame, level: str) -> pd.DataFrame:
        """
        Filter matches by tournament level.
        
        Args:
            df: DataFrame with tourney_level column
            level: Tournament level to filter by
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or 'tourney_level' not in df.columns:
            return pd.DataFrame()
        
        return df[df['tourney_level'] == level]
    
    def filter_by_levels(self, df: pd.DataFrame, levels: list) -> pd.DataFrame:
        """
        Filter matches by multiple tournament levels.
        
        Args:
            df: DataFrame with tourney_level column
            levels: List of tournament levels to filter by
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or 'tourney_level' not in df.columns:
            return pd.DataFrame()
        
        return df[df['tourney_level'].isin(levels)]
    
    def validate_level_data(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Validate tournament level data and return statistics.
        
        Args:
            df: DataFrame with tourney_level column
            
        Returns:
            Dictionary with level validation statistics
        """
        if df.empty or 'tourney_level' not in df.columns:
            return {
                'total_matches': 0,
                'valid_levels': 0,
                'missing_levels': 0,
                'level_types': 0
            }
        
        stats = {
            'total_matches': len(df),
            'valid_levels': df['tourney_level'].notna().sum(),
            'missing_levels': df['tourney_level'].isna().sum(),
            'level_types': df['tourney_level'].nunique()
        }
        
        return stats
    
    def get_most_common_level(self, df: pd.DataFrame) -> Optional[str]:
        """
        Get the most common tournament level.
        
        Args:
            df: DataFrame with tourney_level column
            
        Returns:
            Most common tournament level or None
        """
        if df.empty or 'tourney_level' not in df.columns:
            return None
        
        level_counts = df['tourney_level'].value_counts()
        if level_counts.empty:
            return None
        
        return level_counts.index[0]
    
    def get_level_hierarchy(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Get tournament level hierarchy (ordered by frequency).
        
        Args:
            df: DataFrame with tourney_level column
            
        Returns:
            Dictionary with levels ordered by frequency
        """
        if df.empty or 'tourney_level' not in df.columns:
            return {}
        
        return df['tourney_level'].value_counts().to_dict()
    
    def __str__(self):
        """String representation."""
        return f"LevelProcessor(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"LevelProcessor(verbose={self.verbose})"
