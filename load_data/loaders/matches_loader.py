"""
Matches data loader for AskTennis.
Handles loading and processing of ATP and WTA match data.
"""

import pandas as pd
import os
import glob
from typing import List, Optional, Dict
from config.paths import DataPaths
from config.settings import VERBOSE_LOGGING, YEARS, RECENT_YEARS, LOAD_RECENT_ONLY
from core.progress_tracker import ProgressTracker


class MatchesLoader:
    """
    Loads match data from ATP and WTA files.
    
    Handles:
    - Main tour matches by year
    - Amateur era matches (1877-1967)
    - Qualifying matches
    - Challenger/Futures matches
    - ITF matches
    - Fed Cup matches
    - Data cleaning and standardization
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the matches loader.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        
    def load_all_matches(self, years: List[int] = None) -> pd.DataFrame:
        """
        Load all match data from ATP and WTA files.
        
        Args:
            years: List of years to load (defaults to config setting)
            
        Returns:
            Combined DataFrame with all match data
        """
        if years is None:
            years = RECENT_YEARS if LOAD_RECENT_ONLY else YEARS
            
        if self.verbose:
            print("--- Loading Match Data ---")
        
        master_df_list = []
        
        # Load main tour matches
        main_matches = self._load_main_tour_matches(years)
        if not main_matches.empty:
            master_df_list.append(main_matches)
        
        # Load amateur matches
        amateur_matches = self._load_amateur_matches()
        if not amateur_matches.empty:
            master_df_list.append(amateur_matches)
        
        # Load qualifying/challenger/futures matches
        qualifying_matches = self._load_qualifying_matches(years)
        if not qualifying_matches.empty:
            master_df_list.append(qualifying_matches)
        
        # Load Fed Cup matches
        fed_cup_matches = self._load_fed_cup_matches()
        if not fed_cup_matches.empty:
            master_df_list.append(fed_cup_matches)
        
        if not master_df_list:
            if self.verbose:
                print("No match data found!")
            return pd.DataFrame()
        
        # Combine all match data
        matches_df = pd.concat(master_df_list, ignore_index=True)
        
        # Add era classification
        matches_df = self._add_era_classification(matches_df)
        
        # Add tournament type classification
        matches_df = self._add_tournament_type_classification(matches_df)
        
        # Add tour classification
        matches_df = self._add_tour_classification(matches_df)
        
        if self.verbose:
            print(f"Total matches loaded: {len(matches_df)}")
        
        return matches_df
    
    def _load_main_tour_matches(self, years: List[int]) -> pd.DataFrame:
        """Load main tour matches by year."""
        master_df_list = []
        
        # Process ATP and WTA directories
        for data_dir in [self.paths.tennis_atp_dir, self.paths.tennis_wta_dir]:
            if not os.path.exists(data_dir):
                continue
                
            if self.verbose:
                print(f"\n--- Processing directory: {data_dir} ---")
            
            # Determine tour based on directory
            if 'atp' in data_dir.lower():
                tour_name = 'ATP'
            elif 'wta' in data_dir.lower():
                tour_name = 'WTA'
            else:
                tour_name = 'Unknown'
            
            df_list = []
            for year in years:
                file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
                matching_files = glob.glob(file_pattern)
                
                if matching_files:
                    file_path = matching_files[0]
                    if self.verbose:
                        print(f"  Loading {os.path.basename(file_path)}...")
                    
                    try:
                        df = pd.read_csv(file_path, low_memory=False, index_col=False)
                        df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d')
                        df['tour'] = tour_name
                        df_list.append(df)
                    except Exception as e:
                        if self.verbose:
                            print(f"  Error loading {file_path}: {e}")
            
            if df_list:
                tour_df = pd.concat(df_list, ignore_index=True)
                master_df_list.append(tour_df)
        
        if master_df_list:
            return pd.concat(master_df_list, ignore_index=True)
        return pd.DataFrame()
    
    def _load_amateur_matches(self) -> pd.DataFrame:
        """Load amateur era matches (1877-1967)."""
        amateur_files = self.paths.get_amateur_files()
        
        if not amateur_files:
            if self.verbose:
                print("No amateur tennis files found")
            return pd.DataFrame()
        
        if self.verbose:
            print(f"\n--- Loading Amateur Tennis Data (1877-1967) ---")
        
        amateur_dfs = []
        for file_path in amateur_files:
            if self.verbose:
                print(f"Reading {os.path.basename(file_path)}...")
            
            try:
                df = pd.read_csv(file_path, low_memory=False, index_col=False)
                df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d')
                df['tour'] = 'ATP'  # Amateur data is from ATP source
                amateur_dfs.append(df)
            except Exception as e:
                if self.verbose:
                    print(f"Error loading {file_path}: {e}")
        
        if amateur_dfs:
            amateur_df = pd.concat(amateur_dfs, ignore_index=True)
            if self.verbose:
                print(f"Amateur matches loaded: {len(amateur_df)}")
            return amateur_df
        
        return pd.DataFrame()
    
    def _load_qualifying_matches(self, years: List[int]) -> pd.DataFrame:
        """Load qualifying/challenger/futures matches."""
        if self.verbose:
            print(f"\n--- Loading Qualifying/Challenger/Futures Data ---")
        
        qualifying_dfs = []
        
        # ATP Qualifying data
        atp_qual_files = glob.glob(os.path.join(self.paths.tennis_atp_dir, "atp_matches_qual_*.csv"))
        if atp_qual_files:
            atp_qual_files = self._filter_files_by_years(atp_qual_files, years)
            if self.verbose:
                print(f"Loading ATP Qualifying data ({len(atp_qual_files)} files)...")
            
            for file_path in atp_qual_files:
                try:
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'ATP_Qualifying'
                    df['tour'] = 'ATP'
                    qualifying_dfs.append(df)
                except Exception as e:
                    if self.verbose:
                        print(f"Error loading {file_path}: {e}")
        
        # WTA Qualifying data
        wta_qual_files = glob.glob(os.path.join(self.paths.tennis_wta_dir, "wta_matches_qual_*.csv"))
        if wta_qual_files:
            wta_qual_files = self._filter_files_by_years(wta_qual_files, years)
            if self.verbose:
                print(f"Loading WTA Qualifying data ({len(wta_qual_files)} files)...")
            
            for file_path in wta_qual_files:
                try:
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'WTA_Qualifying'
                    df['tour'] = 'WTA'
                    qualifying_dfs.append(df)
                except Exception as e:
                    if self.verbose:
                        print(f"Error loading {file_path}: {e}")
        
        # ATP Challenger data
        atp_challenger_files = glob.glob(os.path.join(self.paths.tennis_atp_dir, "atp_matches_challenger_*.csv"))
        if atp_challenger_files:
            atp_challenger_files = self._filter_files_by_years(atp_challenger_files, years)
            if self.verbose:
                print(f"Loading ATP Challenger data ({len(atp_challenger_files)} files)...")
            
            for file_path in atp_challenger_files:
                try:
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'ATP_Challenger'
                    df['tour'] = 'ATP'
                    qualifying_dfs.append(df)
                except Exception as e:
                    if self.verbose:
                        print(f"Error loading {file_path}: {e}")
        
        # WTA Challenger data
        wta_challenger_files = glob.glob(os.path.join(self.paths.tennis_wta_dir, "wta_matches_challenger_*.csv"))
        if wta_challenger_files:
            wta_challenger_files = self._filter_files_by_years(wta_challenger_files, years)
            if self.verbose:
                print(f"Loading WTA Challenger data ({len(wta_challenger_files)} files)...")
            
            for file_path in wta_challenger_files:
                try:
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'WTA_Challenger'
                    df['tour'] = 'WTA'
                    qualifying_dfs.append(df)
                except Exception as e:
                    if self.verbose:
                        print(f"Error loading {file_path}: {e}")
        
        # ATP Futures data
        atp_futures_files = glob.glob(os.path.join(self.paths.tennis_atp_dir, "atp_matches_futures_*.csv"))
        if atp_futures_files:
            atp_futures_files = self._filter_files_by_years(atp_futures_files, years)
            if self.verbose:
                print(f"Loading ATP Futures data ({len(atp_futures_files)} files)...")
            
            for file_path in atp_futures_files:
                try:
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'ATP_Futures'
                    df['tour'] = 'ATP'
                    qualifying_dfs.append(df)
                except Exception as e:
                    if self.verbose:
                        print(f"Error loading {file_path}: {e}")
        
        # WTA ITF data
        wta_itf_files = glob.glob(os.path.join(self.paths.tennis_wta_dir, "wta_matches_itf_*.csv"))
        if wta_itf_files:
            wta_itf_files = self._filter_files_by_years(wta_itf_files, years)
            if self.verbose:
                print(f"Loading WTA ITF data ({len(wta_itf_files)} files)...")
            
            for file_path in wta_itf_files:
                try:
                    df = pd.read_csv(file_path, low_memory=False, index_col=False)
                    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                    df['tournament_type'] = 'WTA_ITF'
                    df['tour'] = 'WTA'
                    qualifying_dfs.append(df)
                except Exception as e:
                    if self.verbose:
                        print(f"Error loading {file_path}: {e}")
        
        if qualifying_dfs:
            qualifying_df = pd.concat(qualifying_dfs, ignore_index=True)
            if self.verbose:
                print(f"Qualifying/Challenger/Futures matches loaded: {len(qualifying_df)}")
            return qualifying_df
        
        return pd.DataFrame()
    
    def _load_fed_cup_matches(self) -> pd.DataFrame:
        """Load Fed Cup (BJK Cup) matches."""
        fed_cup_files = self.paths.get_fed_cup_files()
        
        if not fed_cup_files:
            if self.verbose:
                print("No Fed Cup files found")
            return pd.DataFrame()
        
        if self.verbose:
            print(f"Loading Fed Cup (BJK Cup) data ({len(fed_cup_files)} files)...")
        
        fed_cup_dfs = []
        for file_path in fed_cup_files:
            try:
                df = pd.read_csv(file_path, low_memory=False, index_col=False)
                df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
                df['tournament_type'] = 'Fed_Cup'
                df['tour'] = 'WTA'  # Fed Cup is women's competition
                fed_cup_dfs.append(df)
            except Exception as e:
                if self.verbose:
                    print(f"Error loading {file_path}: {e}")
        
        if fed_cup_dfs:
            fed_cup_df = pd.concat(fed_cup_dfs, ignore_index=True)
            if self.verbose:
                print(f"Fed Cup (BJK Cup) matches loaded: {len(fed_cup_df)}")
            return fed_cup_df
        
        return pd.DataFrame()
    
    def _filter_files_by_years(self, files: List[str], years: List[int]) -> List[str]:
        """Filter files by years."""
        if LOAD_RECENT_ONLY:
            filtered_files = []
            for file_path in files:
                try:
                    year = int(file_path.split('_')[-1].split('.')[0])
                    if year in years:
                        filtered_files.append(file_path)
                except (ValueError, IndexError):
                    continue
            return filtered_files
        return files
    
    def _add_era_classification(self, matches_df: pd.DataFrame) -> pd.DataFrame:
        """Add era classification to matches."""
        if matches_df.empty:
            return matches_df
        
        def classify_era(row):
            if pd.isna(row.get('tourney_date')):
                return 'Unknown'
            year = row['tourney_date'].year
            if year >= 1968:
                return 'Open Era'
            else:
                return 'Closed Era'
        
        matches_df['era'] = matches_df.apply(classify_era, axis=1)
        return matches_df
    
    def _add_tournament_type_classification(self, matches_df: pd.DataFrame) -> pd.DataFrame:
        """Add tournament type classification."""
        if matches_df.empty:
            return matches_df
        
        matches_df['tournament_type'] = matches_df['tournament_type'].fillna('Main Tour')
        return matches_df
    
    def _add_tour_classification(self, matches_df: pd.DataFrame) -> pd.DataFrame:
        """Add tour classification."""
        if matches_df.empty:
            return matches_df
        
        matches_df['tour'] = matches_df['tour'].fillna('Unknown')
        return matches_df
    
    def get_matches_stats(self, matches_df: pd.DataFrame) -> dict:
        """Get statistics about loaded matches."""
        if matches_df.empty:
            return {
                'total_matches': 0,
                'atp_matches': 0,
                'wta_matches': 0,
                'by_era': {},
                'by_tournament_type': {}
            }
        
        stats = {
            'total_matches': len(matches_df),
            'atp_matches': len(matches_df[matches_df['tour'] == 'ATP']),
            'wta_matches': len(matches_df[matches_df['tour'] == 'WTA']),
            'by_era': matches_df['era'].value_counts().to_dict(),
            'by_tournament_type': matches_df['tournament_type'].value_counts().to_dict()
        }
        
        return stats
    
    def __str__(self):
        """String representation."""
        return f"MatchesLoader(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"MatchesLoader(verbose={self.verbose}, paths={self.paths})"
