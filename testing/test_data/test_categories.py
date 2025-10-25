"""
Test categorization and validation rules for automated testing.
Defines different types of tennis questions and their validation methods.
"""

from enum import Enum
from typing import Dict, Any, Callable


class TestCategory(Enum):
    """Enumeration of test categories for tennis questions."""
    TOURNAMENT_WINNER = "tournament_winner"
    HEAD_TO_HEAD = "head_to_head"
    SURFACE_PERFORMANCE = "surface_performance"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    HISTORICAL_RECORDS = "historical_records"
    PLAYER_RANKINGS = "player_rankings"
    MATCH_DETAILS = "match_details"
    COMPLEX_QUERIES = "complex_queries"


class ValidationMethod(Enum):
    """Enumeration of validation methods for different question types."""
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    NUMERICAL_ACCURACY = "numerical_accuracy"
    PARTIAL_MATCH = "partial_match"
    RANGE_ACCURACY = "range_accuracy"
    PERCENTAGE_ACCURACY = "percentage_accuracy"


# Test category definitions with validation rules
TEST_CATEGORIES = {
    TestCategory.TOURNAMENT_WINNER: {
        "description": "Questions about tournament winners and champions",
        "validation_method": ValidationMethod.EXACT_MATCH,
        "weight": 1.0,
        "examples": [
            "Who won Wimbledon in 2022?",
            "Who won the French Open in 2021?",
            "Who won the US Open in 2020?"
        ]
    },
    
    TestCategory.HEAD_TO_HEAD: {
        "description": "Head-to-head records between players",
        "validation_method": ValidationMethod.NUMERICAL_ACCURACY,
        "weight": 0.8,
        "examples": [
            "What is the head-to-head record between Federer and Nadal?",
            "How many times has Djokovic beaten Murray?",
            "What is Serena Williams' record against Venus Williams?"
        ]
    },
    
    TestCategory.SURFACE_PERFORMANCE: {
        "description": "Player performance on different surfaces",
        "validation_method": ValidationMethod.PERCENTAGE_ACCURACY,
        "weight": 0.7,
        "examples": [
            "Who has the best record on clay courts?",
            "Which players perform best on grass?",
            "What is Nadal's win percentage on clay?"
        ]
    },
    
    TestCategory.STATISTICAL_ANALYSIS: {
        "description": "Statistical analysis and numerical queries",
        "validation_method": ValidationMethod.NUMERICAL_ACCURACY,
        "weight": 0.9,
        "examples": [
            "Who has the most Grand Slam titles?",
            "Which player has the highest ranking?",
            "What is the average age of top 10 players?"
        ]
    },
    
    TestCategory.HISTORICAL_RECORDS: {
        "description": "Historical records and achievements",
        "validation_method": ValidationMethod.SEMANTIC_SIMILARITY,
        "weight": 0.8,
        "examples": [
            "Who was the youngest Wimbledon champion?",
            "Which player has the longest winning streak?",
            "Who won the most matches in a single year?"
        ]
    },
    
    TestCategory.PLAYER_RANKINGS: {
        "description": "Player rankings and positions",
        "validation_method": ValidationMethod.NUMERICAL_ACCURACY,
        "weight": 0.9,
        "examples": [
            "Who was ranked #1 in 2020?",
            "Which players were in the top 10 in 2019?",
            "What was Federer's highest ranking?"
        ]
    },
    
    TestCategory.MATCH_DETAILS: {
        "description": "Specific match details and scores",
        "validation_method": ValidationMethod.PARTIAL_MATCH,
        "weight": 0.8,
        "examples": [
            "What was the score of the 2008 Wimbledon final?",
            "Who won the longest match in tennis history?",
            "What was the duration of the 2010 Wimbledon match?"
        ]
    },
    
    TestCategory.COMPLEX_QUERIES: {
        "description": "Complex multi-part questions",
        "validation_method": ValidationMethod.SEMANTIC_SIMILARITY,
        "weight": 0.6,
        "examples": [
            "Compare Federer and Nadal's performance on different surfaces",
            "Which players have won all four Grand Slams?",
            "Analyze the evolution of tennis over the decades"
        ]
    }
}


