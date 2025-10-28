"""
Surface data processing utilities for AskTennis data loading.
Handles fixing missing surface data by inferring from tournament names and historical data.
"""

import pandas as pd
from typing import Dict, Optional
from config.settings import VERBOSE_LOGGING


class SurfaceProcessor:
    """
    Processes surface data by fixing missing surface information.
    
    Handles:
    - Inferring surface from tournament names
    - Historical surface inference based on era
    - Grand Slam surface mapping
    - Surface distribution analysis
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the surface processor.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        
        # Surface inference rules
        self.grass_keywords = ['grass', 'lawn', 'wimbledon']
        self.clay_keywords = ['clay', 'dirt', 'red', 'french', 'roland', 'paris']
        self.hard_keywords = ['hard', 'concrete', 'asphalt', 'us open', 'australian', 'melbourne']
        self.carpet_keywords = ['carpet', 'indoor']
        
    def fix_missing_surface_data(self, matches_df: pd.DataFrame) -> pd.DataFrame:
        """
        Fixes missing surface data by inferring surface from tournament names and historical data.
        
        Args:
            matches_df: DataFrame with surface and tourney_name columns
            
        Returns:
            DataFrame with fixed surface data
        """
        if matches_df.empty:
            return matches_df
            
        if 'surface' not in matches_df.columns:
            if self.verbose:
                print("Warning: 'surface' column not found in DataFrame")
            return matches_df
        
        if self.verbose:
            print("\n--- Fixing Missing Surface Data ---")
        
        # Count missing surface data
        missing_before = len(matches_df[matches_df['surface'].isna() | (matches_df['surface'] == '')])
        
        if self.verbose:
            print(f"Missing surface data before fix: {missing_before:,} matches")
        
        if missing_before == 0:
            if self.verbose:
                print("No missing surface data found!")
            return matches_df
        
        # Create a copy to avoid modifying original
        df = matches_df.copy()
        
        # Apply surface inference to missing data
        missing_mask = df['surface'].isna() | (df['surface'] == '')
        df.loc[missing_mask, 'surface'] = df[missing_mask].apply(self._infer_surface, axis=1)
        
        # Count remaining missing surface data
        missing_after = len(df[df['surface'].isna() | (df['surface'] == '')])
        fixed_count = missing_before - missing_after
        
        if self.verbose:
            print(f"Fixed surface data: {fixed_count:,} matches")
            print(f"Remaining missing surface data: {missing_after:,} matches")
            
            if missing_after > 0:
                print("Surface distribution after fix:")
                surface_dist = df['surface'].value_counts()
                for surface, count in surface_dist.items():
                    print(f"  {surface}: {count:,} matches")
        
        return df
    
    def _infer_surface(self, row) -> str:
        """
        Infer surface from tournament name and historical data.
        
        Args:
            row: DataFrame row with tourney_name and tourney_date
            
        Returns:
            Inferred surface type
        """
        tourney_name = str(row['tourney_name']).lower()
        tourney_date = row.get('tourney_date')
        
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
                if any(name in tourney_name for name in self.grass_keywords):
                    return 'Grass'
                elif any(name in tourney_name for name in self.clay_keywords):
                    return 'Clay'
                else:
                    return 'Grass'  # Default for pre-1970s
            
            # 1970s-1980s: Introduction of hard courts
            elif year < 1990:
                if any(name in tourney_name for name in self.hard_keywords):
                    return 'Hard'
                elif any(name in tourney_name for name in self.grass_keywords):
                    return 'Grass'
                elif any(name in tourney_name for name in self.clay_keywords):
                    return 'Clay'
                else:
                    return 'Hard'  # Default for 1970s-1980s
            
            # 1990s+: Mostly hard courts
            else:
                if any(name in tourney_name for name in self.grass_keywords):
                    return 'Grass'
                elif any(name in tourney_name for name in self.clay_keywords):
                    return 'Clay'
                elif any(name in tourney_name for name in self.carpet_keywords):
                    return 'Carpet'
                else:
                    return 'Hard'  # Default for modern era
        
        return 'Hard'  # Final default
    
    def get_surface_statistics(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Get surface distribution statistics.
        
        Args:
            df: DataFrame with surface column
            
        Returns:
            Dictionary with surface distribution
        """
        if df.empty or 'surface' not in df.columns:
            return {}
        
        return df['surface'].value_counts().to_dict()
    
    def get_surface_by_era(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        """
        Get surface distribution by era.
        
        Args:
            df: DataFrame with surface and era columns
            
        Returns:
            Dictionary with surface distribution by era
        """
        if df.empty or 'surface' not in df.columns or 'era' not in df.columns:
            return {}
        
        era_surface = df.groupby('era')['surface'].value_counts()
        result = {}
        
        for era in df['era'].unique():
            if pd.notna(era):
                result[era] = era_surface[era].to_dict()
        
        return result
    
    def get_surface_by_year(self, df: pd.DataFrame, year: int) -> Dict[str, int]:
        """
        Get surface distribution for a specific year.
        
        Args:
            df: DataFrame with surface and event_year columns
            year: Year to filter by
            
        Returns:
            Dictionary with surface distribution for the year
        """
        if df.empty or 'surface' not in df.columns or 'event_year' not in df.columns:
            return {}
        
        year_data = df[df['event_year'] == year]
        return year_data['surface'].value_counts().to_dict()
    
    def filter_by_surface(self, df: pd.DataFrame, surface: str) -> pd.DataFrame:
        """
        Filter matches by surface type.
        
        Args:
            df: DataFrame with surface column
            surface: Surface type to filter by
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or 'surface' not in df.columns:
            return pd.DataFrame()
        
        return df[df['surface'] == surface]
    
    def validate_surface_data(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Validate surface data and return statistics.
        
        Args:
            df: DataFrame with surface column
            
        Returns:
            Dictionary with surface validation statistics
        """
        if df.empty or 'surface' not in df.columns:
            return {
                'total_matches': 0,
                'valid_surface': 0,
                'missing_surface': 0,
                'surface_types': 0
            }
        
        stats = {
            'total_matches': len(df),
            'valid_surface': df['surface'].notna().sum(),
            'missing_surface': df['surface'].isna().sum(),
            'surface_types': df['surface'].nunique()
        }
        
        return stats
    
    def get_most_common_surface(self, df: pd.DataFrame) -> Optional[str]:
        """
        Get the most common surface type.
        
        Args:
            df: DataFrame with surface column
            
        Returns:
            Most common surface type or None
        """
        if df.empty or 'surface' not in df.columns:
            return None
        
        surface_counts = df['surface'].value_counts()
        if surface_counts.empty:
            return None
        
        return surface_counts.index[0]
    
    def __str__(self):
        """String representation."""
        return f"SurfaceProcessor(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"SurfaceProcessor(verbose={self.verbose})"
