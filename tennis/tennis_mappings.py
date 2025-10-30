"""
Tennis Mapping Tools
Contains cached mapping functions and LangChain tools for tennis terminology mapping.
"""

from langchain_core.tools import tool
from typing import List
from functools import lru_cache
import json
from .ranking_analysis import (
    get_ranking_context
)
from .tennis_mapping_dicts import (
    ROUND_MAPPINGS,
    SURFACE_MAPPINGS,
    TOUR_MAPPINGS,
    HAND_MAPPINGS,
    GRAND_SLAM_MAPPINGS,
    TOURNEY_LEVEL_MAPPINGS,
    COMBINED_TOURNAMENT_MAPPINGS
)

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
    def create_ranking_analysis_tool():
        """Create the tennis ranking analysis tool."""
        @tool
        def analyze_ranking_question(question: str, year: int = None) -> str:
            """
            Analyze ranking questions and determine appropriate data source and SQL approach.
            
            Args:
                question: The ranking question to analyze
                year: Optional year for temporal context
                
            Returns:
                JSON string with ranking analysis and recommended approach
            """
            return get_ranking_context(question, year)
        
        return analyze_ranking_question
    
    @staticmethod
    def create_ranking_sql_tool():
        """Create the ranking SQL approach tool."""
        @tool
        def get_ranking_sql_approach(question_type: str, tour: str = "ATP", year: int = None) -> str:
            """
            Get SQL approach for ranking questions.
            
            Args:
                question_type: Type of ranking question (official_rankings, match_time_rankings, etc.)
                tour: Tour type (ATP or WTA)
                year: Optional year for temporal context
                
            Returns:
                JSON string with SQL approach and recommendations
            """
            return get_ranking_sql_approach(question_type, tour, year)
        
        return get_ranking_sql_approach
    
    @staticmethod
    def create_ranking_parameters_tool():
        """Create the ranking parameters extraction tool."""
        @tool
        def extract_ranking_parameters(question: str) -> str:
            """
            Extract key parameters from ranking questions (year, rank limit, players, tour).
            
            Args:
                question: The ranking question to analyze
                
            Returns:
                JSON string with extracted parameters
            """
            return json.dumps(extract_ranking_parameters(question))
        
        return extract_ranking_parameters
    
    @staticmethod
    def create_grand_slam_mapping_tool():
        """Create the Grand Slam mapping tool."""
        @tool
        def get_grand_slam_tournament_names() -> str:
            """
            Get all Grand Slam tournament names as they appear in the database.
            Use this for Grand Slam analysis questions.
            
            Returns:
                JSON string with all Grand Slam tournament names
            """
            return json.dumps({
                "grand_slams": [
                    "Australian Open",
                    "Roland Garros", 
                    "Wimbledon",
                    "US Open"
                ],
                "sql_pattern": "WHERE tourney_name COLLATE NOCASE IN ('Australian Open', 'Roland Garros', 'Wimbledon', 'US Open')",
                "usage": "For Grand Slam questions, use COLLATE NOCASE to handle case variations in SQL queries"
            })
        
        return get_grand_slam_tournament_names
    
    @staticmethod
    def create_all_mapping_tools() -> List:
        """
        Create all tennis mapping tools using the correct, decorated methods.
        
        Returns:
            List of all mapping tools compatible with LangChain.
        """
        return [
            TennisMappingTools.create_round_mapping_tool(),
            TennisMappingTools.create_surface_mapping_tool(),
            TennisMappingTools.create_tour_mapping_tool(),
            TennisMappingTools.create_hand_mapping_tool(),
            TennisMappingTools.create_tournament_mapping_tool(),
            TennisMappingTools.create_grand_slam_mapping_tool(),
            TennisMappingTools.create_ranking_analysis_tool(),
            TennisMappingTools.create_ranking_sql_tool(),
            TennisMappingTools.create_ranking_parameters_tool()
        ]

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'TennisMappingTools',
    'ROUND_MAPPINGS',
    'SURFACE_MAPPINGS', 
    'TOUR_MAPPINGS',
    'HAND_MAPPINGS',
    'GRAND_SLAM_MAPPINGS',
    'TOURNEY_LEVEL_MAPPINGS',
    'COMBINED_TOURNAMENT_MAPPINGS'
]