def get_validation_function(validation_method: ValidationMethod) -> Callable:
    """
    Get the appropriate validation function for a given validation method.
    
    Args:
        validation_method: The validation method to use
        
    Returns:
        Callable validation function
    """
    validation_functions = {
        ValidationMethod.EXACT_MATCH: _validate_exact_match,
        ValidationMethod.SEMANTIC_SIMILARITY: _validate_semantic_similarity,
        ValidationMethod.NUMERICAL_ACCURACY: _validate_numerical_accuracy,
        ValidationMethod.PARTIAL_MATCH: _validate_partial_match,
        ValidationMethod.RANGE_ACCURACY: _validate_range_accuracy,
        ValidationMethod.PERCENTAGE_ACCURACY: _validate_percentage_accuracy
    }
    
    return validation_functions.get(validation_method, _validate_semantic_similarity)


def _validate_exact_match(ai_answer: str, expected_answer: str) -> float:
    """Validate exact string match."""
    if ai_answer.lower().strip() == expected_answer.lower().strip():
        return 1.0
    return 0.0


def _validate_semantic_similarity(ai_answer: str, expected_answer: str) -> float:
    """Validate semantic similarity (placeholder for now)."""
    # TODO: Implement semantic similarity using embeddings
    return _validate_exact_match(ai_answer, expected_answer)


def _validate_numerical_accuracy(ai_answer: str, expected_answer: str) -> float:
    """Validate numerical accuracy."""
    try:
        ai_num = float(ai_answer.strip())
        expected_num = float(expected_answer.strip())
        
        if expected_num == 0:
            return 1.0 if ai_num == 0 else 0.0
        
        accuracy = 1.0 - abs(ai_num - expected_num) / abs(expected_num)
        return max(0.0, min(1.0, accuracy))
    except (ValueError, TypeError):
        return _validate_exact_match(ai_answer, expected_answer)


def _validate_partial_match(ai_answer: str, expected_answer: str) -> float:
    """Validate partial match for complex answers."""
    ai_words = set(ai_answer.lower().split())
    expected_words = set(expected_answer.lower().split())
    
    if not expected_words:
        return 1.0
    
    intersection = ai_words.intersection(expected_words)
    return len(intersection) / len(expected_words)


def _validate_range_accuracy(ai_answer: str, expected_answer: str) -> float:
    """Validate if answer is within acceptable range."""
    try:
        ai_num = float(ai_answer.strip())
        expected_num = float(expected_answer.strip())
        
        # Allow 10% tolerance
        tolerance = 0.1
        lower_bound = expected_num * (1 - tolerance)
        upper_bound = expected_num * (1 + tolerance)
        
        if lower_bound <= ai_num <= upper_bound:
            return 1.0
        else:
            return 0.0
    except (ValueError, TypeError):
        return _validate_exact_match(ai_answer, expected_answer)


def _validate_percentage_accuracy(ai_answer: str, expected_answer: str) -> float:
    """Validate percentage accuracy."""
    try:
        ai_num = float(ai_answer.strip().replace('%', ''))
        expected_num = float(expected_answer.strip().replace('%', ''))
        
        # Allow 5% tolerance for percentages
        tolerance = 0.05
        lower_bound = expected_num * (1 - tolerance)
        upper_bound = expected_num * (1 + tolerance)
        
        if lower_bound <= ai_num <= upper_bound:
            return 1.0
        else:
            return 0.0
    except (ValueError, TypeError):
        return _validate_exact_match(ai_answer, expected_answer)


def get_test_categories() -> Dict[TestCategory, Dict[str, Any]]:
    """
    Get all test categories with their configurations.
    
    Returns:
        Dictionary of test categories and their configurations
    """
    return TEST_CATEGORIES
