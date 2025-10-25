"""
Tennis Ranking Question Validator

This module provides validation and correction for ranking questions to ensure
proper data source usage and SQL construction.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from .ranking_analysis import (
    classify_ranking_question, 
    determine_tour_context, 
    RankingQuestionType,
    TourType
)


class RankingQuestionValidator:
    """Validate and correct ranking questions."""
    
    def __init__(self):
        """Initialize the validator."""
        self.common_mistakes = {
            "using_matches_for_official_rankings": {
                "pattern": r"SELECT.*FROM matches.*WHERE.*winner_rank",
                "description": "Using matches table for official rankings instead of player_rankings_history",
                "fix": "Use player_rankings_history table for official rankings"
            },
            "missing_tour_separation": {
                "pattern": r"SELECT.*FROM.*WHERE.*(?!tour\s*=)",
                "description": "Missing tour separation for ranking queries",
                "fix": "Add tour = 'ATP' or tour = 'WTA' filter"
            },
            "incorrect_date_format": {
                "pattern": r"ranking_date.*=.*'[0-9]{4}'",
                "description": "Using year-only date format instead of full timestamp",
                "fix": "Use full timestamp format: 'YYYY-MM-DD HH:MM:SS'"
            },
            "wrong_player_name_concatenation": {
                "pattern": r"winner_name.*FROM matches",
                "description": "Using winner_name from matches instead of proper name concatenation",
                "fix": "Use name_first || ' ' || name_last for player_rankings_history"
            }
        }
    
    def validate_ranking_question(self, question: str, sql: str) -> Dict[str, Any]:
        """
        Validate ranking question and SQL.
        
        Args:
            question: The ranking question
            sql: The SQL query to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "question_type": None,
            "tour_context": None,
            "recommended_table": None
        }
        
        # Classify the question
        question_type = classify_ranking_question(question)
        tour_context = determine_tour_context(question)
        
        validation_result["question_type"] = question_type.value
        validation_result["tour_context"] = tour_context.value
        
        # Check for common mistakes
        for mistake_type, mistake_info in self.common_mistakes.items():
            if re.search(mistake_info["pattern"], sql, re.IGNORECASE):
                validation_result["errors"].append({
                    "type": mistake_type,
                    "description": mistake_info["description"],
                    "fix": mistake_info["fix"]
                })
                validation_result["is_valid"] = False
        
        # Validate table usage
        recommended_table = self._get_recommended_table(question_type)
        validation_result["recommended_table"] = recommended_table
        
        if recommended_table not in sql:
            validation_result["warnings"].append({
                "type": "table_mismatch",
                "description": f"Expected table '{recommended_table}' not found in SQL",
                "fix": f"Use {recommended_table} table for this type of ranking question"
            })
        
        # Validate tour separation
        if question_type in [RankingQuestionType.OFFICIAL_RANKINGS, 
                           RankingQuestionType.CAREER_HIGH_RANKINGS,
                           RankingQuestionType.RANKING_PROGRESSION]:
            if "tour" not in sql.lower():
                validation_result["warnings"].append({
                    "type": "missing_tour_separation",
                    "description": "Missing tour separation for ranking query",
                    "fix": f"Add tour = '{tour_context.value}' filter"
                })
        
        # Validate date format for official rankings
        if question_type == RankingQuestionType.OFFICIAL_RANKINGS:
            if "ranking_date" in sql and not re.search(r"'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}'", sql):
                validation_result["warnings"].append({
                    "type": "incorrect_date_format",
                    "description": "Using incorrect date format for ranking_date",
                    "fix": "Use full timestamp format: 'YYYY-MM-DD HH:MM:SS'"
                })
        
        return validation_result
    
    def suggest_corrections(self, question: str, sql: str) -> List[str]:
        """
        Suggest corrections for ranking questions.
        
        Args:
            question: The ranking question
            sql: The SQL query to correct
            
        Returns:
            List of correction suggestions
        """
        suggestions = []
        
        # Classify question
        question_type = classify_ranking_question(question)
        tour_context = determine_tour_context(question)
        
        # Suggest table corrections
        if question_type == RankingQuestionType.OFFICIAL_RANKINGS:
            if "matches" in sql.lower():
                suggestions.append("Use player_rankings_history table instead of matches for official rankings")
            if "winner_name" in sql.lower():
                suggestions.append("Use name_first || ' ' || name_last instead of winner_name for player names")
        
        # Suggest tour separation
        if question_type in [RankingQuestionType.OFFICIAL_RANKINGS, 
                           RankingQuestionType.CAREER_HIGH_RANKINGS]:
            if "tour" not in sql.lower():
                suggestions.append(f"Add tour = '{tour_context.value}' filter for proper tour separation")
        
        # Suggest date format corrections
        if question_type == RankingQuestionType.OFFICIAL_RANKINGS:
            if "ranking_date" in sql:
                suggestions.append("Use full timestamp format for ranking_date: 'YYYY-MM-DD HH:MM:SS'")
        
        # Suggest specific SQL improvements
        if question_type == RankingQuestionType.OFFICIAL_RANKINGS:
            suggestions.append("For year-end rankings, use ranking_date = 'YYYY-12-30 00:00:00'")
        
        return suggestions
    
    def generate_corrected_sql(self, question: str, year: Optional[int] = None) -> str:
        """
        Generate corrected SQL for ranking questions.
        
        Args:
            question: The ranking question
            year: Optional year for temporal context
            
        Returns:
            Corrected SQL query
        """
        question_type = classify_ranking_question(question)
        tour_context = determine_tour_context(question)
        
        if question_type == RankingQuestionType.OFFICIAL_RANKINGS:
            # Extract rank limit
            rank_limit = 10  # Default
            rank_match = re.search(r'top\s+(\d+)', question.lower())
            if rank_match:
                rank_limit = int(rank_match.group(1))
            
            # Use year-end date
            date_str = f"{year}-12-30 00:00:00" if year else "2019-12-30 00:00:00"
            
            return f"""
                SELECT name_first || ' ' || name_last as player_name, rank
                FROM player_rankings_history 
                WHERE ranking_date = '{date_str}' 
                  AND rank <= {rank_limit} 
                  AND tour = '{tour_context.value}' 
                ORDER BY rank
            """.strip()
        
        elif question_type == RankingQuestionType.MATCH_TIME_RANKINGS:
            # Extract player names
            players = self._extract_player_names(question)
            if len(players) >= 2:
                return f"""
                    SELECT winner_name, loser_name, winner_rank, loser_rank, event_year, tourney_name
                    FROM matches 
                    WHERE (winner_name = '{players[0]}' AND loser_name = '{players[1]}')
                       OR (winner_name = '{players[1]}' AND loser_name = '{players[0]}')
                      AND event_year = {year if year else 2019}
                      AND (winner_rank IS NOT NULL OR loser_rank IS NOT NULL)
                """.strip()
        
        elif question_type == RankingQuestionType.CAREER_HIGH_RANKINGS:
            # Extract player name
            players = self._extract_player_names(question)
            if players:
                return f"""
                    SELECT name_first || ' ' || name_last as player_name, MIN(rank) as career_high_rank
                    FROM player_rankings_history 
                    WHERE name_first || ' ' || name_last = '{players[0]}'
                      AND tour = '{tour_context.value}'
                    GROUP BY name_first, name_last
                """.strip()
        
        return sql  # Return original if no correction needed
    
    def _get_recommended_table(self, question_type: RankingQuestionType) -> str:
        """Get recommended table for question type."""
        table_mapping = {
            RankingQuestionType.OFFICIAL_RANKINGS: "player_rankings_history",
            RankingQuestionType.MATCH_TIME_RANKINGS: "matches",
            RankingQuestionType.CAREER_HIGH_RANKINGS: "player_rankings_history",
            RankingQuestionType.RANKING_PROGRESSION: "player_rankings_history",
            RankingQuestionType.RANKING_COMPARISON: "player_rankings_history"
        }
        return table_mapping.get(question_type, "matches")
    
    def _extract_player_names(self, question: str) -> List[str]:
        """Extract player names from question."""
        # Simple pattern matching for player names
        # This could be enhanced with more sophisticated NLP
        player_patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First Last
            r'([A-Z][a-z]+)',  # Single name
        ]
        
        players = []
        for pattern in player_patterns:
            matches = re.findall(pattern, question)
            players.extend(matches)
        
        return players
    
    def validate_and_correct(self, question: str, sql: str) -> Dict[str, Any]:
        """
        Comprehensive validation and correction.
        
        Args:
            question: The ranking question
            sql: The SQL query to validate and correct
            
        Returns:
            Dictionary with validation results and corrections
        """
        validation = self.validate_ranking_question(question, sql)
        suggestions = self.suggest_corrections(question, sql)
        
        # Extract year from question
        year_match = re.search(r'\b(19|20)\d{2}\b', question)
        year = int(year_match.group()) if year_match else None
        
        corrected_sql = self.generate_corrected_sql(question, year)
        
        return {
            "validation": validation,
            "suggestions": suggestions,
            "corrected_sql": corrected_sql,
            "is_corrected": corrected_sql != sql
        }


# Export the validator class
__all__ = ['RankingQuestionValidator']
