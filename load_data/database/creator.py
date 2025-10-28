"""
Database creation utilities for AskTennis data loading.
Handles creation and population of SQLite database with tennis data.
"""

import sqlite3
import pandas as pd
from typing import Optional, Dict, Any, List
from config.settings import VERBOSE_LOGGING, CREATE_INDEXES, INDEX_BATCH_SIZE
from config.paths import DataPaths
from core.progress_tracker import ProgressTracker


class DatabaseCreator:
    """
    Creates and populates SQLite database with tennis data.
    
    Handles:
    - Database creation and table population
    - Index creation for performance
    - View creation for easy querying
    - Data validation and integrity checks
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the database creator.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        
    def create_database_with_players(self, 
                                   players_df: pd.DataFrame,
                                   rankings_df: pd.DataFrame,
                                   matches_df: pd.DataFrame,
                                   doubles_df: pd.DataFrame,
                                   database_file: str = None) -> bool:
        """
        Creates the enhanced database with complete tennis history.
        
        Args:
            players_df: Player data
            rankings_df: Rankings data
            matches_df: Match data
            doubles_df: Doubles data
            database_file: Database file path (defaults to config)
            
        Returns:
            True if successful, False otherwise
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        if self.verbose:
            print("=== Enhanced Data Loading with COMPLETE Tournament Coverage ===")
        
        # Validate required data
        if players_df.empty or matches_df.empty:
            if self.verbose:
                print("Error: Could not load required data. Exiting.")
            return False
        
        try:
            # Create database connection
            conn = sqlite3.connect(database_file)
            
            # Create tables with progress tracking
            success = self._create_tables(conn, players_df, rankings_df, matches_df, doubles_df)
            
            if success:
                # Create indexes
                if CREATE_INDEXES:
                    self._create_indexes(conn, rankings_df, doubles_df)
                
                # Create views
                self._create_views(conn, rankings_df)
                
                # Commit and close
                conn.commit()
                conn.close()
                
                if self.verbose:
                    print(f"\n✅ Database created successfully: {database_file}")
                
                return True
            else:
                conn.close()
                return False
                
        except Exception as e:
            if self.verbose:
                print(f"Error creating database: {e}")
            return False
    
    def _create_tables(self, conn: sqlite3.Connection, 
                      players_df: pd.DataFrame,
                      rankings_df: pd.DataFrame,
                      matches_df: pd.DataFrame,
                      doubles_df: pd.DataFrame) -> bool:
        """Create database tables."""
        try:
            # Initialize progress tracker
            steps = 4  # matches, players, rankings, doubles
            progress = ProgressTracker(steps, "Database Creation")
            
            # Write matches data
            progress.update(1, "Writing matches data...")
            matches_df.to_sql('matches', conn, if_exists='replace', index=False)
            
            # Write players data
            progress.update(1, "Writing players data...")
            players_df.to_sql('players', conn, if_exists='replace', index=False)
            
            # Write rankings data
            if not rankings_df.empty:
                progress.update(1, "Writing rankings data...")
                rankings_df.to_sql('rankings', conn, if_exists='replace', index=False)
            else:
                progress.update(1, "No rankings data to write.")
            
            # Write doubles data
            if not doubles_df.empty:
                progress.update(1, "Writing doubles data...")
                doubles_df.to_sql('doubles_matches', conn, if_exists='replace', index=False)
            else:
                progress.update(1, "No doubles data to write.")
            
            progress.complete("Database tables created successfully")
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Error creating tables: {e}")
            return False
    
    def _create_indexes(self, conn: sqlite3.Connection, 
                      rankings_df: pd.DataFrame,
                      doubles_df: pd.DataFrame):
        """Create database indexes for better performance."""
        if self.verbose:
            print("Creating indexes...")
        
        # Matches indexes
        matches_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_matches_winner_id ON matches(winner_id)",
            "CREATE INDEX IF NOT EXISTS idx_matches_loser_id ON matches(loser_id)",
            "CREATE INDEX IF NOT EXISTS idx_matches_year ON matches(event_year)",
            "CREATE INDEX IF NOT EXISTS idx_matches_month ON matches(event_month)",
            "CREATE INDEX IF NOT EXISTS idx_matches_surface ON matches(surface)",
            "CREATE INDEX IF NOT EXISTS idx_matches_tourney_level ON matches(tourney_level)",
            "CREATE INDEX IF NOT EXISTS idx_matches_tour ON matches(tour)"
        ]
        
        # Players indexes
        players_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_players_id ON players(player_id)",
            "CREATE INDEX IF NOT EXISTS idx_players_name ON players(full_name)",
            "CREATE INDEX IF NOT EXISTS idx_players_tour ON players(tour)"
        ]
        
        # Rankings indexes
        rankings_indexes = []
        if not rankings_df.empty:
            rankings_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_rankings_player ON rankings(player)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(ranking_date)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_rank ON rankings(rank)",
                "CREATE INDEX IF NOT EXISTS idx_rankings_tour ON rankings(tour)"
            ]
        
        # Doubles indexes
        doubles_indexes = []
        if not doubles_df.empty:
            doubles_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_doubles_winner1_id ON doubles_matches(winner1_id)",
                "CREATE INDEX IF NOT EXISTS idx_doubles_winner2_id ON doubles_matches(winner2_id)",
                "CREATE INDEX IF NOT EXISTS idx_doubles_loser1_id ON doubles_matches(loser1_id)",
                "CREATE INDEX IF NOT EXISTS idx_doubles_loser2_id ON doubles_matches(loser2_id)",
                "CREATE INDEX IF NOT EXISTS idx_doubles_year ON doubles_matches(event_year)",
                "CREATE INDEX IF NOT EXISTS idx_doubles_month ON doubles_matches(event_month)"
            ]
        
        # Execute all indexes
        all_indexes = matches_indexes + players_indexes + rankings_indexes + doubles_indexes
        
        for index_sql in all_indexes:
            try:
                conn.execute(index_sql)
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not create index: {e}")
    
    def _create_views(self, conn: sqlite3.Connection, rankings_df: pd.DataFrame):
        """Create database views for easy querying."""
        if self.verbose:
            print("Creating player-match views...")
        
        # Basic player-match views
        views = [
            """
            CREATE VIEW IF NOT EXISTS matches_with_winner_info AS
            SELECT m.*, 
                   p1.name_first as winner_first_name,
                   p1.name_last as winner_last_name,
                   p1.hand as winner_hand,
                   p1.dob as winner_dob,
                   p1.ioc as winner_ioc,
                   p1.height as winner_height,
                   p1.tour as winner_tour
            FROM matches m
            LEFT JOIN players p1 ON m.winner_id = p1.player_id
            """,
            """
            CREATE VIEW IF NOT EXISTS matches_with_loser_info AS
            SELECT m.*, 
                   p2.name_first as loser_first_name,
                   p2.name_last as loser_last_name,
                   p2.hand as loser_hand,
                   p2.dob as loser_dob,
                   p2.ioc as loser_ioc,
                   p2.height as loser_height,
                   p2.tour as loser_tour
            FROM matches m
            LEFT JOIN players p2 ON m.loser_id = p2.player_id
            """,
            """
            CREATE VIEW IF NOT EXISTS matches_with_full_info AS
            SELECT m.*,
                   p1.name_first as winner_first_name,
                   p1.name_last as winner_last_name,
                   p1.hand as winner_hand,
                   p1.dob as winner_dob,
                   p1.ioc as winner_ioc,
                   p1.height as winner_height,
                   p1.tour as winner_tour,
                   p2.name_first as loser_first_name,
                   p2.name_last as loser_last_name,
                   p2.hand as loser_hand,
                   p2.dob as loser_dob,
                   p2.ioc as loser_ioc,
                   p2.height as loser_height,
                   p2.tour as loser_tour
            FROM matches m
            LEFT JOIN players p1 ON m.winner_id = p1.player_id
            LEFT JOIN players p2 ON m.loser_id = p2.player_id
            """
        ]
        
        # Rankings-enhanced view (only if rankings data exists)
        if not rankings_df.empty:
            views.append("""
                CREATE VIEW IF NOT EXISTS matches_with_rankings AS
                SELECT m.*,
                       p1.name_first as winner_first_name,
                       p1.name_last as winner_last_name,
                       p1.hand as winner_hand,
                       p1.dob as winner_dob,
                       p1.ioc as winner_ioc,
                       p1.height as winner_height,
                       p1.tour as winner_tour,
                       p2.name_first as loser_first_name,
                       p2.name_last as loser_last_name,
                       p2.hand as loser_hand,
                       p2.dob as loser_dob,
                       p2.ioc as loser_ioc,
                       p2.height as loser_height,
                       p2.tour as loser_tour,
                       r1.rank as winner_rank_at_time,
                       r1.points as winner_points_at_time,
                       r2.rank as loser_rank_at_time,
                       r2.points as loser_points_at_time
                FROM matches m
                LEFT JOIN players p1 ON m.winner_id = p1.player_id
                LEFT JOIN players p2 ON m.loser_id = p2.player_id
                LEFT JOIN rankings r1 ON m.winner_id = r1.player 
                    AND m.event_year = CAST(strftime('%Y', r1.ranking_date) AS INTEGER)
                    AND m.event_month = CAST(strftime('%m', r1.ranking_date) AS INTEGER)
                LEFT JOIN rankings r2 ON m.loser_id = r2.player 
                    AND m.event_year = CAST(strftime('%Y', r2.ranking_date) AS INTEGER)
                    AND m.event_month = CAST(strftime('%m', r2.ranking_date) AS INTEGER)
            """)
        
        # Execute all views
        for view_sql in views:
            try:
                conn.execute(view_sql)
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not create view: {e}")
    
    def get_database_info(self, database_file: str = None) -> Dict[str, Any]:
        """
        Get information about the database.
        
        Args:
            database_file: Database file path
            
        Returns:
            Dictionary with database information
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        try:
            conn = sqlite3.connect(database_file)
            
            info = {
                'file_path': database_file,
                'file_size': self.paths.get_file_size(database_file),
                'tables': [],
                'views': [],
                'indexes': []
            }
            
            # Get tables
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            info['tables'] = [table[0] for table in tables]
            
            # Get views
            views = conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()
            info['views'] = [view[0] for view in views]
            
            # Get indexes
            indexes = conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
            info['indexes'] = [index[0] for index in indexes]
            
            conn.close()
            return info
            
        except Exception as e:
            if self.verbose:
                print(f"Error getting database info: {e}")
            return {'error': str(e)}
    
    def __str__(self):
        """String representation."""
        return f"DatabaseCreator(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"DatabaseCreator(verbose={self.verbose}, paths={self.paths})"
