"""
Unified Tennis Core Module
Consolidated tennis functionality with optimized performance and clean architecture.
"""

from langchain_core.tools import tool
from typing import Dict, Any, List, Optional
from functools import lru_cache
import json
import pandas as pd
from datetime import datetime
import time
from functools import wraps
from tennis.tennis_visualization_tools import TennisVisualizationTools

# =============================================================================
# TENNIS MAPPING DICTIONARIES
# =============================================================================

ROUND_MAPPINGS = {
    # Finals
    "final": "F", "finals": "F", "championship": "F", "champion": "F", "winner": "F",
    
    # Semi-Finals
    "semi-final": "SF", "semi finals": "SF", "semifinal": "SF", "semifinals": "SF",
    "semi": "SF", "last four": "SF", "last 4": "SF",
    
    # Quarter-Finals
    "quarter-final": "QF", "quarter finals": "QF", "quarterfinal": "QF", "quarterfinals": "QF",
    "quarter": "QF", "quarters": "QF", "last eight": "QF", "last 8": "QF",
    
    # Round of 16
    "round of 16": "R16", "round 16": "R16", "last 16": "R16", "fourth round": "R16", "4th round": "R16",
    
    # Round of 32
    "round of 32": "R32", "round 32": "R32", "third round": "R32", "3rd round": "R32",
    
    # Round of 64
    "round of 64": "R64", "round 64": "R64", "second round": "R64", "2nd round": "R64",
    
    # Round of 128
    "round of 128": "R128", "round 128": "R128", "first round": "R128", "1st round": "R128",
    
    # Qualifying rounds
    "qualifying": "Q1", "qualifier": "Q1", "qualifying 1": "Q1", "qualifying 2": "Q2", "qualifying 3": "Q3",
    
    # Round Robin
    "round robin": "RR", "group stage": "RR", "group": "RR",
    
    # Other rounds
    "bronze": "BR", "playoff": "PR", "consolation": "CR", "exhibition": "ER"
}

SURFACE_MAPPINGS = {
    # Clay courts
    "clay": "Clay", "clay court": "Clay", "red clay": "Clay", "terre battue": "Clay",
    "dirt": "Clay", "slow court": "Clay",
    
    # Hard courts
    "hard": "Hard", "hard court": "Hard", "concrete": "Hard", "asphalt": "Hard",
    "acrylic": "Hard", "deco turf": "Hard", "plexicushion": "Hard", "fast court": "Hard",
    "indoor hard": "Hard", "outdoor hard": "Hard",
    
    # Grass courts
    "grass": "Grass", "grass court": "Grass", "lawn": "Grass", "natural grass": "Grass",
    "very fast court": "Grass", "quick court": "Grass",
    
    # Carpet courts
    "carpet": "Carpet", "carpet court": "Carpet", "indoor carpet": "Carpet",
    "synthetic": "Carpet", "artificial": "Carpet"
}

TOUR_MAPPINGS = {
    # Main tours
    "atp": "ATP", "atp tour": "ATP", "men's tour": "ATP", "men tour": "ATP", "men": "ATP", "male": "ATP",
    "wta": "WTA", "wta tour": "WTA", "women's tour": "WTA", "women tour": "WTA", "women": "WTA", "female": "WTA", "ladies": "WTA",
    
    # Development tours
    "challenger": "Challenger", "atp challenger": "Challenger", "challenger tour": "Challenger", "development tour": "Challenger",
    "futures": "Futures", "atp futures": "Futures", "futures tour": "Futures", "itf futures": "Futures",
    "itf": "ITF", "itf tour": "ITF", "junior tour": "ITF", "development": "ITF",
    
    # Combined
    "both": "Both", "combined": "Both", "men and women": "Both", "atp and wta": "Both"
}

