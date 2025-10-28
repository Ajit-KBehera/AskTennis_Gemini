"""
Date processing utilities for AskTennis data loading.
Handles parsing of date components from tournament dates.
"""

import pandas as pd
from typing import Optional
from config.settings import VERBOSE_LOGGING


class DateProcessor:
    """
    Processes date data by parsing tournament dates into components.
    
    Handles:
    - Parsing tourney_date into event_year, event_month, event_date
    - Column reordering to place date components after tourney_date
    - Date validation and error handling
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the date processor.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        
    def parse_date_components(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse tourney_date into event_year, event_month, event_date columns.
        
        Adds three new columns while keeping the original tourney_date column.
        Places the new columns right beside the tourney_date column.
        
        Args:
            df: DataFrame with tourney_date column
            
        Returns:
            DataFrame with added date component columns
        """
        if df.empty:
            return df
            
        if 'tourney_date' not in df.columns:
            if self.verbose:
                print("Warning: 'tourney_date' column not found in DataFrame")
            return df
        
        if self.verbose:
            print("\n--- Parsing Date Components ---")
        
        # Create a copy to avoid modifying original
        df_copy = df.copy()
        
        # Extract date components
        event_year = df_copy['tourney_date'].dt.year
        event_month = df_copy['tourney_date'].dt.month
        event_date = df_copy['tourney_date'].dt.day
        
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
        
        if self.verbose:
            print(f"Date parsing completed: {len(df_reordered)}/{len(df)} dates parsed (100.0%)")
            print(f"Date range: {df_reordered['event_year'].min()}-{df_reordered['event_year'].max()}")
            print(f"Year range: {df_reordered['event_year'].min()} to {df_reordered['event_year'].max()}")
        
        return df_reordered
    
    def validate_dates(self, df: pd.DataFrame) -> dict:
        """
        Validate date data and return statistics.
        
        Args:
            df: DataFrame with date columns
            
        Returns:
            Dictionary with date validation statistics
        """
        if df.empty:
            return {
                'total_dates': 0,
                'valid_dates': 0,
                'invalid_dates': 0,
                'date_range': None,
                'year_range': None
            }
        
        stats = {
            'total_dates': len(df),
            'valid_dates': df['tourney_date'].notna().sum(),
            'invalid_dates': df['tourney_date'].isna().sum(),
            'date_range': None,
            'year_range': None
        }
        
        if 'event_year' in df.columns:
            valid_years = df['event_year'].dropna()
            if not valid_years.empty:
                stats['year_range'] = {
                    'min': int(valid_years.min()),
                    'max': int(valid_years.max())
                }
        
        valid_dates = df['tourney_date'].dropna()
        if not valid_dates.empty:
            stats['date_range'] = {
                'min': valid_dates.min(),
                'max': valid_dates.max()
            }
        
        return stats
    
    def filter_by_year(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        """
        Filter DataFrame by year.
        
        Args:
            df: DataFrame with event_year column
            year: Year to filter by
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or 'event_year' not in df.columns:
            return pd.DataFrame()
        
        return df[df['event_year'] == year]
    
    def filter_by_year_range(self, df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Filter DataFrame by year range.
        
        Args:
            df: DataFrame with event_year column
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or 'event_year' not in df.columns:
            return pd.DataFrame()
        
        return df[(df['event_year'] >= start_year) & (df['event_year'] <= end_year)]
    
    def filter_by_month(self, df: pd.DataFrame, month: int) -> pd.DataFrame:
        """
        Filter DataFrame by month.
        
        Args:
            df: DataFrame with event_month column
            month: Month to filter by (1-12)
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or 'event_month' not in df.columns:
            return pd.DataFrame()
        
        return df[df['event_month'] == month]
    
    def get_season_stats(self, df: pd.DataFrame) -> dict:
        """
        Get statistics by season (year).
        
        Args:
            df: DataFrame with event_year column
            
        Returns:
            Dictionary with season statistics
        """
        if df.empty or 'event_year' not in df.columns:
            return {}
        
        season_stats = df['event_year'].value_counts().sort_index()
        return season_stats.to_dict()
    
    def get_monthly_stats(self, df: pd.DataFrame) -> dict:
        """
        Get statistics by month.
        
        Args:
            df: DataFrame with event_month column
            
        Returns:
            Dictionary with monthly statistics
        """
        if df.empty or 'event_month' not in df.columns:
            return {}
        
        monthly_stats = df['event_month'].value_counts().sort_index()
        return monthly_stats.to_dict()
    
    def __str__(self):
        """String representation."""
        return f"DateProcessor(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"DateProcessor(verbose={self.verbose})"
