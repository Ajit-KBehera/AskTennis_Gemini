"""
Consolidated data formatting utilities for AskTennis AI application.
Reduces multiple formatting methods into a single, configurable formatter.
"""

import re
from typing import List, Dict, Any, Optional


class ConsolidatedFormatter:
    """
    Consolidated data formatter that handles all formatting needs.
    Replaces multiple formatting methods with a single, configurable system.
    """
    
    def __init__(self):
        """Initialize the consolidated formatter."""
        self.list_keywords = ['list', 'all', 'every', 'complete', 'full', 'entire', 'chronological', 'chronologically']
        self.tournament_keywords = ['tournament', 'final', 'won', 'champion', 'brisbane', 'auckland', 'doha', 'dubai', 'abu dhabi']
        self.round_keywords = ['final', 'semifinal', 'quarterfinal', 'round']
        self.player_keywords = ['gauff', 'sabalenka', 'pegula', 'swiatek', 'rybakina', 'dimitrov', 'tabilo', 'svitolina']
    
    def format_result(self, data: List, user_question: str = "", context: Dict[str, Any] = None) -> str:
        """
        Universal result formatter that handles all formatting needs.
        
        Args:
            data: The data to format
            user_question: The user's question for context
            context: Additional context information
            
        Returns:
            Formatted result string
        """
        if not data or len(data) == 0:
            return "No results found"
        
        # Detect context if not provided
        if context is None:
            context = self._detect_context(user_question, data)
        
        # Check if this is a list query
        is_list_query = self._is_list_query(user_question)
        
        # Filter out None values
        filtered_data = self._filter_none_values(data)
        
        if len(filtered_data) == 1:
            return self._format_single_result(filtered_data[0], context)
        else:
            if is_list_query:
                return self._format_list_results(filtered_data, user_question, context)
            else:
                return self._format_multiple_results(filtered_data, context)
    
    def _is_list_query(self, user_question: str) -> bool:
        """Check if the user is asking for a list of items."""
        return any(keyword in user_question.lower() for keyword in self.list_keywords)
    
    def _filter_none_values(self, data: List) -> List:
        """Filter out None values from data."""
        filtered_data = []
        for row in data:
            filtered_row = [str(item) for item in row if item is not None]
            filtered_data.append(filtered_row)
        return filtered_data
    
    def _detect_context(self, user_question: str, data: List) -> Dict[str, Any]:
        """Detect context from user question and data."""
        question_lower = user_question.lower()
        context = {}
        
        # Extract tournament name
        if any(keyword in question_lower for keyword in self.tournament_keywords):
            context['tournament'] = self._extract_tournament_name(question_lower)
        
        # Extract year
        year_match = re.search(r'\b(20\d{2})\b', user_question)
        if year_match:
            context['year'] = year_match.group(1)
        
        # Extract round
        for keyword in self.round_keywords:
            if keyword in question_lower:
                context['round'] = keyword.title()
                break
        
        # Extract player names
        for player in self.player_keywords:
            if player in question_lower:
                context['player'] = player.title()
                break
        
        # Detect query type
        if 'who won' in question_lower:
            context['query_type'] = 'winner'
        elif 'what was the score' in question_lower:
            context['query_type'] = 'score'
        elif 'list' in question_lower or 'all' in question_lower:
            context['query_type'] = 'list'
        elif 'trend' in question_lower or 'performance' in question_lower:
            context['query_type'] = 'analysis'
        
        return context
    
    def _extract_tournament_name(self, question_lower: str) -> str:
        """Extract tournament name from question."""
        words = question_lower.split()
        for i, word in enumerate(words):
            if word in ['won', 'champion', 'final'] and i > 0:
                potential_tournament = words[i-1].title()
                if len(potential_tournament) > 2:
                    return potential_tournament
        
        # Check for specific tournament names
        for tournament in ['brisbane', 'auckland', 'doha', 'dubai', 'abu dhabi']:
            if tournament in question_lower:
                return tournament.title()
        
        return ""
    
    def _format_single_result(self, result: List, context: Dict[str, Any]) -> str:
        """Format a single result."""
        if len(result) >= 3:  # winner, loser, score format
            winner, loser = result[0], result[1]
            score = " ".join(result[2:]) if len(result) > 2 else "Score not available"
            
            # Add context information
            context_parts = []
            if 'tournament' in context:
                context_parts.append(f"in {context['tournament']}")
            if 'year' in context:
                context_parts.append(f"in {context['year']}")
            if 'round' in context:
                context_parts.append(f"in the {context['round']}")
            
            context_str = f" ({' '.join(context_parts)})" if context_parts else ""
            
            # Format based on query type
            if context.get('query_type') == 'winner':
                return f"{winner} won{context_str}"
            elif context.get('query_type') == 'score':
                return f"The score was {score}{context_str}"
            else:
                return f"{winner} defeated {loser} {score}{context_str}"
        elif len(result) == 2:
            return f"{result[0]} - {result[1]}"
        else:
            return str(result[0])
    
    def _format_multiple_results(self, data: List, context: Dict[str, Any]) -> str:
        """Format multiple results."""
        results = []
        for i, row in enumerate(data, 1):
            if len(row) >= 3:
                winner, loser = row[0], row[1]
                score = " ".join(row[2:]) if len(row) > 2 else "Score not available"
                results.append(f"{i}. {winner} defeated {loser} {score}")
            elif len(row) == 2:
                results.append(f"{i}. {row[0]} - {row[1]}")
            else:
                results.append(f"{i}. {row[0]}")
        
        return f"Found {len(data)} result(s):\n\n" + "\n".join(results)
    
    def _format_list_results(self, data: List, user_question: str, context: Dict[str, Any]) -> str:
        """Format list results with chronological ordering."""
        # This would contain the complex chronological formatting logic
        # For now, use the simpler multiple results format
        return self._format_multiple_results(data, context)
