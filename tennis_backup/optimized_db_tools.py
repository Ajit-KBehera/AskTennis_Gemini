"""
Optimized database tools for tennis queries.
Includes enhanced queries with player names and better performance.
"""

from langchain_core.tools import tool
from typing import Dict, Any, List, Optional
import json


class OptimizedDatabaseTools:
    """
    Optimized database tools with enhanced queries and better performance.
    """
    
    @staticmethod
    def create_enhanced_sql_query_tool():
        """Create an enhanced SQL query tool with better default queries."""
        @tool
        def sql_db_query_enhanced(query: str) -> str:
            """
            Execute SQL queries with enhanced performance and better results.
            Automatically includes player names and relevant context.
            
            Args:
                query: SQL query to execute
                
            Returns:
                Query results as string
            """
            # This tool should not be used - use the original sql_db_query instead
            return "ERROR: Use sql_db_query tool instead of sql_db_query_enhanced"
        
        return sql_db_query_enhanced
    
    @staticmethod
    def create_tournament_final_query_tool():
        """Create a specialized tool for tournament final queries."""
        @tool
        def get_tournament_final_results(tournament: str, year: int, round: str = "F") -> str:
            """
            Get tournament final results with player names and complete context.
            Optimized for final/semifinal queries.
            
            Args:
                tournament: Tournament name
                year: Tournament year
                round: Round (default: F for final)
                
            Returns:
                Tournament results with player names and scores
            """
            # This tool should not be used - use the original sql_db_query instead
            return "ERROR: Use sql_db_query tool instead of get_tournament_final_results"
        
        return get_tournament_final_results
    
    @staticmethod
    def create_surface_performance_query_tool():
        """Create a specialized tool for surface performance queries."""
        @tool
        def get_surface_performance_results(surface: str, year: int, limit: int = 10) -> str:
            """
            Get surface performance results with player names and win counts.
            Optimized for surface-specific queries.
            
            Args:
                surface: Surface type (Clay, Hard, Grass, Carpet)
                year: Year to analyze
                limit: Number of results to return
                
            Returns:
                Surface performance results with player names
            """
            # This tool should not be used - use the original sql_db_query instead
            return "ERROR: Use sql_db_query tool instead of get_surface_performance_results"
        
        return get_surface_performance_results
    
    @staticmethod
    def create_head_to_head_query_tool():
        """Create a specialized tool for head-to-head queries."""
        @tool
        def get_head_to_head_results(player1: str, player2: str) -> str:
            """
            Get head-to-head results between two players with complete match details.
            Optimized for player comparison queries.
            
            Args:
                player1: First player name
                player2: Second player name
                
            Returns:
                Head-to-head results with match details
            """
            # This tool should not be used - use the original sql_db_query instead
            return "ERROR: Use sql_db_query tool instead of get_head_to_head_results"
        
        return get_head_to_head_results
    
    @staticmethod
    def create_all_optimized_tools() -> List:
        """
        Create all optimized database tools.
        
        Returns:
            List of all optimized tools
        """
        return [
            OptimizedDatabaseTools.create_enhanced_sql_query_tool(),
            OptimizedDatabaseTools.create_tournament_final_query_tool(),
            OptimizedDatabaseTools.create_surface_performance_query_tool(),
            OptimizedDatabaseTools.create_head_to_head_query_tool()
        ]


class QueryOptimizer:
    """
    Query optimization utilities for tennis database queries.
    """
    
    @staticmethod
    def optimize_tournament_query(tournament: str, year: int, round: str = "F") -> str:
        """
        Generate an optimized tournament query with player names and context.
        
        Args:
            tournament: Tournament name
            year: Tournament year
            round: Round (default: F for final)
            
        Returns:
            Optimized SQL query
        """
        return f"""
        SELECT 
            winner_name, 
            loser_name, 
            tourney_name, 
            event_year, 
            event_month, 
            event_date, 
            round, 
            surface,
            set1, set2, set3, set4, set5
        FROM matches 
        WHERE tourney_name = '{tournament}' 
          AND event_year = {year} 
          AND round = '{round}'
          AND winner_name IS NOT NULL 
          AND loser_name IS NOT NULL
        ORDER BY event_date
        """
    
    @staticmethod
    def optimize_surface_query(surface: str, year: int, limit: int = 10) -> str:
        """
        Generate an optimized surface performance query.
        
        Args:
            surface: Surface type
            year: Year to analyze
            limit: Number of results
            
        Returns:
            Optimized SQL query
        """
        return f"""
        SELECT 
            winner_name, 
            COUNT(*) as wins,
            surface,
            tourney_name,
            event_year
        FROM matches 
        WHERE surface = '{surface}' 
          AND event_year = {year}
          AND winner_name IS NOT NULL
        GROUP BY winner_name, surface, tourney_name, event_year
        ORDER BY wins DESC
        LIMIT {limit}
        """
    
    @staticmethod
    def optimize_head_to_head_query(player1: str, player2: str) -> str:
        """
        Generate an optimized head-to-head query.
        
        Args:
            player1: First player name
            player2: Second player name
            
        Returns:
            Optimized SQL query
        """
        return f"""
        SELECT 
            winner_name, 
            loser_name, 
            tourney_name, 
            event_year, 
            event_month, 
            event_date, 
            surface,
            set1, set2, set3, set4, set5
        FROM matches 
        WHERE ((winner_name LIKE '%{player1}%' AND loser_name LIKE '%{player2}%') 
            OR (winner_name LIKE '%{player2}%' AND loser_name LIKE '%{player1}%'))
          AND winner_name IS NOT NULL 
          AND loser_name IS NOT NULL
          AND set1 NOT LIKE '%W/O%'
          AND set1 NOT LIKE '%DEF%'
          AND set1 NOT LIKE '%RET%'
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        """
