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
        
        # Keywords that suggest table format
        self.table_keywords = [
            'list', 'all', 'every', 'show', 'top', 'compare', 'rankings', 
            'head-to-head', 'h2h', 'matches', 'results', 'statistics', 
            'stats', 'summary', 'table', 'chart', 'breakdown'
        ]
        
        # Keywords that suggest text format
        self.text_keywords = [
            'who won', 'what was', 'how many', 'when did', 'where did',
            'who is', 'what is', 'score', 'result', 'answer'
        ]
    
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
        """Preserve data structure and types for DataFrame compatibility."""
        # Keep None values as None - pandas will handle them correctly:
        # - None becomes NaN for numeric columns (float/int)
        # - None stays as None for object columns (strings)
        # This ensures proper type inference and PyArrow compatibility
        # Don't convert to empty strings as it causes mixed types (string + float)
        return data
    
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
            # Convert all items to strings before joining (handles int/float values)
            score = " ".join(str(item) for item in result[2:] if item) if len(result) > 2 else "Score not available"
            
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
                # Convert all items to strings before joining (handles int/float values)
                score = " ".join(str(item) for item in row[2:] if item) if len(row) > 2 else "Score not available"
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
    
    def format_with_context(self, data: List, user_question: str = "") -> str:
        """
        Format results with context detection from user question.
        This method provides compatibility with the DataFormatter interface.
        
        Args:
            data: The data to format
            user_question: The user's question for context
            
        Returns:
            Formatted result string
        """
        return self.format_result(data, user_question, context=None)
    
    def should_format_as_table(self, data: List, user_question: str = "") -> bool:
        """
        Determine if data should be displayed as a table.
        
        Args:
            data: The data to analyze
            user_question: The user's question for context
            
        Returns:
            True if data should be displayed as table, False otherwise
        """
        if not data or len(data) == 0:
            return False
        
        # Analyze data structure
        num_rows = len(data)
        num_cols = len(data[0]) if data else 0
        
        # Rule 1: Single row, single column → text format
        if num_rows == 1 and num_cols == 1:
            return False
        
        # Rule 2: Multiple rows (3+) → table format
        if num_rows >= 3:
            return True
        
        # Rule 3: Multiple columns (3+) → table format
        if num_cols >= 3:
            return True
        
        # Rule 4: Query type analysis
        query_type = self._analyze_query_type(user_question)
        
        # Table-friendly query types
        if query_type in ['list', 'comparison', 'ranking', 'head_to_head', 'statistics']:
            return True
        
        # Text-friendly query types
        if query_type in ['single_value', 'simple_answer', 'narrative']:
            return False
        
        # Rule 5: For 2 rows, check if it's a comparison or simple answer
        if num_rows == 2:
            # If it looks like a comparison (e.g., "Player A vs Player B")
            if self._is_comparison_query(user_question):
                return True
            # Otherwise, text format
            return False
        
        # Default: use table for multiple columns, text for single column
        return num_cols >= 2
    
    def _analyze_query_type(self, user_question: str) -> str:
        """
        Analyze the query type to determine format preference.
        
        Args:
            user_question: The user's question
            
        Returns:
            Query type string
        """
        question_lower = user_question.lower()
        
        # List queries
        if any(keyword in question_lower for keyword in ['list', 'all', 'every', 'show all']):
            return 'list'
        
        # Comparison queries
        if any(keyword in question_lower for keyword in ['top', 'best', 'most', 'compare', 'versus', 'vs']):
            return 'comparison'
        
        # Ranking queries
        if any(keyword in question_lower for keyword in ['ranking', 'ranked', 'rankings', 'top 10', 'top 5']):
            return 'ranking'
        
        # Head-to-head queries
        if any(keyword in question_lower for keyword in ['head-to-head', 'h2h', 'head to head', 'against']):
            return 'head_to_head'
        
        # Statistics queries
        if any(keyword in question_lower for keyword in ['statistics', 'stats', 'summary', 'breakdown', 'analysis']):
            return 'statistics'
        
        # Single value queries
        if any(keyword in question_lower for keyword in ['who won', 'what was', 'who is', 'what is']):
            return 'single_value'
        
        # Simple answer queries
        if any(keyword in question_lower for keyword in ['how many', 'when did', 'where did']):
            return 'simple_answer'
        
        # Default to narrative for complex queries
        return 'narrative'
    
    def _is_comparison_query(self, user_question: str) -> bool:
        """
        Check if the query is asking for a comparison.
        
        Args:
            user_question: The user's question
            
        Returns:
            True if it's a comparison query
        """
        question_lower = user_question.lower()
        comparison_keywords = ['vs', 'versus', 'against', 'compare', 'comparison', 'between']
        return any(keyword in question_lower for keyword in comparison_keywords)
    
    def _is_h2h_query(self, user_question: str) -> bool:
        """
        Check if the query is a head-to-head (h2h) query.
        
        Args:
            user_question: The user's question
            
        Returns:
            True if it's an h2h query
        """
        question_lower = user_question.lower()
        h2h_keywords = ['h2h', 'head-to-head', 'head to head']
        return any(keyword in question_lower for keyword in h2h_keywords)
    
    def _filter_h2h_columns(self, data: List, columns: List[str]) -> tuple:
        """
        Filter and reorder columns for h2h queries to show only:
        Year, Tournament Name, Surface, Winner, Loser, Score
        
        Args:
            data: The data rows
            columns: List of column names
            
        Returns:
            Tuple of (filtered_data, filtered_columns)
        """
        if not data or not columns:
            return data, columns
        
        # Map of desired column names to their indices in the original data
        # Order: Year, Tournament Name, Surface, Winner, Loser, Score
        desired_columns = ['Year', 'Tournament', 'Surface', 'Winner', 'Loser', 'Score']
        
        # Map column names to their indices (case-insensitive, handle variations)
        column_mapping = {
            'year': 'event_year',
            'tournament': 'tourney_name',
            'surface': 'surface',
            'winner': 'winner_name',
            'loser': 'loser_name',
            'score': 'score'
        }
        
        # Find indices of desired columns in the original column list
        column_indices = []
        filtered_column_names = []
        
        for desired_col in desired_columns:
            # Try to find matching column
            found = False
            for i, col in enumerate(columns):
                col_lower = col.lower()
                # Check if this column matches our desired column
                if desired_col.lower() == 'year' and ('year' in col_lower or 'event_year' in col_lower):
                    column_indices.append(i)
                    filtered_column_names.append(desired_col)
                    found = True
                    break
                elif desired_col.lower() == 'tournament' and ('tournament' in col_lower or 'tourney_name' in col_lower):
                    # Match tournament or tourney_name, but not just 'tour' (which is ATP/WTA)
                    column_indices.append(i)
                    filtered_column_names.append(desired_col)
                    found = True
                    break
                elif desired_col.lower() == 'surface' and 'surface' in col_lower:
                    column_indices.append(i)
                    filtered_column_names.append(desired_col)
                    found = True
                    break
                elif desired_col.lower() == 'winner' and ('winner' in col_lower and 'rank' not in col_lower):
                    column_indices.append(i)
                    filtered_column_names.append(desired_col)
                    found = True
                    break
                elif desired_col.lower() == 'loser' and ('loser' in col_lower and 'rank' not in col_lower):
                    column_indices.append(i)
                    filtered_column_names.append(desired_col)
                    found = True
                    break
                elif desired_col.lower() == 'score' and 'score' in col_lower:
                    column_indices.append(i)
                    filtered_column_names.append(desired_col)
                    found = True
                    break
            
            # If not found, try to find by SQL column mapping
            if not found:
                sql_col_name = column_mapping.get(desired_col.lower())
                if sql_col_name:
                    for i, col in enumerate(columns):
                        if sql_col_name.lower() in col.lower():
                            column_indices.append(i)
                            filtered_column_names.append(desired_col)
                            found = True
                            break
        
        # If we found at least 5 columns (Year, Surface, Winner, Loser, Score), filter the data
        # Tournament name might not be available in all queries, so it's optional
        if len(column_indices) >= 5:
            filtered_data = []
            for row in data:
                filtered_row = [row[i] if i < len(row) else None for i in column_indices]
                filtered_data.append(filtered_row)
            return filtered_data, filtered_column_names
        
        # If we couldn't find enough columns, return original data and columns
        return data, columns
    
    def format_for_display(self, data: List, user_question: str = "", sql_query: str = "") -> Dict[str, Any]:
        """
        Format results for display, returning both text and table-ready data.
        
        Args:
            data: The data to format
            user_question: The user's question for context
            sql_query: Optional SQL query to extract column names from
            
        Returns:
            Dictionary with 'format', 'text', 'data', and 'columns' keys
        """
        # Filter out None values
        filtered_data = self._filter_none_values(data)
        
        if not filtered_data or len(filtered_data) == 0:
            return {
                'format': 'text',
                'text': 'No results found',
                'data': [],
                'columns': []
            }
        
        # Determine format
        should_table = self.should_format_as_table(filtered_data, user_question)
        
        # Format text version
        formatted_text = self.format_result(filtered_data, user_question, context=None)
        
        # Extract columns from SQL query if available, otherwise infer from context
        if sql_query:
            columns = self._extract_columns_from_sql(sql_query, filtered_data)
        else:
            columns = self._extract_columns(filtered_data, user_question)
        
        # For h2h queries, filter and reorder columns to show only: Year, Tournament, Surface, Winner, Loser, Score
        is_h2h = self._is_h2h_query(user_question)
        if is_h2h and should_table:
            filtered_data, columns = self._filter_h2h_columns(filtered_data, columns)
        
        if should_table:
            return {
                'format': 'table',
                'text': formatted_text,  # Keep text as fallback/header
                'data': filtered_data,
                'columns': columns
            }
        else:
            return {
                'format': 'text',
                'text': formatted_text,
                'data': filtered_data,
                'columns': columns
            }
    
    def _extract_columns_from_sql(self, sql_query: str, data: List) -> List[str]:
        """
        Extract column names from SQL SELECT query.
        
        Args:
            sql_query: SQL SELECT query string
            data: The data to match column count
            
        Returns:
            List of column names
        """
        import re
        
        # Extract SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE | re.DOTALL)
        if not select_match:
            # Fallback to context-based extraction
            return self._extract_columns(data, "")
        
        select_clause = select_match.group(1).strip()
        
        # Split by comma, handling nested parentheses
        columns = []
        current_col = ""
        paren_level = 0
        
        for char in select_clause:
            if char == '(':
                paren_level += 1
                current_col += char
            elif char == ')':
                paren_level -= 1
                current_col += char
            elif char == ',' and paren_level == 0:
                # This is a column separator
                col = current_col.strip()
                if col:
                    # Extract column name (handle aliases with AS)
                    col_name = self._extract_column_name(col)
                    # Always append - _extract_column_name should always return a value
                    if col_name and col_name.strip():
                        columns.append(col_name)
                    else:
                        # Fallback: use column expression as-is (cleaned up)
                        columns.append(col.strip().replace('_', ' ').title())
                current_col = ""
            else:
                current_col += char
        
        # Add the last column
        if current_col.strip():
            col_name = self._extract_column_name(current_col.strip())
            # Always append - _extract_column_name should always return a value
            if col_name and col_name.strip():
                columns.append(col_name)
            else:
                # Fallback: use column expression as-is (cleaned up)
                columns.append(current_col.strip().replace('_', ' ').title())
        
        # Validate column count matches data
        if data and len(data) > 0:
            expected_cols = len(data[0])
            if len(columns) != expected_cols:
                # If mismatch, use generic names or context-based extraction
                # This ensures we always have the correct number of columns
                fallback_columns = self._extract_columns(data, "")
                if len(fallback_columns) == expected_cols:
                    return fallback_columns
                # If fallback also fails, generate generic column names
                return [f'Column {i+1}' for i in range(expected_cols)]
        
        return columns if columns else self._extract_columns(data, "")
    
    def _extract_column_name(self, column_expr: str) -> str:
        """
        Extract column name from SQL column expression (handles aliases, functions, etc.).
        
        Args:
            column_expr: SQL column expression (e.g., "winner_name", "winner_name AS Winner", "COUNT(*) as count")
            
        Returns:
            Clean column name
        """
        import re
        
        # Remove leading/trailing whitespace
        column_expr = column_expr.strip()
        
        # Check for AS alias
        as_match = re.search(r'\s+AS\s+([^\s,]+)', column_expr, re.IGNORECASE)
        if as_match:
            return as_match.group(1).strip('"\'`')
        
        # Check for space-separated alias (without AS)
        parts = column_expr.split()
        if len(parts) > 1 and not parts[-1].upper() in ['FROM', 'WHERE', 'GROUP', 'ORDER', 'HAVING']:
            # Last part might be an alias
            potential_alias = parts[-1].strip('"\'`')
            if potential_alias and not potential_alias.startswith('('):
                return potential_alias
        
        # Extract column name (last identifier before any function/operator)
        # Handle cases like "table.column", "column", "COUNT(column)"
        col_match = re.search(r'(\w+)\s*$', column_expr)
        if col_match:
            col_name = col_match.group(1)
            # Clean up common SQL column names: convert snake_case to Title Case
            # Map common column names to readable formats
            column_mapping = {
                'winner_name': 'Winner',
                'loser_name': 'Loser',
                'tourney_name': 'Tournament',
                'event_year': 'Year',
                'surface': 'Surface',
                'score': 'Score',
                'round': 'Round',
                'tourney_date': 'Date',
                'winner_rank': 'Winner Rank',
                'loser_rank': 'Loser Rank',
                'set1': 'Set 1',
                'set2': 'Set 2',
                'set3': 'Set 3',
                'set4': 'Set 4',
                'set5': 'Set 5',
                'minutes': 'Minutes',
                'tour': 'Tour'
            }
            
            if col_name.lower() in column_mapping:
                return column_mapping[col_name.lower()]
            
            # Otherwise convert snake_case to Title Case
            col_name = col_name.replace('_', ' ').title()
            return col_name
        
        # Fallback: use the original expression if no match found
        return column_expr.strip()
    
    def _extract_columns(self, data: List, user_question: str = "") -> List[str]:
        """
        Extract column names from data structure and query context.
        
        Args:
            data: The data to analyze
            user_question: The user's question for context
            
        Returns:
            List of column names
        """
        if not data or len(data) == 0:
            return []
        
        num_cols = len(data[0])
        question_lower = user_question.lower()
        
        # Default column names based on data structure
        if num_cols == 1:
            return ['Result']
        elif num_cols == 2:
            # Common 2-column patterns
            if 'head-to-head' in question_lower or 'h2h' in question_lower:
                return ['Player', 'Wins']
            elif 'vs' in question_lower or 'versus' in question_lower:
                return ['Player', 'Record']
            else:
                return ['Column 1', 'Column 2']
        elif num_cols >= 3:
            # Common multi-column patterns (match data)
            if any(keyword in question_lower for keyword in ['match', 'game', 'score']):
                return ['Winner', 'Loser', 'Score'] + [f'Set {i}' for i in range(4, num_cols + 1)]
            elif any(keyword in question_lower for keyword in ['player', 'tournament', 'ranking']):
                # Try to infer columns from context
                columns = ['Player']
                if 'tournament' in question_lower:
                    columns.append('Tournament')
                if 'year' in question_lower or any(char.isdigit() for char in user_question):
                    columns.append('Year')
                if 'ranking' in question_lower:
                    columns.append('Ranking')
                if 'wins' in question_lower:
                    columns.append('Wins')
                # Fill remaining columns
                while len(columns) < num_cols:
                    columns.append(f'Column {len(columns) + 1}')
                return columns[:num_cols]
            else:
                # Generic column names
                return [f'Column {i+1}' for i in range(num_cols)]
        
        return []