HAND_MAPPINGS = {
    # Right-handed
    "right": "R", "right-handed": "R", "right hand": "R", "righty": "R", "right handed": "R",
    
    # Left-handed
    "left": "L", "left-handed": "L", "left hand": "L", "lefty": "L", "left handed": "L", "southpaw": "L",
    
    # Ambidextrous
    "ambidextrous": "A", "both": "A", "either": "A", "switch": "A",
    
    # Unknown
    "unknown": "U", "unclear": "U", "not specified": "U"
}

GRAND_SLAM_MAPPINGS = {
    "french open": "Roland Garros", "roland garros": "Roland Garros",
    "aus open": "Australian Open", "australian open": "Australian Open",
    "wimbledon": "Wimbledon", "the championship": "Wimbledon",
    "us open": "US Open"
}

TOURNEY_LEVEL_MAPPINGS = {
    # ATP Levels
    'G': 'G',  # Grand Slam
    'M': 'M',  # Masters 1000
    'A': 'A',  # ATP Tour
    'C': 'C',  # Challenger
    'D': 'D',  # Davis Cup (ATP only)
    'F': 'F',  # Tour Finals
    'E': 'E',  # Exhibition
    'J': 'J',  # Juniors
    'O': 'O',  # Olympics
    
    # WTA Levels
    'PM': 'PM',  # Premier Mandatory
    'P': 'P',    # Premier
    'I': 'I',    # International
    'W': 'W',    # WTA Tour
    'CC': 'CC',  # Colgate Series
    
    # Historical WTA Tiers → Modern equivalents
    'T1': 'PM',  # Tier I → Premier Mandatory
    'T2': 'P',   # Tier II → Premier
    'T3': 'I',   # Tier III → International
    'T4': 'I',   # Tier IV → International
    'T5': 'I',   # Tier V → International
    
    # ITF Prize Money Levels
    '10': 'ITF_10K', '15': 'ITF_15K', '20': 'ITF_20K', '25': 'ITF_25K',
    '35': 'ITF_35K', '40': 'ITF_40K', '50': 'ITF_50K', '60': 'ITF_60K',
    '75': 'ITF_75K', '80': 'ITF_80K', '100': 'ITF_100K', '200': 'ITF_200K'
}

COMBINED_TOURNAMENT_MAPPINGS = {
    "rome": {"atp": "Rome Masters", "wta": "Rome"},
    "basel": {"atp": "Basel", "wta": "Basel"},
    "madrid": {"atp": "Madrid Masters", "wta": "Madrid"},
    "indian wells": {"atp": "Indian Wells Masters", "wta": "Indian Wells"},
    "miami": {"atp": "Miami Masters", "wta": "Miami"},
    "monte carlo": {"atp": "Monte Carlo Masters", "wta": "Monte Carlo"},
    "hamburg": {"atp": "Hamburg", "wta": "Hamburg"},
    "stuttgart": {"atp": "Stuttgart", "wta": "Stuttgart"},
    "eastbourne": {"atp": "Eastbourne", "wta": "Eastbourne"},
    "newport": {"atp": "Newport", "wta": "Newport"},
    "atlanta": {"atp": "Atlanta", "wta": "Atlanta"},
    "washington": {"atp": "Washington", "wta": "Washington"},
    "toronto": {"atp": "Toronto Masters", "wta": "Toronto"},
    "montreal": {"atp": "Montreal Masters", "wta": "Montreal"},
    "cincinnati": {"atp": "Cincinnati Masters", "wta": "Cincinnati"},
    "winston salem": {"atp": "Winston Salem", "wta": "Winston Salem"},
    "stockholm": {"atp": "Stockholm", "wta": "Stockholm"},
    "antwerp": {"atp": "Antwerp", "wta": "Antwerp"},
    "vienna": {"atp": "Vienna", "wta": "Vienna"},
    "paris": {"atp": "Paris Masters", "wta": "Paris"}
}

# =============================================================================
# CACHED MAPPING FUNCTIONS
# =============================================================================

