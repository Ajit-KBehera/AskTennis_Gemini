"""
Generic mapping utilities for AskTennis AI application.
Consolidates all mapping functions into a single, configurable system.
"""

from functools import lru_cache
from typing import Dict, Any
import json


class GenericMappingTool:
    """
    Generic mapping tool that handles all tennis terminology mappings.
    Replaces individual mapping functions with a single, configurable system.
    """
    
    def __init__(self, mappings: Dict[str, str], mapping_type: str):
        """
        Initialize the generic mapping tool.
        
        Args:
            mappings: Dictionary of mappings
            mapping_type: Type of mapping (e.g., 'tennis_round', 'tennis_surface')
        """
        self.mappings = mappings
        self.mapping_type = mapping_type
    
    @lru_cache(maxsize=128)
    def get_mapping(self, input_value: str) -> str:
        """
        Get mapping for input value with caching.
        
        Args:
            input_value: The value to map
            
        Returns:
            JSON string with mapping result
        """
        input_lower = input_value.lower().strip()
        
        if input_lower in self.mappings:
            return json.dumps({
                f"database_{self.mapping_type.split('_')[1]}": self.mappings[input_lower],
                "type": self.mapping_type
            })
        
        return json.dumps({
            f"database_{self.mapping_type.split('_')[1]}": input_value,
            "type": "unknown"
        })
    
    def clear_cache(self):
        """Clear the mapping cache."""
        self.get_mapping.cache_clear()
    
    def get_cache_info(self):
        """Get cache statistics."""
        return self.get_mapping.cache_info()


# Pre-configured mapping tools
def create_round_mapping_tool():
    """Create round mapping tool with pre-configured mappings."""
    from tennis.tennis_core import ROUND_MAPPINGS
    return GenericMappingTool(ROUND_MAPPINGS, "tennis_round")


def create_surface_mapping_tool():
    """Create surface mapping tool with pre-configured mappings."""
    from tennis.tennis_core import SURFACE_MAPPINGS
    return GenericMappingTool(SURFACE_MAPPINGS, "tennis_surface")


def create_tour_mapping_tool():
    """Create tour mapping tool with pre-configured mappings."""
    from tennis.tennis_core import TOUR_MAPPINGS
    return GenericMappingTool(TOUR_MAPPINGS, "tennis_tour")


def create_hand_mapping_tool():
    """Create hand mapping tool with pre-configured mappings."""
    from tennis.tennis_core import HAND_MAPPINGS
    return GenericMappingTool(HAND_MAPPINGS, "tennis_hand")


def create_tournament_mapping_tool():
    """Create tournament mapping tool with pre-configured mappings."""
    from tennis.tennis_core import GRAND_SLAM_MAPPINGS, COMBINED_TOURNAMENT_MAPPINGS
    
    # Combine mappings
    combined_mappings = {**GRAND_SLAM_MAPPINGS, **COMBINED_TOURNAMENT_MAPPINGS}
    return GenericMappingTool(combined_mappings, "tennis_tournament")
