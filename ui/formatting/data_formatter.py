"""
Data formatting utilities for AskTennis AI application.
Handles all data formatting, response processing, and result presentation.
Extracted from ui_components.py for better modularity.
"""

import re
from typing import List, Dict, Any, Optional


class DataFormatter:
    """
    Centralized data formatting class for tennis query results.
    Handles various data formats and presentation styles.
    """
    
    @staticmethod
    def is_list_query(user_question: str) -> bool:
        """Detect if the user is asking for a list of items."""
        list_keywords = ['list', 'all', 'every', 'complete', 'full', 'entire', 'chronological', 'chronologically']
        return any(keyword in user_question.lower() for keyword in list_keywords)
    
    @staticmethod
    def format_match_result(data: List, query_context: str = "") -> str:
        """Format match results in a user-friendly way."""
        if not data or len(data) == 0:
            return "No results found"
        
        result = data[0]  # Get first result
        
        # Handle different result formats
        if len(result) >= 3:  # winner, loser, score format
            winner, loser = result[0], result[1]
            # Filter out None values and format score
            score_parts = [str(s) for s in result[2:] if s is not None]
            score = " ".join(score_parts) if score_parts else "Score not available"
            
            # Add context if available
            context = f" in {query_context}" if query_context else ""
            return f"{winner} defeated {loser} {score}{context}"
        
        elif len(result) == 2:  # winner, score format
            winner, score = result[0], result[1]
            return f"{winner} won with score {score}"
        
        else:  # Single value
            return str(result[0])
    
    @staticmethod
    def format_tournament_results(data: List, tournament_name: str = "") -> str:
        """Format tournament results with proper context."""
        if not data or len(data) == 0:
            return "No results found"
        
        if len(data) == 1:
            result = data[0]
            if len(result) >= 3:  # winner, loser, score format
                winner, loser = result[0], result[1]
                score_parts = [str(s) for s in result[2:] if s is not None]
                score = " ".join(score_parts) if score_parts else "Score not available"
                context = f" in {tournament_name}" if tournament_name else ""
                return f"{winner} defeated {loser} {score}{context}"
            else:
                return str(result[0])
        else:
            # Multiple results - format as list
            results = []
            for i, row in enumerate(data, 1):
                if len(row) >= 3:
                    winner, loser = row[0], row[1]
                    score_parts = [str(s) for s in row[2:] if s is not None]
                    score = " ".join(score_parts) if score_parts else "Score not available"
                    results.append(f"{i}. {winner} defeated {loser} {score}")
                else:
                    results.append(f"{i}. {row[0]}")
            
            context = f" in {tournament_name}" if tournament_name else ""
            return f"Found {len(data)} result(s){context}:\n\n" + "\n".join(results)
    
    @staticmethod
    def format_database_result(data: List, query_type: str = "general") -> str:
        """Format database results based on query type."""
        if not data or len(data) == 0:
            return "No results found"
        
        # Filter out None values from the result
        filtered_data = []
        for row in data:
            filtered_row = [str(item) for item in row if item is not None]
            filtered_data.append(filtered_row)
        
        if len(filtered_data) == 1:
            result = filtered_data[0]
            if len(result) >= 3:  # winner, loser, score format
                winner, loser = result[0], result[1]
                score = " ".join(result[2:]) if len(result) > 2 else "Score not available"
                return f"{winner} defeated {loser} {score}"
            elif len(result) == 2:
                return f"{result[0]} - {result[1]}"
            else:
                return str(result[0])
        else:
            # Multiple results
            results = []
            for i, row in enumerate(filtered_data, 1):
                if len(row) >= 3:
                    winner, loser = row[0], row[1]
                    score = " ".join(row[2:]) if len(row) > 2 else "Score not available"
                    results.append(f"{i}. {winner} defeated {loser} {score}")
                elif len(row) == 2:
                    results.append(f"{i}. {row[0]} - {row[1]}")
                else:
                    results.append(f"{i}. {row[0]}")
            
            return f"Found {len(filtered_data)} result(s):\n\n" + "\n".join(results)
    
    @staticmethod
    def detect_query_context(user_question: str, data: List) -> Dict[str, Any]:
        """Detect context from user question and data to improve formatting."""
        question_lower = user_question.lower()
        context = {}
        
        # Extract tournament name if mentioned
        tournament_keywords = ['tournament', 'final', 'won', 'champion', 'brisbane', 'auckland', 'doha', 'dubai', 'abu dhabi']
        if any(keyword in question_lower for keyword in tournament_keywords):
            # Try to extract tournament name from question
            words = question_lower.split()
            for i, word in enumerate(words):
                if word in ['won', 'champion', 'final'] and i > 0:
                    # Look for tournament name before the keyword
                    potential_tournament = words[i-1].title()
                    if len(potential_tournament) > 2:  # Avoid short words
                        context['tournament'] = potential_tournament
                        break
            
            # Also check for specific tournament names
            for tournament in ['brisbane', 'auckland', 'doha', 'dubai', 'abu dhabi']:
                if tournament in question_lower:
                    context['tournament'] = tournament.title()
                    break
        
        # Extract year if mentioned
        year_match = re.search(r'\b(20\d{2})\b', user_question)
        if year_match:
            context['year'] = year_match.group(1)
        
        # Extract round if mentioned
        round_keywords = ['final', 'semifinal', 'quarterfinal', 'round']
        for keyword in round_keywords:
            if keyword in question_lower:
                context['round'] = keyword.title()
                break
        
        # Extract player names if mentioned
        player_keywords = ['gauff', 'sabalenka', 'pegula', 'swiatek', 'rybakina', 'dimitrov', 'tabilo', 'svitolina']
        for player in player_keywords:
            if player in question_lower:
                context['player'] = player.title()
                break
        
        # Also try to extract player names from the question more broadly
        words = question_lower.split()
        for i, word in enumerate(words):
            if word in ['matches', 'of'] and i > 0:
                potential_player = words[i-1].title()
                if len(potential_player) > 2:  # Avoid short words
                    context['player'] = potential_player
                    break
        
        # Detect query type for better formatting
        if 'who won' in question_lower:
            context['query_type'] = 'winner'
        elif 'what was the score' in question_lower:
            context['query_type'] = 'score'
        elif 'list' in question_lower or 'all' in question_lower:
            context['query_type'] = 'list'
        elif 'trend' in question_lower or 'performance' in question_lower:
            context['query_type'] = 'analysis'
        
        return context
    
    @staticmethod
    def format_with_context(data: List, user_question: str = "") -> str:
        """Format database results with context from user question."""
        if not data or len(data) == 0:
            return "No results found"
        
        context = DataFormatter.detect_query_context(user_question, data)
        
        # Filter out None values from the result
        filtered_data = []
        for row in data:
            filtered_row = [str(item) for item in row if item is not None]
            filtered_data.append(filtered_row)
        
        # Check if this is a list query
        is_list_query = any(keyword in user_question.lower() for keyword in ['list', 'all', 'chronologically', 'matches'])
        
        if len(filtered_data) == 1:
            result = filtered_data[0]
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
        else:
            # Multiple results - enhanced formatting for list queries
            if is_list_query:
                return DataFormatter.format_chronological_list(filtered_data, user_question, context)
            else:
                # Regular multiple results
                results = []
                for i, row in enumerate(filtered_data, 1):
                    if len(row) >= 3:
                        winner, loser = row[0], row[1]
                        score = " ".join(row[2:]) if len(row) > 2 else "Score not available"
                        results.append(f"{i}. {winner} defeated {loser} {score}")
                    elif len(row) == 2:
                        results.append(f"{i}. {row[0]} - {row[1]}")
                    else:
                        results.append(f"{i}. {row[0]}")
                
                return f"Found {len(filtered_data)} result(s):\n\n" + "\n".join(results)