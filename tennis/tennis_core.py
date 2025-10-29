"""
Tennis Core Module - Orchestrator
Main entry point that imports and exposes all tennis functionality.
This module serves as a clean interface to all tennis-related components.
"""

# Import all functionality from compartmentalized modules
from .tennis_mappings import (
    TennisMappingTools,
    standardize_tourney_level,
    ROUND_MAPPINGS,
    SURFACE_MAPPINGS, 
    TOUR_MAPPINGS,
    HAND_MAPPINGS,
    GRAND_SLAM_MAPPINGS,
    TOURNEY_LEVEL_MAPPINGS,
    COMBINED_TOURNAMENT_MAPPINGS
)

from .tennis_prompts import TennisPromptBuilder

# =============================================================================
# MAIN EXPORTS
# =============================================================================

# Export main classes and functions
__all__ = [
    'TennisMappingTools',
    'TennisPromptBuilder', 
    'standardize_tourney_level',
    'ROUND_MAPPINGS',
    'SURFACE_MAPPINGS', 
    'TOUR_MAPPINGS',
    'HAND_MAPPINGS',
    'GRAND_SLAM_MAPPINGS',
    'TOURNEY_LEVEL_MAPPINGS',
    'COMBINED_TOURNAMENT_MAPPINGS'
]
