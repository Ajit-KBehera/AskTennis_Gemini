"""
Cached tennis terminology mapping tools for natural language processing.
Optimized version with caching to prevent duplicate tool calls.
"""

from langchain_core.tools import tool
from typing import Dict, Any, List
from functools import lru_cache
import json

# Import the original mappings
from .tennis_mappings import (
    ROUND_MAPPINGS, SURFACE_MAPPINGS, TOUR_MAPPINGS, 
    HAND_MAPPINGS, GRAND_SLAM_MAPPINGS, COMBINED_TOURNAMENT_MAPPINGS
)


class CachedTennisMappingFactory:
    """
    Factory class for creating cached tennis mapping tools.
    Implements caching to prevent duplicate tool calls and improve performance.
    """
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _get_round_mapping(round_name: str) -> str:
        """Cached round mapping function."""
        round_lower = round_name.lower().strip()
        
        if round_lower in ROUND_MAPPINGS:
            return json.dumps({"database_round": ROUND_MAPPINGS[round_lower], "type": "tennis_round"})
        
        return json.dumps({"database_round": round_name, "type": "unknown"})
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _get_surface_mapping(surface: str) -> str:
        """Cached surface mapping function."""
        surface_lower = surface.lower().strip()
        
        if surface_lower in SURFACE_MAPPINGS:
            return json.dumps({"database_surface": SURFACE_MAPPINGS[surface_lower], "type": "tennis_surface"})
        
        return json.dumps({"database_surface": surface, "type": "unknown"})
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _get_tour_mapping(tour: str) -> str:
        """Cached tour mapping function."""
        tour_lower = tour.lower().strip()
        
        if tour_lower in TOUR_MAPPINGS:
            return json.dumps({"database_tour": TOUR_MAPPINGS[tour_lower], "type": "tennis_tour"})
        
        return json.dumps({"database_tour": tour, "type": "unknown"})
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _get_hand_mapping(hand: str) -> str:
        """Cached hand mapping function."""
        hand_lower = hand.lower().strip()
        
        if hand_lower in HAND_MAPPINGS:
            return json.dumps({"database_hand": HAND_MAPPINGS[hand_lower], "type": "tennis_hand"})
        
        return json.dumps({"database_hand": hand, "type": "unknown"})
    
    @staticmethod
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
    
    @staticmethod
    def create_round_mapping_tool():
        """Create the cached tennis round mapping tool."""
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
            return CachedTennisMappingFactory._get_round_mapping(round_name)
        
        return get_tennis_round_mapping
    
    @staticmethod
    def create_surface_mapping_tool():
        """Create the cached tennis surface mapping tool."""
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
            return CachedTennisMappingFactory._get_surface_mapping(surface)
        
        return get_tennis_surface_mapping
    
    @staticmethod
    def create_tour_mapping_tool():
        """Create the cached tennis tour mapping tool."""
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
            return CachedTennisMappingFactory._get_tour_mapping(tour)
        
        return get_tennis_tour_mapping
    
    @staticmethod
    def create_hand_mapping_tool():
        """Create the cached tennis hand mapping tool."""
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
            return CachedTennisMappingFactory._get_hand_mapping(hand)
        
        return get_tennis_hand_mapping
    
    @staticmethod
    def create_tournament_mapping_tool():
        """Create the cached tennis tournament mapping tool."""
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
            return CachedTennisMappingFactory._get_tournament_mapping(tournament)
        
        return get_tournament_mapping
    
    @staticmethod
    def create_all_mapping_tools() -> List:
        """
        Create all cached tennis mapping tools.
        
        Returns:
            List of all cached mapping tools
        """
        return [
            CachedTennisMappingFactory.create_round_mapping_tool(),
            CachedTennisMappingFactory.create_surface_mapping_tool(),
            CachedTennisMappingFactory.create_tour_mapping_tool(),
            CachedTennisMappingFactory.create_hand_mapping_tool(),
            CachedTennisMappingFactory.create_tournament_mapping_tool()
        ]
    
    @staticmethod
    def clear_cache():
        """Clear all mapping caches."""
        CachedTennisMappingFactory._get_round_mapping.cache_clear()
        CachedTennisMappingFactory._get_surface_mapping.cache_clear()
        CachedTennisMappingFactory._get_tour_mapping.cache_clear()
        CachedTennisMappingFactory._get_hand_mapping.cache_clear()
        CachedTennisMappingFactory._get_tournament_mapping.cache_clear()
    
    @staticmethod
    def get_cache_info():
        """Get cache statistics for all mapping functions."""
        return {
            "round_mapping": CachedTennisMappingFactory._get_round_mapping.cache_info(),
            "surface_mapping": CachedTennisMappingFactory._get_surface_mapping.cache_info(),
            "tour_mapping": CachedTennisMappingFactory._get_tour_mapping.cache_info(),
            "hand_mapping": CachedTennisMappingFactory._get_hand_mapping.cache_info(),
            "tournament_mapping": CachedTennisMappingFactory._get_tournament_mapping.cache_info()
        }
