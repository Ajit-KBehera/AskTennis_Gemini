"""
Score processing utilities for AskTennis data loading.
Handles parsing of tennis match scores into individual sets.
"""

import pandas as pd
from typing import List, Optional
from config.settings import VERBOSE_LOGGING


class ScoreProcessor:
    """
    Processes score data by parsing tennis match scores into individual sets.
    
    Handles:
    - Parsing score column into set1, set2, set3, set4, set5 columns
    - Special cases: W/O (Walkover), DEF (Default), RET (Retirement)
    - Column reordering to place set columns after score
    - Score validation and error handling
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the score processor.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        
    def parse_score_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse score column into set1, set2, set3, set4, set5 columns.
        
        Adds five new columns while keeping the original score column.
        Places the new columns right beside the score column.
        Handles RET by putting 'RET' in subsequent set columns.
        
        Args:
            df: DataFrame with score column
            
        Returns:
            DataFrame with added set score columns
        """
        if df.empty:
            return df
            
        if 'score' not in df.columns:
            if self.verbose:
                print("Warning: 'score' column not found in DataFrame")
            return df
        
        if self.verbose:
            print("\n--- Parsing Score Data ---")
        
        # Create a copy to avoid modifying original
        df_copy = df.copy()
        
        # Apply parsing to all scores
        parsed_scores = df_copy['score'].apply(self._parse_score)
        
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
        
        if self.verbose:
            print(f"Score parsing completed: {len(df_reordered)}/{len(df)} matches parsed (100.0%)")
            print("Sample parsed scores:")
            sample_scores = df_reordered[['set1', 'set2', 'set3', 'set4', 'set5']].dropna(how='all').head(3)
            for idx, row in sample_scores.iterrows():
                original = df.loc[idx, 'score'] if idx < len(df) else 'N/A'
                parsed = ' | '.join([str(s) for s in row.values if pd.notna(s)])
                print(f"  Original: {original} -> Parsed: {parsed}")
        
        return df_reordered
    
    def _parse_score(self, score_str) -> List[Optional[str]]:
        """
        Parse a single score string into set scores.
        
        Args:
            score_str: Score string to parse
            
        Returns:
            List of 5 set scores (None for empty sets)
        """
        if pd.isna(score_str) or score_str == '':
            return [None, None, None, None, None]
        
        score_str = str(score_str).strip()
        
        # Handle special cases
        if score_str in ['W/O', 'WO', 'Walkover']:
            return ['W/O', None, None, None, None]
        elif score_str in ['DEF', 'Default']:
            return ['DEF', None, None, None, None]
        elif 'W/O' in score_str.upper() or 'WO' in score_str.upper():
            return self._parse_walkover_score(score_str)
        elif 'DEF' in score_str.upper() or 'DEFAULT' in score_str.upper():
            return self._parse_default_score(score_str)
        elif 'RET' in score_str.upper():
            return self._parse_retirement_score(score_str)
        else:
            # Normal score parsing
            parts = score_str.split()
            sets = parts[:5]  # Take first 5 parts
            while len(sets) < 5:
                sets.append(None)
            return sets
    
    def _parse_walkover_score(self, score_str: str) -> List[Optional[str]]:
        """Parse walkover score."""
        parts = score_str.split()
        sets = []
        
        for part in parts:
            if 'W/O' in part.upper() or 'WO' in part.upper():
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
    
    def _parse_default_score(self, score_str: str) -> List[Optional[str]]:
        """Parse default score."""
        parts = score_str.split()
        sets = []
        
        for part in parts:
            if 'DEF' in part.upper() or 'DEFAULT' in part.upper():
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
    
    def _parse_retirement_score(self, score_str: str) -> List[Optional[str]]:
        """Parse retirement score."""
        parts = score_str.split()
        sets = []
        
        for part in parts:
            if 'RET' in part.upper():
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
    
    def validate_scores(self, df: pd.DataFrame) -> dict:
        """
        Validate score data and return statistics.
        
        Args:
            df: DataFrame with score columns
            
        Returns:
            Dictionary with score validation statistics
        """
        if df.empty:
            return {
                'total_scores': 0,
                'valid_scores': 0,
                'invalid_scores': 0,
                'walkovers': 0,
                'defaults': 0,
                'retirements': 0
            }
        
        stats = {
            'total_scores': len(df),
            'valid_scores': df['score'].notna().sum(),
            'invalid_scores': df['score'].isna().sum(),
            'walkovers': 0,
            'defaults': 0,
            'retirements': 0
        }
        
        if 'score' in df.columns:
            scores = df['score'].dropna().astype(str)
            stats['walkovers'] = scores.str.contains('W/O|WO', case=False, na=False).sum()
            stats['defaults'] = scores.str.contains('DEF|DEFAULT', case=False, na=False).sum()
            stats['retirements'] = scores.str.contains('RET', case=False, na=False).sum()
        
        return stats
    
    def get_set_statistics(self, df: pd.DataFrame) -> dict:
        """
        Get statistics about sets played.
        
        Args:
            df: DataFrame with set columns
            
        Returns:
            Dictionary with set statistics
        """
        if df.empty:
            return {
                'matches_with_sets': 0,
                'average_sets_per_match': 0,
                'max_sets_played': 0,
                'set_distribution': {}
            }
        
        set_columns = ['set1', 'set2', 'set3', 'set4', 'set5']
        available_set_columns = [col for col in set_columns if col in df.columns]
        
        if not available_set_columns:
            return {'matches_with_sets': 0, 'average_sets_per_match': 0, 'max_sets_played': 0, 'set_distribution': {}}
        
        # Count sets played per match
        sets_played = df[available_set_columns].notna().sum(axis=1)
        
        stats = {
            'matches_with_sets': (sets_played > 0).sum(),
            'average_sets_per_match': sets_played.mean(),
            'max_sets_played': sets_played.max(),
            'set_distribution': sets_played.value_counts().sort_index().to_dict()
        }
        
        return stats
    
    def filter_by_match_length(self, df: pd.DataFrame, min_sets: int = None, max_sets: int = None) -> pd.DataFrame:
        """
        Filter matches by number of sets played.
        
        Args:
            df: DataFrame with set columns
            min_sets: Minimum number of sets
            max_sets: Maximum number of sets
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return pd.DataFrame()
        
        set_columns = ['set1', 'set2', 'set3', 'set4', 'set5']
        available_set_columns = [col for col in set_columns if col in df.columns]
        
        if not available_set_columns:
            return pd.DataFrame()
        
        # Count sets played per match
        sets_played = df[available_set_columns].notna().sum(axis=1)
        
        mask = pd.Series([True] * len(df), index=df.index)
        
        if min_sets is not None:
            mask &= (sets_played >= min_sets)
        
        if max_sets is not None:
            mask &= (sets_played <= max_sets)
        
        return df[mask]
    
    def __str__(self):
        """String representation."""
        return f"ScoreProcessor(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"ScoreProcessor(verbose={self.verbose})"
