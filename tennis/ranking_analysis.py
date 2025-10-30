"""
Tennis Ranking Analysis Module

This module provides intelligent ranking question analysis and data source determination
for tennis-related queries involving player rankings.
"""

import json
import re
from enum import Enum
from functools import lru_cache
from typing import Dict, List, Optional, Any


class RankingQuestionType(Enum):
    """Types of ranking questions."""
    OFFICIAL_RANKINGS = "official_rankings"      # Year-end, weekly rankings
    MATCH_TIME_RANKINGS = "match_time_rankings"   # Winner/loser rank at match time
    CAREER_HIGH_RANKINGS = "career_high"         # Best ranking achieved
    RANKING_PROGRESSION = "ranking_progression"  # Ranking changes over time
    RANKING_COMPARISON = "ranking_comparison"    # Compare rankings between players


# Ranking question patterns for classification
RANKING_PATTERNS = {
    # Official Rankings Patterns
    "top.*in.*year": RankingQuestionType.OFFICIAL_RANKINGS,
    "ranked.*in.*": RankingQuestionType.OFFICIAL_RANKINGS,
    "year.*end.*rank": RankingQuestionType.OFFICIAL_RANKINGS,
    "weekly.*rank": RankingQuestionType.OFFICIAL_RANKINGS,
    "top.*players.*in": RankingQuestionType.OFFICIAL_RANKINGS,
    "who.*were.*top": RankingQuestionType.OFFICIAL_RANKINGS,
    "rankings.*in": RankingQuestionType.OFFICIAL_RANKINGS,
    
    # Match-time Rankings Patterns  
    "rank.*when.*beat": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*during.*match": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*at.*time.*match": RankingQuestionType.MATCH_TIME_RANKINGS,
    "winner.*rank": RankingQuestionType.MATCH_TIME_RANKINGS,
    "loser.*rank": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*when.*won": RankingQuestionType.MATCH_TIME_RANKINGS,
    "rank.*when.*lost": RankingQuestionType.MATCH_TIME_RANKINGS,
    
    # Career High Patterns
    "highest.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "best.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "peak.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "career.*high": RankingQuestionType.CAREER_HIGH_RANKINGS,
    "maximum.*rank": RankingQuestionType.CAREER_HIGH_RANKINGS,
    
    # Progression Patterns
    "rank.*improvement": RankingQuestionType.RANKING_PROGRESSION,
    "rank.*decline": RankingQuestionType.RANKING_PROGRESSION,
    "rank.*change": RankingQuestionType.RANKING_PROGRESSION,
    "ranking.*evolution": RankingQuestionType.RANKING_PROGRESSION,
    "rank.*progress": RankingQuestionType.RANKING_PROGRESSION,
    
    # Comparison Patterns
    "compare.*rank": RankingQuestionType.RANKING_COMPARISON,
    "rank.*vs": RankingQuestionType.RANKING_COMPARISON,
    "rank.*between": RankingQuestionType.RANKING_COMPARISON,
}


# Data source mapping for different ranking question types
RANKING_DATA_SOURCES = {
    RankingQuestionType.OFFICIAL_RANKINGS: {
        "primary_table": "player_rankings_history",
        "backup_table": "rankings", 
        "key_fields": ["ranking_date", "rank", "player", "tour"],
        "join_required": True,
        "tour_separation": True,
        "description": "Official ATP/WTA rankings"
    },
    RankingQuestionType.MATCH_TIME_RANKINGS: {
        "primary_table": "matches",
        "backup_table": "matches_with_rankings",
        "key_fields": ["winner_rank", "loser_rank", "event_year", "tourney_name"],
        "join_required": False,
        "tour_separation": False,
        "description": "Match-specific rankings at time of match"
    },
    RankingQuestionType.CAREER_HIGH_RANKINGS: {
        "primary_table": "player_rankings_history",
        "backup_table": "rankings",
        "key_fields": ["rank", "player", "tour"],
        "join_required": True,
        "tour_separation": True,
        "description": "Career high rankings"
    },
    RankingQuestionType.RANKING_PROGRESSION: {
        "primary_table": "player_rankings_history",
        "backup_table": "rankings",
        "key_fields": ["ranking_date", "rank", "player", "tour"],
        "join_required": True,
        "tour_separation": True,
        "description": "Ranking progression over time"
    },
    RankingQuestionType.RANKING_COMPARISON: {
        "primary_table": "player_rankings_history",
        "backup_table": "rankings",
        "key_fields": ["ranking_date", "rank", "player", "tour"],
        "join_required": True,
        "tour_separation": True,
        "description": "Ranking comparisons between players"
    }
}


