"""
Database Service for Enhanced UI
Provides dynamic data for dropdowns and analysis
"""

import sqlite3
import pandas as pd
from typing import List, Optional, Union, Tuple
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
        """Get all unique players from database who have played matches."""
        try:
            with sqlite3.connect(_self.db_path) as conn:
                query = """
                SELECT player_name
                FROM (
                    SELECT winner_name as player_name
                    FROM matches 
                    WHERE winner_name IS NOT NULL AND winner_name != ''
                    UNION
                    SELECT loser_name as player_name
                    FROM matches 
                    WHERE loser_name IS NOT NULL AND loser_name != ''
                )
                ORDER BY player_name
                """
                df = pd.read_sql_query(query, conn)
            if df.empty:
                return [DatabaseService.ALL_PLAYERS]
            return [DatabaseService.ALL_PLAYERS] + df['player_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching players: {e}")
            return [DatabaseService.ALL_PLAYERS, "Roger Federer", "Rafael Nadal", "Novak Djokovic"]
    
    @st.cache_data(ttl=60)  # Cache for 1 minute (shorter TTL since it depends on player selection)
    def get_all_tournaments(_self, player_name: Optional[str] = None) -> List[str]:
        """Get tournaments from database, optionally filtered by player.
        
        Args:
            player_name: Optional player name to filter tournaments. If None or "All Players", 
                        returns all tournaments.
        
        Returns:
            List[str]: List of tournaments with "All Tournaments" as first element
        """
        # Sanitize input: trim whitespace and handle empty strings
        player_name = _self._sanitize_string(player_name)
        
        # If no player specified or "All Players", return all tournaments
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            try:
                with sqlite3.connect(_self.db_path) as conn:
                    query = """
                    SELECT DISTINCT tourney_name FROM matches 
                    WHERE tourney_name IS NOT NULL AND tourney_name != ''
                    ORDER BY tourney_name
                    """
                    df = pd.read_sql_query(query, conn)
                if df.empty:
                    return [DatabaseService.ALL_TOURNAMENTS]
                return [DatabaseService.ALL_TOURNAMENTS] + df['tourney_name'].tolist()
            except Exception as e:
                st.error(f"Error fetching tournaments: {e}")
                return [DatabaseService.ALL_TOURNAMENTS, "Wimbledon", "French Open", "US Open", "Australian Open"]
        
        # Filter tournaments for specific player
        try:
            with sqlite3.connect(_self.db_path) as conn:
                query = """
                SELECT DISTINCT tourney_name
                FROM matches 
                WHERE (winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)
                  AND tourney_name IS NOT NULL AND tourney_name != ''
                ORDER BY tourney_name
                """
                df = pd.read_sql_query(query, conn, params=[player_name, player_name])
            if df.empty:
                return [DatabaseService.ALL_TOURNAMENTS]
            return [DatabaseService.ALL_TOURNAMENTS] + df['tourney_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching tournaments for player: {e}")
            # Fallback to all tournaments on error
            try:
                with sqlite3.connect(_self.db_path) as conn:
                    query = """
                    SELECT DISTINCT tourney_name FROM matches 
                    WHERE tourney_name IS NOT NULL AND tourney_name != ''
                    ORDER BY tourney_name
                    """
                    df = pd.read_sql_query(query, conn)
                if df.empty:
                    return [DatabaseService.ALL_TOURNAMENTS]
                return [DatabaseService.ALL_TOURNAMENTS] + df['tourney_name'].tolist()
            except Exception:
                return [DatabaseService.ALL_TOURNAMENTS, "Wimbledon", "French Open", "US Open", "Australian Open"]
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_player_year_range(_self, player_name: str) -> Tuple[int, int]:
        """Get the year range (min and max event_year) for a specific player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Tuple[int, int]: (min_year, max_year) or (1968, 2025) if no matches found
        """
        player_name = _self._sanitize_string(player_name)
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            return (1968, 2024)  # Default range
        
        try:
            with sqlite3.connect(_self.db_path) as conn:
                query = """
                SELECT MIN(event_year) as min_year, MAX(event_year) as max_year
                FROM matches 
                WHERE (winner_name COLLATE NOCASE = ? OR loser_name COLLATE NOCASE = ?)
                  AND event_year IS NOT NULL
                """
                df = pd.read_sql_query(query, conn, params=[player_name, player_name])
            
            if df.empty or df['min_year'].iloc[0] is None or df['max_year'].iloc[0] is None:
                return (1968, 2024)  # Default range if no matches found
            
            min_year = int(df['min_year'].iloc[0])
            max_year = int(df['max_year'].iloc[0])
            
            # Ensure valid range
            if min_year < _self.MIN_YEAR:
                min_year = _self.MIN_YEAR
            if max_year > _self.MAX_YEAR:
                max_year = _self.MAX_YEAR
            
            return (min_year, max_year)
        except Exception as e:
            st.warning(f"Error fetching year range for player: {e}")
            return (1968, 2024)  # Default range on error
    
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
            if df.empty:
                return [DatabaseService.ALL_OPPONENTS]
            return [DatabaseService.ALL_OPPONENTS] + df['opponent_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching opponents: {e}")
            return _self.get_all_players()
    
    def get_matches_with_filters(self, player: Optional[str] = None, 
                                opponent: Optional[str] = None, 
                                tournament: Optional[str] = None, 
                                year: Optional[Union[int, str, Tuple[int, int], List[int]]] = None, 
                                surfaces: Optional[List[str]] = None,
                                return_all_columns: bool = False,
                                _cache_bust: int = 0) -> pd.DataFrame:
        """Get matches based on filters."""
        try:
            # Sanitize string inputs: trim whitespace and handle None/empty strings
            player = self._sanitize_string(player)
            opponent = self._sanitize_string(opponent)
            tournament = self._sanitize_string(tournament)
            # Don't sanitize year - it can be int, tuple, list, or str
            
            # Debug logging - format year for display
            year_display = year
            if isinstance(year, tuple):
                year_display = f"{year[0]}-{year[1]}"
            elif isinstance(year, list):
                year_display = f"{min(year)}-{max(year)}" if len(year) > 1 else str(year[0])
            st.write(f"🔍 Querying: player='{player}', year={year_display}, tournament='{tournament}', surfaces='{surfaces}'")
            
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
            
            # Handle year filtering: supports None, int, tuple (range), or list
            if year is not None and year != self.ALL_YEARS:
                try:
                    # Handle tuple (year range) - use BETWEEN for efficiency
                    if isinstance(year, tuple) and len(year) == 2:
                        start_year, end_year = int(year[0]), int(year[1])
                        # Ensure start <= end
                        if start_year > end_year:
                            start_year, end_year = end_year, start_year
                        
                        # Validate year range
                        if (self.MIN_YEAR <= start_year <= self.MAX_YEAR and 
                            self.MIN_YEAR <= end_year <= self.MAX_YEAR):
                            where_conditions.append("event_year BETWEEN ? AND ?")
                            params.extend([start_year, end_year])
                        else:
                            st.warning(f"Invalid year range: {start_year}-{end_year}. Skipping year filter.")
                    
                    # Handle list (multiple specific years) - use IN
                    elif isinstance(year, list) and len(year) > 0:
                        year_list = [int(y) for y in year if isinstance(y, (int, str)) and str(y).isdigit()]
                        # Validate all years
                        valid_years = [y for y in year_list if self.MIN_YEAR <= y <= self.MAX_YEAR]
                        
                        if valid_years:
                            if len(valid_years) == 1:
                                # Single year in list - use equality
                                where_conditions.append("event_year = ?")
                                params.append(valid_years[0])
                            else:
                                # Multiple years - use IN
                                placeholders = ','.join(['?' for _ in valid_years])
                                where_conditions.append(f"event_year IN ({placeholders})")
                                params.extend(valid_years)
                        else:
                            st.warning(f"Invalid year values in list. Skipping year filter.")
                    
                    # Handle single integer year
                    elif isinstance(year, int):
                        if self.MIN_YEAR <= year <= self.MAX_YEAR:
                            where_conditions.append("event_year = ?")
                            params.append(year)
                        else:
                            st.warning(f"Invalid year range: {year}. Skipping year filter.")
                    
                    # Handle string (backward compatibility)
                    elif isinstance(year, str):
                        year_int = int(year)
                        if self.MIN_YEAR <= year_int <= self.MAX_YEAR:
                            where_conditions.append("event_year = ?")
                            params.append(year_int)
                        else:
                            st.warning(f"Invalid year range: {year_int}. Skipping year filter.")
                    else:
                        st.warning(f"Invalid year format: {type(year)}. Expected int, tuple, list, or str. Skipping year filter.")
                        
                except (ValueError, TypeError) as e:
                    st.warning(f"Invalid year format: {year}. Error: {e}. Skipping year filter.")
            
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
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_player_ranking_timeline(_self, player_name: str, year: Optional[Union[int, str, Tuple[int, int], List[int]]] = None) -> pd.DataFrame:
        """
        Get ranking timeline data for a specific player from both ATP and WTA rankings.
        
        Args:
            player_name: Name of the player
            year: Optional year filter. Can be:
                - None: All years
                - int: Single year
                - tuple: Year range (start_year, end_year)
                - list: Multiple specific years
            
        Returns:
            DataFrame with columns: ranking_date, rank, tour (ATP/WTA)
        """
        player_name = _self._sanitize_string(player_name)
        if not player_name or player_name == DatabaseService.ALL_PLAYERS:
            return pd.DataFrame()
        
        try:
            with sqlite3.connect(_self.db_path) as conn:
                # Build year filter clause for ranking_date
                year_filter_clause = ""
                year_params = []
                
                if year is not None and year != _self.ALL_YEARS:
                    try:
                        # Handle tuple (year range) - use BETWEEN for efficiency
                        if isinstance(year, tuple) and len(year) == 2:
                            start_year, end_year = int(year[0]), int(year[1])
                            # Ensure start <= end
                            if start_year > end_year:
                                start_year, end_year = end_year, start_year
                            
                            # Validate year range
                            if (_self.MIN_YEAR <= start_year <= _self.MAX_YEAR and 
                                _self.MIN_YEAR <= end_year <= _self.MAX_YEAR):
                                year_filter_clause = "AND CAST(strftime('%Y', ranking_date) AS INTEGER) BETWEEN ? AND ?"
                                year_params = [start_year, end_year]
                        
                        # Handle list (multiple specific years) - use IN
                        elif isinstance(year, list) and len(year) > 0:
                            year_list = [int(y) for y in year if isinstance(y, (int, str)) and str(y).isdigit()]
                            # Validate all years
                            valid_years = [y for y in year_list if _self.MIN_YEAR <= y <= _self.MAX_YEAR]
                            
                            if valid_years:
                                if len(valid_years) == 1:
                                    # Single year in list - use equality
                                    year_filter_clause = "AND CAST(strftime('%Y', ranking_date) AS INTEGER) = ?"
                                    year_params = [valid_years[0]]
                                else:
                                    # Multiple years - use IN
                                    placeholders = ','.join(['?' for _ in valid_years])
                                    year_filter_clause = f"AND CAST(strftime('%Y', ranking_date) AS INTEGER) IN ({placeholders})"
                                    year_params = valid_years
                        
                        # Handle single integer year
                        elif isinstance(year, int):
                            if _self.MIN_YEAR <= year <= _self.MAX_YEAR:
                                year_filter_clause = "AND CAST(strftime('%Y', ranking_date) AS INTEGER) = ?"
                                year_params = [year]
                        
                        # Handle string (backward compatibility)
                        elif isinstance(year, str):
                            year_int = int(year)
                            if _self.MIN_YEAR <= year_int <= _self.MAX_YEAR:
                                year_filter_clause = "AND CAST(strftime('%Y', ranking_date) AS INTEGER) = ?"
                                year_params = [year_int]
                                
                    except (ValueError, TypeError) as e:
                        # If year filtering fails, just continue without year filter
                        pass
                
                # Query ATP rankings - join with atp_players to get player name
                atp_query = f"""
                SELECT ar.ranking_date, ar.rank, 'ATP' as tour
                FROM atp_rankings ar
                JOIN atp_players ap ON ar.player = ap.player_id
                WHERE (COALESCE(ap.full_name, ap.name_first || ' ' || ap.name_last) COLLATE NOCASE = ?
                    OR ap.full_name COLLATE NOCASE = ?
                    OR (ap.name_first || ' ' || ap.name_last) COLLATE NOCASE = ?)
                  AND ar.ranking_date IS NOT NULL
                  AND ar.rank IS NOT NULL
                  {year_filter_clause}
                ORDER BY ar.ranking_date ASC
                """
                
                # Query WTA rankings - join with wta_players to get player name
                wta_query = f"""
                SELECT wr.ranking_date, wr.rank, 'WTA' as tour
                FROM wta_rankings wr
                JOIN wta_players wp ON wr.player = wp.player_id
                WHERE (COALESCE(wp.full_name, wp.name_first || ' ' || wp.name_last) COLLATE NOCASE = ?
                    OR wp.full_name COLLATE NOCASE = ?
                    OR (wp.name_first || ' ' || wp.name_last) COLLATE NOCASE = ?)
                  AND wr.ranking_date IS NOT NULL
                  AND wr.rank IS NOT NULL
                  {year_filter_clause}
                ORDER BY wr.ranking_date ASC
                """
                
                # Execute both queries with player name params + year params
                player_params = [player_name, player_name, player_name]
                atp_df = pd.read_sql_query(atp_query, conn, params=player_params + year_params)
                wta_df = pd.read_sql_query(wta_query, conn, params=player_params + year_params)
                
                # Combine results
                if not atp_df.empty and not wta_df.empty:
                    combined_df = pd.concat([atp_df, wta_df], ignore_index=True)
                elif not atp_df.empty:
                    combined_df = atp_df
                elif not wta_df.empty:
                    combined_df = wta_df
                else:
                    return pd.DataFrame()
                
                # Sort by date
                combined_df['ranking_date'] = pd.to_datetime(combined_df['ranking_date'])
                combined_df = combined_df.sort_values('ranking_date').reset_index(drop=True)
                
                return combined_df
                
        except Exception as e:
            st.warning(f"Error fetching ranking timeline for {player_name}: {e}")
            return pd.DataFrame()