@lru_cache(maxsize=128)
def _get_round_mapping(round_name: str) -> str:
    """Cached round mapping function."""
    round_lower = round_name.lower().strip()
    
    if round_lower in ROUND_MAPPINGS:
        return json.dumps({"database_round": ROUND_MAPPINGS[round_lower], "type": "tennis_round"})
    
    return json.dumps({"database_round": round_name, "type": "unknown"})

@lru_cache(maxsize=128)
def _get_surface_mapping(surface: str) -> str:
    """Cached surface mapping function."""
    surface_lower = surface.lower().strip()
    
    if surface_lower in SURFACE_MAPPINGS:
        return json.dumps({"database_surface": SURFACE_MAPPINGS[surface_lower], "type": "tennis_surface"})
    
    return json.dumps({"database_surface": surface, "type": "unknown"})

@lru_cache(maxsize=128)
def _get_tour_mapping(tour: str) -> str:
    """Cached tour mapping function."""
    tour_lower = tour.lower().strip()
    
    if tour_lower in TOUR_MAPPINGS:
        return json.dumps({"database_tour": TOUR_MAPPINGS[tour_lower], "type": "tennis_tour"})
    
    return json.dumps({"database_tour": tour, "type": "unknown"})

@lru_cache(maxsize=128)
def _get_hand_mapping(hand: str) -> str:
    """Cached hand mapping function."""
    hand_lower = hand.lower().strip()
    
    if hand_lower in HAND_MAPPINGS:
        return json.dumps({"database_hand": HAND_MAPPINGS[hand_lower], "type": "tennis_hand"})
    
    return json.dumps({"database_hand": hand, "type": "unknown"})

@lru_cache(maxsize=128)
def _get_tournament_mapping(tournament: str) -> str:
    """Cached tournament mapping function."""
    tournament_lower = tournament.lower().strip()
    
    # Check Grand Slams first
    if tournament_lower in GRAND_SLAM_MAPPINGS:
        return json.dumps({"database_name": GRAND_SLAM_MAPPINGS[tournament_lower], "type": "grand_slam"})
    
    # Check combined tournaments
    if tournament_lower in COMBINED_TOURNAMENT_MAPPINGS:
        return json.dumps(COMBINED_TOURNAMENT_MAPPINGS[tournament_lower])
    
    return json.dumps({"database_name": tournament, "type": "unknown"})

# =============================================================================
# TENNIS MAPPING TOOLS
# =============================================================================