# SQL templates for different ranking question types
RANKING_SQL_TEMPLATES = {
    RankingQuestionType.OFFICIAL_RANKINGS: {
        "top_players_year": """
            SELECT name_first || ' ' || name_last as player_name, rank
            FROM player_rankings_history 
            WHERE ranking_date = '{year}-12-30 00:00:00' 
              AND rank <= {limit} 
              AND tour = '{tour}' 
            ORDER BY rank
        """,
        "top_players_week": """
            SELECT name_first || ' ' || name_last as player_name, rank
            FROM player_rankings_history 
            WHERE ranking_date = '{date}' 
              AND rank <= {limit} 
              AND tour = '{tour}' 
            ORDER BY rank
        """,
        "specific_rank": """
            SELECT name_first || ' ' || name_last as player_name, rank
            FROM player_rankings_history 
            WHERE ranking_date = '{date}' 
              AND rank = {rank} 
              AND tour = '{tour}'
        """
    },
    RankingQuestionType.MATCH_TIME_RANKINGS: {
        "winner_rank_at_match": """
            SELECT winner_name, winner_rank, event_year, tourney_name
            FROM matches 
            WHERE winner_name = '{player}' 
              AND event_year = {year}
              AND winner_rank IS NOT NULL
            ORDER BY event_year, tourney_name
        """,
        "loser_rank_at_match": """
            SELECT loser_name, loser_rank, event_year, tourney_name
            FROM matches 
            WHERE loser_name = '{player}' 
              AND event_year = {year}
              AND loser_rank IS NOT NULL
            ORDER BY event_year, tourney_name
        """,
        "rank_during_match": """
            SELECT winner_name, loser_name, winner_rank, loser_rank, event_year, tourney_name
            FROM matches 
            WHERE (winner_name = '{player1}' AND loser_name = '{player2}')
               OR (winner_name = '{player2}' AND loser_name = '{player1}')
              AND event_year = {year}
              AND (winner_rank IS NOT NULL OR loser_rank IS NOT NULL)
        """
    },
    RankingQuestionType.CAREER_HIGH_RANKINGS: {
        "career_high_rank": """
            SELECT name_first || ' ' || name_last as player_name, MIN(rank) as career_high_rank
            FROM player_rankings_history 
            WHERE name_first || ' ' || name_last = '{player}'
              AND tour = '{tour}'
            GROUP BY name_first, name_last
        """,
        "multiple_players_career_high": """
            SELECT name_first || ' ' || name_last as player_name, MIN(rank) as career_high_rank
            FROM player_rankings_history 
            WHERE name_first || ' ' || name_last IN ({players})
              AND tour = '{tour}'
            GROUP BY name_first, name_last
            ORDER BY career_high_rank
        """
    }
}


@lru_cache(maxsize=256)
def classify_ranking_question(question: str) -> RankingQuestionType:
    """
    Classify a ranking question into its appropriate type.
    
    Args:
        question: The ranking question to classify
        
    Returns:
        RankingQuestionType enum value
    """
    question_lower = question.lower()
    
    # Check patterns in order of specificity
    for pattern, question_type in RANKING_PATTERNS.items():
        if re.search(pattern, question_lower):
            return question_type
    
    # Default to official rankings if no pattern matches
    return RankingQuestionType.OFFICIAL_RANKINGS


@lru_cache(maxsize=256)
def get_ranking_context(question: str, year: Optional[int] = None, tour: Optional[str] = None) -> str:
    """
    Get comprehensive ranking context for a question.
    
    Args:
        question: The ranking question
        year: Optional year for temporal context
        tour: Optional tour specification
        
    Returns:
        JSON string with ranking analysis and recommendations
    """
    # Classify question type
    question_type = classify_ranking_question(question)
    
    # Tour detection is handled by LLM via prompt instructions
    # If tour is not provided, LLM will determine it from the question context
    # or use UNION queries for ambiguous cases
    
    # Get appropriate data source
    data_source = RANKING_DATA_SOURCES.get(question_type)
    
    # Get SQL templates
    sql_templates = RANKING_SQL_TEMPLATES.get(question_type, {})
    
    return json.dumps({
        "question_type": question_type.value,
        "data_source": data_source,
        "tour": tour,
        "year": year,
        "sql_templates": sql_templates,
        "recommendations": {
            "use_table": data_source["primary_table"],
            "tour_separation": data_source["tour_separation"],
            "join_required": data_source["join_required"]
        }
    })


@lru_cache(maxsize=128)
def get_ranking_sql_approach(question_type: str, tour: str = "ATP", year: Optional[int] = None) -> str:
    """
    Get SQL approach for ranking questions.
    
    Args:
        question_type: Type of ranking question
        tour: Tour type (ATP or WTA)
        year: Optional year for temporal context
        
    Returns:
        JSON string with SQL approach
    """
    question_type_enum = RankingQuestionType(question_type)
    data_source = RANKING_DATA_SOURCES.get(question_type_enum)
    sql_templates = RANKING_SQL_TEMPLATES.get(question_type_enum, {})
    
    return json.dumps({
        "data_source": data_source,
        "sql_templates": sql_templates,
        "tour": tour,
        "year": year,
        "key_considerations": {
            "tour_separation": data_source["tour_separation"],
            "join_required": data_source["join_required"],
            "primary_table": data_source["primary_table"]
        }
    })


def extract_ranking_parameters(question: str) -> Dict[str, Any]:
    """
    Extract key parameters from ranking questions.
    
    Args:
        question: The ranking question
        
    Returns:
        Dictionary with extracted parameters
    """
    parameters = {
        "year": None,
        "rank_limit": None,
        "players": [],
        "tour": None
    }
    
    # Extract year
    year_match = re.search(r'\b(19|20)\d{2}\b', question)
    if year_match:
        parameters["year"] = int(year_match.group())
    
    # Extract rank limit (top 10, top 5, etc.)
    rank_match = re.search(r'top\s+(\d+)', question.lower())
    if rank_match:
        parameters["rank_limit"] = int(rank_match.group(1))
    
    # Extract specific rank
    specific_rank_match = re.search(r'rank(?:ed)?\s+(\d+)', question.lower())
    if specific_rank_match:
        parameters["rank_limit"] = int(specific_rank_match.group(1))
    
    # Extract player names (basic pattern)
    # This could be enhanced with more sophisticated NLP
    player_patterns = [
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last
        r'([A-Z][a-z]+)',  # Single name
    ]
    
    for pattern in player_patterns:
        matches = re.findall(pattern, question)
        parameters["players"].extend(matches)
    
    return parameters


# Export key functions
__all__ = [
    'RankingQuestionType',
    'classify_ranking_question',
    'get_ranking_context',
    'get_ranking_sql_approach',
    'extract_ranking_parameters',
    'RANKING_DATA_SOURCES',
    'RANKING_SQL_TEMPLATES'
]
