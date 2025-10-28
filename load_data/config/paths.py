"""
File paths and directory management for AskTennis data loading.
Centralizes all file path operations and directory management.
"""

import os
from .settings import PROJECT_ROOT

class DataPaths:
    """Manages all data file paths and directories."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_root = os.path.join(self.project_root, "data")
        self.logs_root = os.path.join(self.project_root, "logs")
        
    # --- Data Directory Paths ---
    @property
    def tennis_atp_dir(self):
        return os.path.join(self.data_root, "tennis_atp")
    
    @property
    def tennis_wta_dir(self):
        return os.path.join(self.data_root, "tennis_wta")
    
    @property
    def tennis_slam_dir(self):
        return os.path.join(self.data_root, "tennis_slam_pointbypoint")
    
    @property
    def tennis_charting_dir(self):
        return os.path.join(self.data_root, "tennis_MatchChartingProject")
    
    # --- Player File Paths ---
    @property
    def atp_players_file(self):
        return os.path.join(self.tennis_atp_dir, "atp_players.csv")
    
    @property
    def wta_players_file(self):
        return os.path.join(self.tennis_wta_dir, "wta_players.csv")
    
    # --- Ranking File Paths ---
    def get_atp_rankings_file(self, year):
        return os.path.join(self.tennis_atp_dir, f"atp_rankings_{year}.csv")
    
    def get_wta_rankings_file(self, year):
        return os.path.join(self.tennis_wta_dir, f"wta_rankings_{year}.csv")
    
    # --- Match File Paths ---
    def get_atp_matches_file(self, year):
        return os.path.join(self.tennis_atp_dir, f"atp_matches_{year}.csv")
    
    def get_wta_matches_file(self, year):
        return os.path.join(self.tennis_wta_dir, f"wta_matches_{year}.csv")
    
    def get_atp_matches_qualifying_file(self, year):
        return os.path.join(self.tennis_atp_dir, f"atp_matches_qualifying_{year}.csv")
    
    def get_wta_matches_qualifying_file(self, year):
        return os.path.join(self.tennis_wta_dir, f"wta_matches_qualifying_{year}.csv")
    
    def get_atp_matches_challenger_file(self, year):
        return os.path.join(self.tennis_atp_dir, f"atp_matches_challenger_{year}.csv")
    
    def get_wta_matches_challenger_file(self, year):
        return os.path.join(self.tennis_wta_dir, f"wta_matches_challenger_{year}.csv")
    
    def get_atp_matches_futures_file(self, year):
        return os.path.join(self.tennis_atp_dir, f"atp_matches_futures_{year}.csv")
    
    def get_wta_matches_itf_file(self, year):
        return os.path.join(self.tennis_wta_dir, f"wta_matches_itf_{year}.csv")
    
    # --- Doubles File Paths ---
    def get_atp_doubles_file(self, year):
        return os.path.join(self.tennis_atp_dir, f"atp_matches_doubles_{year}.csv")
    
    def get_wta_doubles_file(self, year):
        return os.path.join(self.tennis_wta_dir, f"wta_matches_doubles_{year}.csv")
    
    # --- Special Tournament File Paths ---
    def get_fed_cup_files(self):
        """Get all Fed Cup (BJK Cup) files."""
        import glob
        return glob.glob(os.path.join(self.tennis_wta_dir, "wta_matches_fed_cup_*.csv"))
    
    def get_amateur_files(self):
        """Get all amateur era files."""
        import glob
        amateur_files = []
        amateur_files.extend(glob.glob(os.path.join(self.tennis_atp_dir, "atp_matches_amateur_*.csv")))
        amateur_files.extend(glob.glob(os.path.join(self.tennis_wta_dir, "wta_matches_amateur_*.csv")))
        return amateur_files
    
    # --- Database File Paths ---
    @property
    def main_database_file(self):
        return os.path.join(self.project_root, "tennis_data.db")
    
    @property
    def main_tour_database_file(self):
        return os.path.join(self.project_root, "tennis_data_main_tour_singles_open_era.db")
    
    # --- Log File Paths ---
    @property
    def data_loading_log_file(self):
        return os.path.join(self.logs_root, "data_loading.log")
    
    @property
    def error_log_file(self):
        return os.path.join(self.logs_root, "data_loading_errors.log")
    
    # --- Utility Methods ---
    def ensure_directory_exists(self, directory_path):
        """Ensure a directory exists, create if it doesn't."""
        os.makedirs(directory_path, exist_ok=True)
    
    def file_exists(self, file_path):
        """Check if a file exists."""
        return os.path.exists(file_path)
    
    def get_file_size(self, file_path):
        """Get file size in bytes."""
        if self.file_exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    def list_files_in_directory(self, directory_path, pattern="*.csv"):
        """List all files matching pattern in directory."""
        import glob
        if os.path.exists(directory_path):
            return glob.glob(os.path.join(directory_path, pattern))
        return []