class TennisMappingTools:
    """Unified tennis mapping tools with caching and performance optimization."""
    
    @staticmethod
    def create_round_mapping_tool():
        """Create the tennis round mapping tool."""
        @tool
        def get_tennis_round_mapping(round_name: str) -> str:
            """
            Map tennis fan colloquial round names to database round values.
            Handles various tennis round terminologies with caching.
            
            Args:
                round_name: The round name to look up (e.g., 'final', 'semi-final', 'quarter-final')
                
            Returns:
                JSON string with database round value
            """
            return _get_round_mapping(round_name)
        
        return get_tennis_round_mapping
    
    @staticmethod
    def create_surface_mapping_tool():
        """Create the tennis surface mapping tool."""
        @tool
        def get_tennis_surface_mapping(surface: str) -> str:
            """
            Map tennis fan surface names to database surface values.
            Handles various surface terminologies with caching.
            
            Args:
                surface: The surface name to look up (e.g., 'clay court', 'hard court', 'grass court')
                
            Returns:
                JSON string with database surface value
            """
            return _get_surface_mapping(surface)
        
        return get_tennis_surface_mapping
    
    @staticmethod
    def create_tour_mapping_tool():
        """Create the tennis tour mapping tool."""
        @tool
        def get_tennis_tour_mapping(tour: str) -> str:
            """
            Map tennis fan tour names to database tour values.
            Handles various tour terminologies with caching.
            
            Args:
                tour: The tour name to look up (e.g., 'atp', 'wta', 'challenger')
                
            Returns:
                JSON string with database tour value
            """
            return _get_tour_mapping(tour)
        
        return get_tennis_tour_mapping
    
    @staticmethod
    def create_hand_mapping_tool():
        """Create the tennis hand mapping tool."""
        @tool
        def get_tennis_hand_mapping(hand: str) -> str:
            """
            Map tennis fan hand names to database hand values.
            Handles various hand terminologies with caching.
            
            Args:
                hand: The hand name to look up (e.g., 'right-handed', 'left-handed', 'southpaw')
                
            Returns:
                JSON string with database hand value
            """
            return _get_hand_mapping(hand)
        
        return get_tennis_hand_mapping
    
    @staticmethod
    def create_tournament_mapping_tool():
        """Create the tennis tournament mapping tool."""
        @tool
        def get_tournament_mapping(tournament: str) -> str:
            """
            Map tennis fan colloquial names to database tournament names.
            Handles Grand Slams, Masters, and combined events with caching.
            
            Args:
                tournament: The tournament name to look up (e.g., 'french open', 'aus open', 'wimbledon')
                
            Returns:
                JSON string with database tournament names
            """
            return _get_tournament_mapping(tournament)
        
        return get_tournament_mapping
    
    @staticmethod
    def create_all_mapping_tools() -> List:
        """
        Create all tennis mapping tools.
        
        Returns:
            List of all mapping tools
        """
        return [
            TennisMappingTools.create_round_mapping_tool(),
            TennisMappingTools.create_surface_mapping_tool(),
            TennisMappingTools.create_tour_mapping_tool(),
            TennisMappingTools.create_hand_mapping_tool(),
            TennisMappingTools.create_tournament_mapping_tool()
        ]
    
    @staticmethod
    def create_all_tennis_tools() -> List:
        """
        Create all tennis tools including mapping and visualization tools.
        
        Returns:
            List of all tennis tools
        """
        mapping_tools = TennisMappingTools.create_all_mapping_tools()
        visualization_tools = TennisVisualizationTools.create_all_visualization_tools()
        return mapping_tools + visualization_tools
    
    @staticmethod
    def clear_cache():
        """Clear all mapping caches."""
        _get_round_mapping.cache_clear()
        _get_surface_mapping.cache_clear()
        _get_tour_mapping.cache_clear()
        _get_hand_mapping.cache_clear()
        _get_tournament_mapping.cache_clear()
    
    @staticmethod
    def get_cache_info():
        """Get cache statistics for all mapping functions."""
        return {
            "round_mapping": _get_round_mapping.cache_info(),
            "surface_mapping": _get_surface_mapping.cache_info(),
            "tour_mapping": _get_tour_mapping.cache_info(),
            "hand_mapping": _get_hand_mapping.cache_info(),
            "tournament_mapping": _get_tournament_mapping.cache_info()
        }

# =============================================================================
# TENNIS PROMPTS
# =============================================================================

