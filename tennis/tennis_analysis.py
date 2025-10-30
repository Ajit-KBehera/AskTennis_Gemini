"""
Tennis Question Analysis Module

This module provides question analysis functions for understanding tennis query context.
Functions analyze natural language questions to extract relevant tennis information.
"""

from functools import lru_cache


@lru_cache(maxsize=128)
def determine_tour_context(question: str) -> str:
    """
    Determine if question is about men's (ATP) or women's (WTA) tennis.
    Uses TOUR_MAPPINGS as the single source of truth for tour detection.
    
    Args:
        question: The question to analyze
        
    Returns:
        Tour string ("ATP", "WTA", or "BOTH" for ambiguous questions)
    """
    # Lazy import to avoid circular dependency
    from .tennis_mappings import TOUR_MAPPINGS
    
    question_lower = question.lower()
    
    # Extract ATP and WTA keywords from TOUR_MAPPINGS (single source of truth)
    atp_keywords = [kw for kw, value in TOUR_MAPPINGS.items() if value == "ATP"]
    wta_keywords = [kw for kw, value in TOUR_MAPPINGS.items() if value == "WTA"]
    
    # Check for explicit tour mentions using TOUR_MAPPINGS keywords
    if any(keyword in question_lower for keyword in atp_keywords):
        return "ATP"
    elif any(keyword in question_lower for keyword in wta_keywords):
        return "WTA"
    
    # Check for player names that might indicate tour
    # (This could be expanded with known player lists)
    
    # Default to BOTH for ambiguous questions (more neutral default)
    return "BOTH"


__all__ = ['determine_tour_context']

