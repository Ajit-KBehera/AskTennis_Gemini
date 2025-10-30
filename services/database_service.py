"""
Database Service for Enhanced UI
Provides dynamic data for dropdowns and analysis
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any
import streamlit as st  
from functools import lru_cache

class DatabaseService:
    """Service for database operations in enhanced UI."""
    
    def __init__(self, db_path: str = "tennis_data.db"):
        """Initialize database service."""
        self.db_path = db_path
    
    def clear_cache(self):
        """Clear all cached data."""
        try:
            st.cache_data.clear()
        except:
            pass
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_all_players(_self) -> List[str]:
        """Get all unique players from database."""
        try:
            conn = sqlite3.connect(_self.db_path)
            query = """
            SELECT DISTINCT winner_name as player_name FROM matches 
            WHERE winner_name IS NOT NULL AND winner_name != ''
            UNION
            SELECT DISTINCT loser_name as player_name FROM matches 
            WHERE loser_name IS NOT NULL AND loser_name != ''
            ORDER BY player_name
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return ["All Players"] + df['player_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching players: {e}")
            return ["All Players", "Roger Federer", "Rafael Nadal", "Novak Djokovic"]
    
    @st.cache_data(ttl=300)
    def get_all_tournaments(_self) -> List[str]:
        """Get all unique tournaments from database."""
        try:
            conn = sqlite3.connect(_self.db_path)
            query = """
            SELECT DISTINCT tourney_name FROM matches 
            WHERE tourney_name IS NOT NULL AND tourney_name != ''
            ORDER BY tourney_name
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return ["All Tournaments"] + df['tourney_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching tournaments: {e}")
            return ["All Tournaments", "Wimbledon", "French Open", "US Open", "Australian Open"]
    
    @st.cache_data(ttl=60)  # Cache for 1 minute
    def get_opponents_for_player(_self, player_name: str) -> List[str]:
        """Get opponents for a specific player."""
        if not player_name or player_name == "All Players":
            return _self.get_all_players()
        
        try:
            conn = sqlite3.connect(_self.db_path)
            query = """
            SELECT DISTINCT 
                CASE 
                    WHEN winner_name = ? THEN loser_name
                    WHEN loser_name = ? THEN winner_name
                END as opponent_name
            FROM matches 
            WHERE (winner_name = ? OR loser_name = ?)
            AND opponent_name IS NOT NULL
            ORDER BY opponent_name
            """
            df = pd.read_sql_query(query, conn, params=[player_name, player_name, player_name, player_name])
            conn.close()
            return ["All Opponents"] + df['opponent_name'].tolist()
        except Exception as e:
            st.error(f"Error fetching opponents: {e}")
            return _self.get_all_players()
    
    def get_matches_with_filters(self, player: str = None, opponent: str = None, 
                                tournament: str = None, year: str = None, 
                                surfaces: List[str] = None, _cache_bust: int = 0) -> pd.DataFrame:
        """Get matches based on filters."""
        try:
            # Debug logging
            st.write(f"🔍 Querying: player='{player}', year='{year}', tournament='{tournament}', surfaces='{surfaces}'")
            
            conn = sqlite3.connect(self.db_path)
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if player and player != "All Players":
                where_conditions.append("(winner_name = ? OR loser_name = ?)")
                params.extend([player, player])
            
            if opponent and opponent != "All Opponents":
                where_conditions.append("(winner_name = ? OR loser_name = ?)")
                params.extend([opponent, opponent])
            
            if tournament and tournament != "All Tournaments":
                where_conditions.append("tourney_name = ?")
                params.append(tournament)
            
            if year and year != "All Years":
                where_conditions.append("event_year = ?")
                params.append(int(year))
            
            if surfaces and len(surfaces) > 0:
                # Handle multiple surface filtering
                placeholders = ','.join(['?' for _ in surfaces])
                where_conditions.append(f"surface IN ({placeholders})")
                params.extend(surfaces)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
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
            LIMIT 5000
            """
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            # Debug logging
            st.write(f"📊 Found {len(df)} matches")
            if len(df) == 0:
                st.write(f"❌ No matches found. Query: {query}")
                st.write(f"🔧 Parameters: {params}")
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching matches: {e}")
            return pd.DataFrame()