class TennisPromptBuilder:
    """Unified tennis prompt builder with optimized system prompts."""
    
    @staticmethod
    def create_system_prompt(db_schema: str) -> str:
        """
        Create the optimized system prompt for the tennis AI agent.
        
        Args:
            db_schema: Database schema information
            
        Returns:
            Complete system prompt string
        """
        return f"""You are a high-performance tennis AI assistant designed to answer questions about tennis matches by querying a SQL database efficiently.

        PERFORMANCE OPTIMIZATION RULES:
        - ALWAYS use cached mapping tools to avoid duplicate calls
        - Use optimized database queries that include player names and context
        - Prefer specialized tools over generic SQL queries when available
        - Include relevant player information in all responses
        - Use efficient query patterns to minimize response time

        Here is the schema for the `matches` table you can query:
        {db_schema}
        
        CRITICAL: TOURNAMENT NAME MAPPING (CACHED)
        - Tennis fans use colloquial names that don't match database names
        - ALWAYS use get_tournament_mapping tool to convert fan names to database names
        - These mappings are now CACHED for better performance
        - Grand Slams: "French Open" → "Roland Garros", "Aus Open" → "Australian Open", "The Championship" → "Wimbledon"
        - Combined tournaments: "Rome" → ATP="Rome Masters" + WTA="Rome", "Madrid" → ATP="Madrid Masters" + WTA="Madrid"
        - CRITICAL: For combined tournaments (without ATP/WTA specification), ALWAYS search BOTH tournaments using UNION
        - Examples:
          * "Miami 2017" → Search both "Miami Masters" (ATP) AND "Miami" (WTA) using UNION
          * "Rome 2022" → Search both "Rome Masters" (ATP) AND "Rome" (WTA) using UNION
          * "Madrid 2021" → Search both "Madrid Masters" (ATP) AND "Madrid" (WTA) using UNION
        - NEVER search only one tournament when user doesn't specify ATP/WTA
        
        CRITICAL: TOURNAMENT WINNER QUERIES (OPTIMIZED)
        - When user asks "Who won X tournament" (without specifying round), ALWAYS assume they mean the FINAL
        - ALWAYS include round = 'F' filter for tournament winner queries
        - CRITICAL: When user specifies "ATP" or "WTA", ALWAYS filter by tour column
        - Use sql_db_query with optimized queries that include player names
        - Examples:
          * "Who won French Open 2022" → Use sql_db_query with optimized query for "Roland Garros" + round = 'F'
          * "Who won Rome 2022" → Use sql_db_query for both ATP/WTA tournaments
          * "Who won Wimbledon 2021" → Use sql_db_query with optimized query for "Wimbledon" + round = 'F'
          * "ATP Indian Wells 2017" → Use sql_db_query with tour = 'ATP' + tourney_name = 'Indian Wells' + event_year = 2017
          * "WTA Indian Wells 2017" → Use sql_db_query with tour = 'WTA' + tourney_name = 'Indian Wells' + event_year = 2017
        - For specific rounds: "Who won French Open Semi-Final 2022" → round = 'SF'
        - For generic tournament queries: "Who won Rome Final 2022" → round = 'F' for both ATP and WTA
        - ALWAYS check if user specifies ATP/WTA and filter accordingly
        
        CRITICAL: TENNIS ROUND TERMINOLOGY (CACHED)
        - Tennis fans use various round names that don't match database values
        - ALWAYS use get_tennis_round_mapping tool to convert fan round names to database values
        - These mappings are now CACHED for better performance
        - IMPORTANT: The database column is called 'round', NOT 'round_num'
        - When ordering by rounds, use ORDER BY round, not ORDER BY round_num
        - Common mappings:
          * "Final" → "F", "Semi-Final" → "SF", "Quarter-Final" → "QF"
          * "Round of 16" → "R16", "Round of 32" → "R32", "Round of 64" → "R64"
          * "First Round" → "R128", "Second Round" → "R64", "Third Round" → "R32"
          * "Last 16" → "R16", "Last 8" → "QF", "Last 4" → "SF"
          * "Qualifying" → "Q1", "Round Robin" → "RR"
        - Examples:
          * "Who won French Open Semi-Final 2022" → round = 'SF'
          * "Who reached Wimbledon Quarter-Finals 2021" → round = 'QF'
          * "Who won Rome Last 16 2022" → round = 'R16'
          * "Differentiate by rounds" → ORDER BY round (NOT round_num)
        
        CRITICAL: COMBINED TOURNAMENT QUERIES (ATP + WTA)
        - CRITICAL: When user asks for tournament without specifying ATP/WTA, ALWAYS search BOTH tours
        - Use UNION to combine ATP and WTA results from the same tournament
        - Examples:
          * "Miami 2017 all match results" → UNION of "Miami Masters" (ATP) + "Miami" (WTA)
          * "Rome 2022 results" → UNION of "Rome Masters" (ATP) + "Rome" (WTA)
          * "Madrid 2021 matches" → UNION of "Madrid Masters" (ATP) + "Madrid" (WTA)
        - SQL Pattern: SELECT ... FROM matches WHERE tourney_name = 'Tournament ATP' AND event_year = YYYY
                      UNION ALL
                      SELECT ... FROM matches WHERE tourney_name = 'Tournament WTA' AND event_year = YYYY
        - NEVER return only ATP or only WTA results when user doesn't specify tour
        
        CRITICAL: TOUR FILTERING (ATP vs WTA)
        - CRITICAL: When user specifies "ATP" or "WTA", ALWAYS filter by tour column
        - The database has a 'tour' column that distinguishes between ATP and WTA matches
        - Examples:
          * "ATP Indian Wells 2017" → Add tour = 'ATP' to WHERE clause
          * "WTA Indian Wells 2017" → Add tour = 'WTA' to WHERE clause
          * "ATP French Open 2022" → Add tour = 'ATP' to WHERE clause
          * "WTA French Open 2022" → Add tour = 'WTA' to WHERE clause
        - If user doesn't specify ATP/WTA, search both tours using UNION
        - ALWAYS check user query for ATP/WTA specification and filter accordingly
        
        CRITICAL: TENNIS SURFACE TERMINOLOGY (CACHED)
        - Tennis fans use various surface names that don't match database values
        - ALWAYS use get_tennis_surface_mapping tool to convert fan surface names to database values
        - These mappings are now CACHED for better performance
        - Use sql_db_query with optimized queries for surface-specific queries
        - Common mappings:
          * "Clay Court" → "Clay", "Red Clay" → "Clay", "Terre Battue" → "Clay"
          * "Hard Court" → "Hard", "Concrete" → "Hard", "Deco Turf" → "Hard"
          * "Grass Court" → "Grass", "Lawn" → "Grass", "Natural Grass" → "Grass"
          * "Carpet Court" → "Carpet", "Synthetic" → "Carpet", "Artificial" → "Carpet"
        - Examples:
          * "Who won on clay courts in 2022" → Use sql_db_query with optimized query for surface = 'Clay'
          * "Best players on grass" → Use sql_db_query with optimized query for surface = 'Grass'
          * "Hard court specialists" → Use sql_db_query with optimized query for surface = 'Hard'
        
        CRITICAL: HEAD-TO-HEAD QUERIES (OPTIMIZED)
        - For head-to-head questions (e.g., "Player A vs Player B h2h"), use sql_db_query with optimized queries
        - Use optimized queries that include player names and match details
        - ALWAYS include the surface column in your head-to-head queries
        - Include match details like year, tournament, surface, score, and winner
        - Format the response to show both the overall record and individual match details
        - Count ONLY completed matches (exclude W/O, DEF, RET matches from head-to-head records)
        - Double-check your counting: count wins for each player separately
        - Verify your count matches the number of matches displayed in the table
        - If you find W/O, DEF, or RET in the score, exclude that match from the head-to-head record
        - Always state the correct win-loss record in your summary
        - Example: "Player A leads Player B 15-3" (not counting walkovers)
        
        ENHANCED RESPONSE QUALITY:
        - ALWAYS include player names in responses
        - Provide context about tournaments, surfaces, and years
        - Format scores clearly and consistently
        - Include relevant statistics and rankings when available
        - Explain what the data represents (e.g., "men's final", "women's semifinal")
        
        CRITICAL: RESPONSE FORMATTING FOR TOURNAMENT RESULTS
        - When showing tournament results, ALWAYS format as: "Player A defeated Player B 6-4, 6-4"
        - For multiple matches (men's/women's), clearly separate them
        - Example: "The 2008 Wimbledon finals featured:
          - Men's Final: Rafael Nadal defeated Roger Federer 6-4, 6-4, 6-7(5), 6-7(8), 9-7
          - Women's Final: Venus Williams defeated Serena Williams 7-5, 6-4"
        - NEVER just list scores without player names
        
        CRITICAL: ALWAYS INCLUDE PLAYER NAMES IN QUERIES
        - NEVER use queries that only return scores without player names
        - ALWAYS include winner_name and loser_name in SELECT statements
        - Example: SELECT winner_name, loser_name, set1, set2, set3, set4, set5 FROM matches...
        - This ensures responses include who actually played and won
        
        CRITICAL: SQL SYNTAX FOR UNION QUERIES
        - When using UNION ALL, ORDER BY clause must come AFTER the entire UNION statement
        - CORRECT: SELECT ... FROM table1 UNION ALL SELECT ... FROM table2 ORDER BY column
        - WRONG: SELECT ... FROM table1 ORDER BY column UNION ALL SELECT ... FROM table2 ORDER BY column
        - Always place ORDER BY at the very end of the complete UNION query
        
        CRITICAL: PLAYER NAME VARIATIONS
        - Player names in database may be different from common usage
        - Examples: "Carlos Alcaraz" (not "Carlos Alcaraz Garfia"), "Roger Federer" (not "Roger Federer Jr.")
        - If no results found, try simpler player names without middle names or suffixes
        - Use LIKE operator for partial name matching: WHERE winner_name LIKE '%Alcaraz%'
        - Always check both winner_name and loser_name for player queries
        
        OPTIMIZED QUERY PATTERNS:
        - Use specialized tools when available instead of generic SQL
        - Include player names in all queries
        - Add proper filtering to avoid over-fetching data
        - Use efficient query patterns for better performance
        - Include relevant context in responses
        
        ENHANCED DATABASE FEATURES:
        - The database now includes a `players` table with player metadata (handedness, nationality, height, birth date, etc.)
        - The database includes a `rankings` table with historical ranking data (1973-2024, 5.3M+ records)
        - The database includes COMPLETE TOURNAMENT COVERAGE (1877-2024, 1.7M+ matches)
        - The database includes a `doubles_matches` table with doubles match data (2000-2020, 26K+ matches)
        - Use `matches_with_full_info` view for queries that need player details
        - Use `matches_with_rankings` view for queries that need ranking context
        - Use `player_rankings_history` view for ranking analysis
        - Available player fields: winner_hand, winner_ioc, winner_height, winner_dob, loser_hand, loser_ioc, loser_height, loser_dob
        - Available ranking fields: winner_rank_at_time, winner_points_at_time, loser_rank_at_time, loser_points_at_time
        - Era classification: Amateur (1877-1967), Professional (1968-2024)
        - Tournament types: Main_Tour, ATP_Qual_Chall, ATP_Futures, WTA_Qual_ITF
        - Match types: Singles (matches table), Doubles (doubles_matches table)
        - Historical coverage: 147 years of complete tennis history (1877-2024)
        
        CRITICAL: VISUALIZATION TOOLS (NEW FEATURE)
        - When users ask for visualizations, charts, or graphical representations, you MUST follow this exact workflow:
          1. FIRST: Use sql_db_query to get the data from the database
          2. SECOND: Format the data as JSON with the required column names
          3. THIRD: Call the appropriate visualization tool with the JSON data
        - NEVER call visualization tools with empty data '[]' - ALWAYS query the database first
        - Available visualization tools:
          * create_head_to_head_chart: For comparing two players (e.g., "Show me Nadal vs Federer head-to-head")
          * create_surface_performance_chart: For showing player performance by surface (e.g., "Show me Djokovic's performance by surface")
          * create_ranking_history_chart: For showing ranking trends over time (e.g., "Show me Serena's ranking history")
          * create_tournament_performance_chart: For showing wins by tournament (e.g., "Show me Federer's tournament wins")
          * create_season_performance_chart: For showing performance by year (e.g., "Show me Nadal's wins by year")
        - REQUIRED WORKFLOW FOR VISUALIZATIONS:
          * Step 1: Query database with sql_db_query to get match data
          * Step 2: Convert results to JSON format with required columns
          * Step 3: Call visualization tool with the JSON data
        - The visualization tools expect JSON data with specific column names
        - For head-to-head: winner_name, loser_name, surface, year, tournament
        - For surface performance: winner_name, loser_name, surface, year
        - For ranking history: ranking_date, rank, player
        - For tournament performance: winner_name, loser_name, tourney_name, year
        - For season performance: winner_name, loser_name, year
        - When users ask questions like "Show me", "Visualize", "Chart", "Graph", "Plot" - ALWAYS query database first, then use visualization tools
        
        PERFORMANCE OPTIMIZATION WORKFLOW:
        1. Use cached mapping tools for terminology conversion
        2. Use specialized tools when available (get_tournament_final_results, get_surface_performance_results, get_head_to_head_results)
        3. For visualization requests, query database first, then use appropriate visualization tool
        4. For complex queries, use sql_db_query_enhanced with optimized patterns
        5. Always include player names and context in responses
        6. Format results clearly and consistently
        
        REMEMBER: 
        - Use cached tools for better performance
        - Include player names in all responses
        - Use specialized tools when available
        - Use visualization tools for graphical representations
        - Provide context and clear formatting
        - Optimize for speed and accuracy
        """
    
    @staticmethod
    def create_optimized_prompt_template(system_prompt: str):
        """
        Create an optimized prompt template.
        
        Args:
            system_prompt: System prompt string
            
        Returns:
            Optimized ChatPromptTemplate
        """
        from langchain_core.prompts import ChatPromptTemplate
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{messages}")
        ])

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def standardize_tourney_level(level, tour=None, era=None):
    """
    Replace old tourney levels with new standardized levels.
    
    Args:
        level: The original tourney_level value
        tour: The tour (ATP or WTA) for context
        era: The era for historical context (optional)
    
    Returns:
        Standardized tourney_level value
    """
    if pd.isna(level) or level == '':
        return level
    
    level_str = str(level).strip()
    
    # Special case: WTA D level → BJK_Cup
    if level_str == 'D' and tour == 'WTA':
        return 'BJK_Cup'
    
    # Direct mapping
    if level_str in TOURNEY_LEVEL_MAPPINGS:
        return TOURNEY_LEVEL_MAPPINGS[level_str]
    
    # Handle unknown levels
    print(f"Warning: Unknown tourney_level '{level_str}' for tour '{tour}'")
    return level_str  # Keep as-is if unknown

# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================

class PerformanceMonitor:
    """Lightweight performance monitoring for tennis tools."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics = {
            "tool_calls": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "total_queries": 0
        }
    
    def track_tool_call(self, tool_name: str, execution_time: float):
        """Track tool call performance."""
        if tool_name not in self.metrics["tool_calls"]:
            self.metrics["tool_calls"][tool_name] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0
            }
        
        self.metrics["tool_calls"][tool_name]["count"] += 1
        self.metrics["tool_calls"][tool_name]["total_time"] += execution_time
        self.metrics["tool_calls"][tool_name]["avg_time"] = (
            self.metrics["tool_calls"][tool_name]["total_time"] / 
            self.metrics["tool_calls"][tool_name]["count"]
        )
    
    def get_performance_summary(self):
        """Get performance summary."""
        return {
            "total_tool_calls": sum(tool["count"] for tool in self.metrics["tool_calls"].values()),
            "cache_hit_rate": self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0,
            "tool_performance": self.metrics["tool_calls"]
        }

# =============================================================================
# MAIN EXPORTS
# =============================================================================

# Export main classes and functions
__all__ = [
    'TennisMappingTools',
    'TennisPromptBuilder', 
    'PerformanceMonitor',
    'standardize_tourney_level',
    'ROUND_MAPPINGS',
    'SURFACE_MAPPINGS', 
    'TOUR_MAPPINGS',
    'HAND_MAPPINGS',
    'GRAND_SLAM_MAPPINGS',
    'TOURNEY_LEVEL_MAPPINGS',
    'COMBINED_TOURNAMENT_MAPPINGS'
]
