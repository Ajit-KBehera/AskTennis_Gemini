"""
Database Service for Enhanced UI
Provides dynamic data for dropdowns and analysis
"""

import sqlite3
import pandas as pd
from typing import List, Optional
import streamlit as st
from constants import DEFAULT_DB_PATH

class DatabaseService:
    """Service for database operations in enhanced UI."""
    
    # Constants for filter options
    ALL_PLAYERS = "All Players"
    ALL_TOURNAMENTS = "All Tournaments"
    ALL_OPPONENTS = "All Opponents"
    ALL_YEARS = "All Years"
    
    # Configuration constants
    MIN_YEAR = 1900
    MAX_YEAR = 2100
    DEFAULT_QUERY_LIMIT = 5000
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database service."""
        if db_path is None:
            # Extract file path from SQLAlchemy URI format if present
            db_path = DEFAULT_DB_PATH
            if db_path.startswith("sqlite:///"):
                db_path = db_path.replace("sqlite:///", "")
            elif db_path.startswith("sqlite://"):
                db_path = db_path.replace("sqlite://", "")
        self.db_path = db_path
    
    @staticmethod
    def _sanitize_string(value: Optional[str]) -> Optional[str]:
        """Sanitize string input by trimming whitespace and handling empty strings.
        
        Args:
            value: String value to sanitize
            
        Returns:
            Sanitized string or None if value is empty/invalid
        """
        if not value or not isinstance(value, str):
            return None
        sanitized = value.strip()
        return sanitized if sanitized else None
    
    def clear_cache(self):
        """Clear all cached data."""
        try:
            st.cache_data.clear()
        except Exception:
            # Cache clearing is optional, fail silently if not available
            pass
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_all_players(_self) -> List[str]:
        """Get all unique players from database."""
        try:
            with sqlite3.connect(_self.db_path) as conn:
                query = """
                SELECT DISTINCT 
                    COALESCE(full_name, name_first || ' ' || name_last) as player_name
                FROM players 
                WHERE (full_name IS NOT NULL AND full_name != '') 
                   OR (name_first IS NOT NULL AND name_last IS NOT NULL)
                ORDER BY player_name
                """
                df = pd.read_sql_query(query, conn)
            if df.empty or 'player_name' not in df.columns:
                return [DatabaseService.ALL_PLAYERS]
            return [DatabaseService.ALL_PLAYERS] + df['player_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching players: {e}")
            return [DatabaseService.ALL_PLAYERS, "Roger Federer", "Rafael Nadal", "Novak Djokovic"]
    
    @st.cache_data(ttl=300)
    def get_all_tournaments(_self) -> List[str]:
        """Get all unique tournaments from database."""
        try:
            with sqlite3.connect(_self.db_path) as conn:
                query = """
                SELECT DISTINCT tourney_name FROM matches 
                WHERE tourney_name IS NOT NULL AND tourney_name != ''
                ORDER BY tourney_name
                """
                df = pd.read_sql_query(query, conn)
            if df.empty or 'tourney_name' not in df.columns:
                return [DatabaseService.ALL_TOURNAMENTS]
            return [DatabaseService.ALL_TOURNAMENTS] + df['tourney_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching tournaments: {e}")
            return [DatabaseService.ALL_TOURNAMENTS, "Wimbledon", "French Open", "US Open", "Australian Open"]
    
    @st.cache_data(ttl=60)  # Cache for 1 minute
    def get_opponents_for_player(_self, player_name: str) -> List[str]:
        """Get opponents for a specific player."""
        # Sanitize input: trim whitespace and handle empty strings
        player_name = _self._sanitize_string(player_name)
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            return _self.get_all_players()
        
        try:
            with sqlite3.connect(_self.db_path) as conn:
                query = """
                SELECT DISTINCT opponent_name
                FROM (
                    SELECT loser_name as opponent_name
                    FROM matches 
                    WHERE winner_name = ? AND loser_name IS NOT NULL
                    UNION ALL
                    SELECT winner_name as opponent_name
                    FROM matches 
                    WHERE loser_name = ? AND winner_name IS NOT NULL
                )
                ORDER BY opponent_name
                """
                df = pd.read_sql_query(query, conn, params=[player_name, player_name])
            if df.empty or 'opponent_name' not in df.columns:
                return [DatabaseService.ALL_OPPONENTS]
            return [DatabaseService.ALL_OPPONENTS] + df['opponent_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching opponents: {e}")
            return _self.get_all_players()
    
    def get_matches_with_filters(self, player: Optional[str] = None, 
                                opponent: Optional[str] = None, 
                                tournament: Optional[str] = None, 
                                year: Optional[str] = None, 
                                surfaces: Optional[List[str]] = None,
                                return_all_columns: bool = False,
                                _cache_bust: int = 0) -> pd.DataFrame:
        """Get matches based on filters."""
        try:
            # Sanitize string inputs: trim whitespace and handle None/empty strings
            player = self._sanitize_string(player)
            opponent = self._sanitize_string(opponent)
            tournament = self._sanitize_string(tournament)
            year = self._sanitize_string(year)
            
            # Debug logging
            st.write(f"🔍 Querying: player='{player}', year='{year}', tournament='{tournament}', surfaces='{surfaces}'")
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            # Optimize: if both player and opponent are specified, combine them into one condition
            # Use COLLATE NOCASE for case-insensitive matching
            if player and player != self.ALL_PLAYERS and opponent and opponent != self.ALL_OPPONENTS:
                # Match where both players are involved (either order)
                where_conditions.append("((winner_name COLLATE NOCASE = ? AND loser_name COLLATE NOCASE = ?) OR (winner_name COLLATE NOCASE = ? AND loser_name COLLATE NOCASE = ?))")
                params.extend([player, opponent, opponent, player])
            else:
                # Handle player and opponent separately if only one is specified
                if player and player != self.ALL_PLAYERS:
                    where_conditions.append("(winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)")
                    params.extend([player, player])
                
                if opponent and opponent != self.ALL_OPPONENTS:
                    where_conditions.append("(winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)")
                    params.extend([opponent, opponent])
            
            if tournament and tournament != self.ALL_TOURNAMENTS:
                where_conditions.append("tourney_name = ?")
                params.append(tournament)
            
            if year and year != self.ALL_YEARS:
                try:
                    year_int = int(year)
                    # Validate reasonable year range
                    if self.MIN_YEAR <= year_int <= self.MAX_YEAR:
                        where_conditions.append("event_year = ?")
                        params.append(year_int)
                    else:
                        st.warning(f"Invalid year range: {year_int}. Skipping year filter.")
                except (ValueError, TypeError):
                    st.warning(f"Invalid year format: {year}. Skipping year filter.")
            
            if surfaces:
                # Filter and validate surfaces: remove empty strings, None values, and strip whitespace
                valid_surfaces = [
                    s.strip() for s in surfaces 
                    if s and isinstance(s, str) and s.strip()
                ]
                
                if valid_surfaces:
                    # Handle multiple surface filtering
                    placeholders = ','.join(['?' for _ in valid_surfaces])
                    where_conditions.append(f"surface IN ({placeholders})")
                    params.extend(valid_surfaces)
                elif len(surfaces) > 0:
                    # User provided surfaces but all were invalid
                    st.warning(f"Invalid surface values provided. Skipping surface filter.")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Select columns based on return_all_columns parameter
            if return_all_columns:
                # Return all columns for chart generation
                query = f"""
                SELECT *
                FROM matches 
                WHERE {where_clause}
                ORDER BY tourney_date ASC, match_num ASC
                LIMIT {self.DEFAULT_QUERY_LIMIT}
                """
            else:
                # Return selected columns for table display
                query = f"""
                SELECT
                    event_year,
                    tourney_date,
                    tourney_name,
                    round,
                    winner_name,
                    loser_name,
                    surface,
                    score
                FROM matches 
                WHERE {where_clause}
                ORDER BY tourney_date ASC, match_num ASC
                LIMIT {self.DEFAULT_QUERY_LIMIT}
                """
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
            
            # Debug logging
            st.write(f"📊 Found {len(df)} matches")
            if len(df) == 0:
                st.write(f"❌ No matches found. Query: {query}")
                st.write(f"🔧 Parameters: {params}")
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching matches: {e}")
            return pd.DataFrame()