"""
Players data loader for AskTennis.
Handles loading and processing of ATP and WTA player data.
"""

import pandas as pd
import os
from typing import Optional, Tuple
from config.paths import DataPaths
from config.settings import VERBOSE_LOGGING


class PlayersLoader:
    """
    Loads player information from ATP and WTA player files.
    
    Handles:
    - ATP player data loading
    - WTA player data loading
    - Data cleaning and standardization
    - Player name processing
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the players loader.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        
    def load_all_players(self) -> pd.DataFrame:
        """
        Load all player data from ATP and WTA files.
        
        Returns:
            Combined DataFrame with all player data
        """
        if self.verbose:
            print("--- Loading Player Information ---")
        
        # Load ATP and WTA players
        atp_players = self._load_atp_players()
        wta_players = self._load_wta_players()
        
        # Combine players
        all_players = self._combine_players(atp_players, wta_players)
        
        if all_players.empty:
            if self.verbose:
                print("No player data found!")
            return pd.DataFrame()
        
        # Clean and standardize data
        all_players = self._clean_player_data(all_players)
        
        if self.verbose:
            print(f"Total players loaded: {len(all_players)}")
        
        return all_players
    
    def _load_atp_players(self) -> pd.DataFrame:
        """Load ATP players data."""
        atp_file = self.paths.atp_players_file
        
        if not self.paths.file_exists(atp_file):
            if self.verbose:
                print(f"Warning: {atp_file} not found")
            return pd.DataFrame()
        
        if self.verbose:
            print(f"Reading {atp_file}...")
        
        try:
            atp_players = pd.read_csv(atp_file, index_col=False)
            atp_players['tour'] = 'ATP'
            
            if self.verbose:
                print(f"ATP players loaded: {len(atp_players)}")
            
            return atp_players
            
        except Exception as e:
            if self.verbose:
                print(f"Error loading ATP players: {e}")
            return pd.DataFrame()
    
    def _load_wta_players(self) -> pd.DataFrame:
        """Load WTA players data."""
        wta_file = self.paths.wta_players_file
        
        if not self.paths.file_exists(wta_file):
            if self.verbose:
                print(f"Warning: {wta_file} not found")
            return pd.DataFrame()
        
        if self.verbose:
            print(f"Reading {wta_file}...")
        
        try:
            wta_players = pd.read_csv(wta_file, index_col=False)
            wta_players['tour'] = 'WTA'
            
            if self.verbose:
                print(f"WTA players loaded: {len(wta_players)}")
            
            return wta_players
            
        except Exception as e:
            if self.verbose:
                print(f"Error loading WTA players: {e}")
            return pd.DataFrame()
    
    def _combine_players(self, atp_players: pd.DataFrame, wta_players: pd.DataFrame) -> pd.DataFrame:
        """Combine ATP and WTA player data."""
        if not atp_players.empty and not wta_players.empty:
            return pd.concat([atp_players, wta_players], ignore_index=True)
        elif not atp_players.empty:
            return atp_players
        elif not wta_players.empty:
            return wta_players
        else:
            return pd.DataFrame()
    
    def _clean_player_data(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize player data.
        
        Args:
            players_df: Raw player data
            
        Returns:
            Cleaned player data
        """
        if players_df.empty:
            return players_df
        
        # Clean date of birth
        players_df['dob'] = pd.to_datetime(players_df['dob'], format='%Y%m%d', errors='coerce')
        
        # Clean height data
        players_df['height'] = pd.to_numeric(players_df['height'], errors='coerce')
        
        # Create full name for easier searching
        players_df['full_name'] = players_df['name_first'] + ' ' + players_df['name_last']
        
        # Clean any NaN values in full_name
        players_df['full_name'] = players_df['full_name'].fillna('Unknown Player')
        
        return players_df
    
    def get_player_stats(self, players_df: pd.DataFrame) -> dict:
        """
        Get statistics about loaded players.
        
        Args:
            players_df: Player data
            
        Returns:
            Dictionary with player statistics
        """
        if players_df.empty:
            return {
                'total_players': 0,
                'atp_players': 0,
                'wta_players': 0,
                'players_with_height': 0,
                'players_with_dob': 0
            }
        
        stats = {
            'total_players': len(players_df),
            'atp_players': len(players_df[players_df['tour'] == 'ATP']),
            'wta_players': len(players_df[players_df['tour'] == 'WTA']),
            'players_with_height': players_df['height'].notna().sum(),
            'players_with_dob': players_df['dob'].notna().sum()
        }
        
        return stats
    
    def search_players(self, players_df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """
        Search for players by name.
        
        Args:
            players_df: Player data
            search_term: Search term
            
        Returns:
            Filtered player data
        """
        if players_df.empty or not search_term:
            return pd.DataFrame()
        
        search_term = search_term.lower()
        
        # Search in first name, last name, and full name
        mask = (
            players_df['name_first'].str.lower().str.contains(search_term, na=False) |
            players_df['name_last'].str.lower().str.contains(search_term, na=False) |
            players_df['full_name'].str.lower().str.contains(search_term, na=False)
        )
        
        return players_df[mask]
    
    def __str__(self):
        """String representation."""
        return f"PlayersLoader(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"PlayersLoader(verbose={self.verbose}, paths={self.paths})"
