"""
Query processing utilities for AskTennis AI application.
Handles query processing, agent interaction, and response handling.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
import ast
import pandas as pd
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.messages import HumanMessage, AIMessage
from tennis_logging.logging_factory import log_user_query, log_llm_interaction, log_final_response, log_error
from ui.formatting.consolidated_formatter import ConsolidatedFormatter


class QueryProcessor:
    """
    Centralized query processing class for tennis queries.
    Handles agent interaction, response processing, and error handling.
    
    Method execution order:
    1. __init__() - Initialize the processor
    2. handle_user_query() - Main entry point, handles user query
    3. process_agent_response() - Processes agent response (called by handle_user_query)
    """
    
    def __init__(self, data_formatter: ConsolidatedFormatter):
        """
        Initialize the query processor.
        
        Args:
            data_formatter: ConsolidatedFormatter instance for formatting responses
        """
        self.data_formatter = data_formatter
    
    def handle_user_query(self, user_question: str, agent_graph, logger):
        """Handle user query processing and response display."""
        # Log the user query
        log_user_query(user_question, "user_session")
        
        with st.spinner("The AI is analyzing your question and querying the database..."):
            try:
                start_time = datetime.now()
                
                # The config dictionary ensures each user gets their own conversation history.
                config = {"configurable": {"thread_id": "user_session"}}
                
                # Log the initial LLM interaction
                log_llm_interaction([HumanMessage(content=user_question)], "INITIAL_USER_QUERY")
                
                # Only pass the new message - LangGraph's checkpointer automatically loads
                # conversation history from memory based on the thread_id in config
                response = agent_graph.invoke(
                    {"messages": [HumanMessage(content=user_question)]},
                    config=config
                )
                
                # Log the complete conversation flow
                log_llm_interaction(response["messages"], "COMPLETE_CONVERSATION_FLOW")
                
                # Process the response - now returns dict with summary and structured data
                response_data = self.process_agent_response(response, logger, user_question)
                
                # Calculate total processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Store response data in session state (clear old data first to fix caching)
                if 'ai_query_results' in st.session_state:
                    del st.session_state.ai_query_results
                if 'ai_query_summary' in st.session_state:
                    del st.session_state.ai_query_summary
                if 'ai_query_structured_data' in st.session_state:
                    del st.session_state.ai_query_structured_data
                if 'ai_query_dataframe' in st.session_state:
                    del st.session_state.ai_query_dataframe
                
                # Store new response data
                st.session_state.ai_query_results = response_data
                st.session_state.ai_query_summary = response_data.get('summary', '')
                st.session_state.ai_query_structured_data = response_data.get('structured_data')
                st.session_state.ai_query_dataframe = response_data.get('dataframe')
                
                # Log response
                summary_text = response_data.get('summary', '')
                if summary_text and summary_text.strip():
                    log_final_response(summary_text, processing_time)
                else:
                    log_final_response("No clear response generated", processing_time)

            except Exception as e:
                # Log error
                log_error(e, f"Processing user query: {user_question}")
                st.error(f"An error occurred while processing your request: {e}")
    
    def process_agent_response(self, response: dict, logger, user_question: str = "") -> Dict[str, Any]:
        """
        Process and format the agent's response.
        Returns a dictionary with summary text and structured data (if available).
        
        Returns:
            Dict with keys:
                - summary: str - Summary text to display
                - structured_data: Optional[List[List]] - Raw structured data (list of lists)
                - dataframe: Optional[pd.DataFrame] - DataFrame for table display
                - is_table_candidate: bool - Whether response should show a table
        """
        # Extract summary from LLM response
        summary = ""
        structured_data = None
        
        # The final answer is in the content of the last AIMessage.
        # Parse Gemini's structured output format
        last_message = response["messages"][-1]
        logger.info(f"Last message type: {type(last_message)}")
        logger.info(f"Last message content: {last_message.content}")
        logger.info(f"Last message content type: {type(last_message.content)}")
        
        if isinstance(last_message.content, list) and last_message.content:
            # For Gemini, content is a list of dicts. We want the text from the first part.
            summary = last_message.content[0].get("text", "")
            if logger is not None:
                logger.info(f"Extracted from list content: {summary}")
        else:
            # Fallback for standard string content
            summary = last_message.content
            if logger is not None:
                logger.info(f"Using string content: {summary}")
        
        # Try to extract structured data from messages
        # IMPORTANT: Only check messages from the CURRENT query, not previous queries
        # Find the index of the last HumanMessage (current query)
        messages = response["messages"]
        last_human_message_idx = None
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                last_human_message_idx = i
                break
        
        # Only process messages after the last HumanMessage (current query cycle)
        current_query_messages = messages[last_human_message_idx + 1:] if last_human_message_idx is not None else messages
        
        if logger is not None:
            logger.info(f"Attempting to extract structured data from {len(current_query_messages)} messages in current query...")
        
        # First, try to parse database results from AI messages (in reverse order of current query)
        # Look for structured data (list of tuples/lists) - these are typically database query results
        for i, message in enumerate(reversed(current_query_messages)):
            if isinstance(message, AIMessage) and message.content:
                if logger is not None:
                    logger.info(f"Checking AI message {i} from current query: {message.content}")
                try:
                    content_str = str(message.content)
                    if logger is not None:
                        logger.info(f"Content string: {content_str}")
                    # Look for structured data pattern: list of tuples/lists (database results)
                    if content_str.startswith('[') and content_str.endswith(']'):
                        if logger is not None:
                            logger.info("Found list-like content, attempting to parse...")
                        data = ast.literal_eval(content_str)
                        if logger is not None:
                            logger.info(f"Parsed data: {data}, type: {type(data)}")
                        # Verify this is structured data (list of tuples/lists), not just a simple list
                        if data and len(data) > 0 and isinstance(data, list):
                            # Check if first element is a tuple/list (database row format)
                            if isinstance(data[0], (list, tuple)):
                                structured_data = data
                                # Generate summary if not already extracted
                                if not summary or not summary.strip():
                                    summary = self._generate_summary_from_data(data, user_question)
                                if logger is not None:
                                    logger.info(f"✅ Extracted structured data: {len(data)} rows")
                                break
                            else:
                                # Simple list (not structured data), skip
                                if logger is not None:
                                    logger.info(f"Skipping simple list (not structured data)")
                except Exception as e:
                    if logger is not None:
                        logger.info(f"Failed to parse message {i}: {e}")
                    continue
        
        # If still no structured data, try tool messages from current query
        # Note: Tool results are returned as AIMessage objects (not ToolMessage) in LangGraph
        if structured_data is None:
            for message in reversed(current_query_messages):
                # Check if this is a tool result message (AIMessage with tool result content)
                # Tool results are wrapped as AIMessage objects with content as string representation
                if isinstance(message, AIMessage) and message.content:
                    content_str = str(message.content)
                    # Check if content looks like structured data (list of tuples/lists)
                    if content_str.startswith('[') and content_str.endswith(']'):
                        try:
                            data = ast.literal_eval(content_str)
                            if data and len(data) > 0 and isinstance(data, list):
                                # Verify this looks like database results (list of tuples/lists)
                                if isinstance(data[0], (list, tuple)):
                                    structured_data = data
                                    # Generate summary if not already extracted
                                    if not summary or not summary.strip():
                                        summary = self._generate_summary_from_data(data, user_question)
                                    if logger is not None:
                                        logger.info(f"✅ Extracted structured data from tool result message: {len(data)} rows")
                                    break
                        except Exception as e:
                            if logger is not None:
                                logger.info(f"Failed to parse tool result message content: {e}")
                            continue
                
                # Also check for actual ToolMessage objects (if LangGraph uses them)
                if hasattr(message, 'type') and hasattr(message, 'name'):
                    if message.type == 'tool' and 'sql_db_query' in str(message.name):
                        try:
                            content_str = str(message.content)
                            if content_str.startswith('[') and content_str.endswith(']'):
                                data = ast.literal_eval(content_str)
                                if data and len(data) > 0 and isinstance(data, list):
                                    structured_data = data
                                    # Generate summary if not already extracted
                                    if not summary or not summary.strip():
                                        summary = self._generate_summary_from_data(data, user_question)
                                    if logger is not None:
                                        logger.info(f"✅ Extracted structured data from ToolMessage: {len(data)} rows")
                                    break
                        except Exception as e:
                            if logger is not None:
                                logger.info(f"Failed to parse ToolMessage: {e}")
                            continue
        
        # Determine if table should be shown
        is_table_candidate = self._should_show_table(structured_data, summary, user_question)
        
        # Extract SQL query for column name inference
        sql_query = self._extract_sql_query_from_messages(current_query_messages, logger)
        
        # Convert structured data to DataFrame if applicable
        dataframe = None
        if structured_data and is_table_candidate:
            try:
                dataframe = self._convert_to_dataframe(structured_data, user_question, sql_query, current_query_messages)
            except Exception as e:
                if logger is not None:
                    logger.info(f"Failed to convert to DataFrame: {e}")
                dataframe = None
        
        # Ensure we have at least a summary
        if not summary or not summary.strip():
            if structured_data:
                summary = self._generate_summary_from_data(structured_data, user_question)
            else:
                summary = "I processed your request but couldn't generate a clear response."
        
        return {
            'summary': summary,
            'structured_data': structured_data,
            'dataframe': dataframe,
            'is_table_candidate': is_table_candidate
        }
    
    def _should_show_table(self, structured_data: Optional[List[List]], summary: str, user_question: str) -> bool:
        """
        Determine if response should display a table.
        
        Show table when:
        - Multiple rows exist
        - Multiple columns exist (even with single row)
        - Query type suggests tabular data (list, compare, statistics)
        
        Don't show table when:
        - Single value response
        - Narrative/explanatory response
        - No structured data available
        """
        if not structured_data:
            return False
        
        # Single value - no table
        if len(structured_data) == 1 and len(structured_data[0]) == 1:
            return False
        
        # Multiple rows - show table
        if len(structured_data) > 1:
            return True
        
        # Single row, multiple columns - show table if more than 2 columns
        if len(structured_data) == 1 and len(structured_data[0]) > 2:
            return True
        
        # Check query type for table preference
        question_lower = user_question.lower()
        table_keywords = ['list', 'show', 'display', 'compare', 'statistics', 'stats', 'ranking', 'rankings', 'table']
        if any(keyword in question_lower for keyword in table_keywords):
            return True
        
        return False
    
    def _generate_summary_from_data(self, data: List[List], user_question: str) -> str:
        """Generate a concise summary sentence from structured data."""
        if not data:
            return "No results found."
        
        num_rows = len(data)
        
        # Single value
        if num_rows == 1 and len(data[0]) == 1:
            return f"The answer is: {data[0][0]}"
        
        # Single row, multiple columns
        if num_rows == 1:
            return self.data_formatter.format_with_context(data, user_question)
        
        # Multiple rows
        return f"Found {num_rows} result(s) matching your query."
    
    def _convert_to_dataframe(self, structured_data: List[List], user_question: str, 
                             sql_query: Optional[str] = None, messages: Optional[List] = None) -> pd.DataFrame:
        """
        Convert structured data (list of lists) to pandas DataFrame.
        Uses adaptive column name inference from SQL query, data patterns, and query context.
        
        Args:
            structured_data: List of lists representing rows
            user_question: User's question for context
            sql_query: SQL query string (if available)
            messages: Message list for additional context
        """
        if not structured_data:
            return pd.DataFrame()
        
        num_cols = len(structured_data[0]) if structured_data else 0
        if num_cols == 0:
            return pd.DataFrame()
        
        # Try to infer column names using adaptive multi-layer approach
        column_names = self._infer_column_names(structured_data, num_cols, user_question, sql_query, messages)
        
        # Create DataFrame
        df = pd.DataFrame(structured_data, columns=column_names)
        
        return df
    
    def _extract_sql_query_from_messages(self, messages: List, logger) -> Optional[str]:
        """
        Extract SQL query from agent response messages.
        Looks for SQL queries in tool calls and message content.
        
        Args:
            messages: List of messages from current query
            logger: Logger instance
            
        Returns:
            SQL query string or None if not found
        """
        
        for message in reversed(messages):
            # Check tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.get('name') in ['sql_db_query', 'sql_db_query_checker']:
                        args = tool_call.get('args', {})
                        query = args.get('query', '')
                        if query:
                            return query
            
            # Check message content for SQL code blocks
            if hasattr(message, 'content') and message.content:
                content_str = str(message.content)
                
                # Look for SQL code blocks
                sql_pattern = r'```sqlite?\s*\n?(.*?)```'
                matches = re.findall(sql_pattern, content_str, re.DOTALL | re.IGNORECASE)
                if matches:
                    return matches[0].strip()
                
                # Look for SELECT statements in content
                if 'SELECT' in content_str.upper():
                    # Try to extract SQL query
                    lines = content_str.split('\n')
                    sql_lines = []
                    in_sql = False
                    for line in lines:
                        if 'SELECT' in line.upper():
                            in_sql = True
                            sql_lines.append(line)
                        elif in_sql:
                            sql_lines.append(line)
                            # Stop at common SQL terminators
                            if any(term in line.upper() for term in ['```', 'UNION', 'WHERE', 'FROM', 'ORDER', 'GROUP', 'LIMIT']):
                                break
                    if sql_lines:
                        return ' '.join(sql_lines).strip()
        
        return None
    
    def _parse_sql_column_names(self, sql_query: str, num_cols: int) -> Optional[List[str]]:
        """
        Parse column names from SQL SELECT statement.
        
        Args:
            sql_query: SQL query string
            num_cols: Expected number of columns
            
        Returns:
            List of column names or None if parsing fails
        """
        
        if not sql_query:
            return None
        
        try:
            # Normalize SQL query
            sql_query = sql_query.strip()
            
            # Handle UNION queries - take first SELECT clause
            if 'UNION' in sql_query.upper():
                sql_query = sql_query.split('UNION')[0]
            
            # Extract SELECT clause
            select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE | re.DOTALL)
            if not select_match:
                return None
            
            select_clause = select_match.group(1).strip()
            
            # Split by comma, handling nested functions and subqueries
            columns = []
            current_col = ""
            paren_depth = 0
            
            for char in select_clause:
                if char == '(':
                    paren_depth += 1
                    current_col += char
                elif char == ')':
                    paren_depth -= 1
                    current_col += char
                elif char == ',' and paren_depth == 0:
                    if current_col.strip():
                        columns.append(current_col.strip())
                    current_col = ""
                else:
                    current_col += char
            
            # Add last column
            if current_col.strip():
                columns.append(current_col.strip())
            
            # Clean and extract column names
            column_names = []
            for col in columns:
                col = col.strip()
                
                # Handle AS aliases
                if ' AS ' in col.upper():
                    alias = col.split(' AS ')[-1].strip()
                    column_names.append(self._clean_column_name(alias))
                # Handle aliases with quotes
                elif re.search(r'\s+["\']?(\w+)["\']?\s*$', col):
                    match = re.search(r'\s+["\']?(\w+)["\']?\s*$', col)
                    column_names.append(self._clean_column_name(match.group(1)))
                # Handle aggregate functions
                elif re.match(r'\w+\(.*?\)', col, re.IGNORECASE):
                    func_match = re.match(r'(\w+)\(.*?\)', col, re.IGNORECASE)
                    func_name = func_match.group(1).lower()
                    if func_name in ['count', 'sum', 'avg', 'min', 'max']:
                        # Try to extract column name from function
                        inner_match = re.search(r'\(["\']?(\w+)["\']?\)', col, re.IGNORECASE)
                        if inner_match:
                            column_names.append(f"{func_name.title()}({self._clean_column_name(inner_match.group(1))})")
                        else:
                            column_names.append(f"{func_name.title()}")
                    else:
                        column_names.append(self._clean_column_name(col))
                # Handle simple column names
                else:
                    # Remove quotes and get column name
                    clean_name = re.sub(r'["\']', '', col)
                    # Handle table.column format
                    if '.' in clean_name:
                        clean_name = clean_name.split('.')[-1]
                    column_names.append(self._clean_column_name(clean_name))
            
            # Ensure we have the right number of columns
            if len(column_names) == num_cols:
                return column_names
            elif len(column_names) > num_cols:
                return column_names[:num_cols]
            else:
                # Pad with generic names if needed
                while len(column_names) < num_cols:
                    column_names.append(f"Column_{len(column_names) + 1}")
                return column_names
                
        except Exception as e:
            return None
    
    def _clean_column_name(self, name: str) -> str:
        """Clean and format column name for display."""
        
        # Remove quotes and whitespace
        name = re.sub(r'["\']', '', name).strip()
        
        # Handle snake_case to Title Case
        if '_' in name:
            parts = name.split('_')
            name = ' '.join(word.capitalize() for word in parts)
        else:
            # Capitalize first letter
            name = name.capitalize()
        
        return name
    
    def _analyze_data_patterns(self, structured_data: List[List], num_cols: int) -> Optional[List[str]]:
        """
        Analyze data patterns to infer column names from actual data values.
        
        Args:
            structured_data: List of lists representing rows
            num_cols: Number of columns
            
        Returns:
            List of inferred column names or None
        """
        if not structured_data or len(structured_data) == 0:
            return None
        
        column_names = []
        
        for col_idx in range(num_cols):
            # Collect all values in this column
            column_values = [str(row[col_idx]).strip() for row in structured_data if len(row) > col_idx]
            
            if not column_values:
                column_names.append(f"Column_{col_idx + 1}")
                continue
            
            # Analyze patterns
            first_value = column_values[0] if column_values else ""
            
            # Check for player names (common tennis data)
            if self._looks_like_player_name(first_value):
                if any('winner' in str(v).lower() for v in column_values[:3]):
                    column_names.append('Winner')
                elif any('loser' in str(v).lower() for v in column_values[:3]):
                    column_names.append('Loser')
                else:
                    column_names.append('Player')
            
            # Check for years
            elif self._looks_like_year(first_value):
                column_names.append('Year')
            
            # Check for scores
            elif self._looks_like_score(first_value):
                column_names.append('Score')
            
            # Check for numeric data
            elif self._is_numeric(first_value):
                # Check if it's a ranking
                if self._could_be_ranking(column_values):
                    column_names.append('Rank')
                # Check if it's a count
                elif self._could_be_count(column_values):
                    column_names.append('Count')
                else:
                    column_names.append('Value')
            
            # Check for tournament names
            elif self._looks_like_tournament(first_value):
                column_names.append('Tournament')
            
            # Check for surface types
            elif self._looks_like_surface(first_value):
                column_names.append('Surface')
            
            # Default
            else:
                column_names.append(f"Column_{col_idx + 1}")
        
        return column_names if len(column_names) == num_cols else None
    
    def _looks_like_player_name(self, value: str) -> bool:
        """Check if value looks like a player name."""
        if not value or len(value) < 2:
            return False
        # Player names typically have 2+ words or are capitalized
        words = value.split()
        return len(words) >= 1 and value[0].isupper()
    
    def _looks_like_year(self, value: str) -> bool:
        """Check if value looks like a year."""
        try:
            year = int(value)
            return 1900 <= year <= 2100
        except:
            return False
    
    def _looks_like_score(self, value: str) -> bool:
        """Check if value looks like a tennis score."""
        if not value:
            return False
        # Scores typically contain digits, dashes, or spaces
        return bool(re.search(r'\d', value)) and ('-' in value or ' ' in value or '/' in value)
    
    def _is_numeric(self, value: str) -> bool:
        """Check if value is numeric."""
        try:
            float(value)
            return True
        except:
            return False
    
    def _could_be_ranking(self, values: List[str]) -> bool:
        """Check if values could be rankings."""
        try:
            nums = [int(v) for v in values[:10] if self._is_numeric(v)]
            if not nums:
                return False
            # Rankings are typically small positive integers
            return all(1 <= n <= 1000 for n in nums)
        except:
            return False
    
    def _could_be_count(self, values: List[str]) -> bool:
        """Check if values could be counts."""
        try:
            nums = [int(v) for v in values[:10] if self._is_numeric(v)]
            if not nums:
                return False
            # Counts are typically small positive integers
            return all(0 <= n <= 10000 for n in nums)
        except:
            return False
    
    def _looks_like_tournament(self, value: str) -> bool:
        """Check if value looks like a tournament name."""
        tournament_keywords = ['wimbledon', 'open', 'masters', 'cup', 'championship', 'tournament']
        return any(keyword in value.lower() for keyword in tournament_keywords)
    
    def _looks_like_surface(self, value: str) -> bool:
        """Check if value looks like a surface type."""
        surface_types = ['hard', 'clay', 'grass', 'carpet']
        return value.lower() in surface_types
    
    def _infer_column_names(self, structured_data: List[List], num_cols: int, user_question: str,
                           sql_query: Optional[str] = None, messages: Optional[List] = None) -> List[str]:
        """
        Adaptive column name inference using multi-layer approach:
        1. Parse SQL SELECT clause (most reliable)
        2. Analyze data patterns (adaptive)
        3. Use query context (fallback)
        
        Args:
            structured_data: List of lists representing rows
            num_cols: Number of columns
            user_question: User's question for context
            sql_query: SQL query string (if available)
            messages: Message list for additional context
            
        Returns:
            List of column names
        """
        # Layer 1: Extract column names from SQL SELECT clause (most reliable)
        if sql_query:
            sql_columns = self._parse_sql_column_names(sql_query, num_cols)
            if sql_columns and len(sql_columns) == num_cols:
                return sql_columns
        
        # Layer 2: Analyze data patterns (adaptive)
        data_columns = self._analyze_data_patterns(structured_data, num_cols)
        if data_columns and len(data_columns) == num_cols:
            return data_columns
        
        # Layer 3: Use query context (fallback to current hardcoded approach)
        return self._infer_from_query_context(num_cols, user_question)
    
    def _infer_from_query_context(self, num_cols: int, user_question: str) -> List[str]:
        """
        Infer column names from query context (fallback method).
        This is the original hardcoded approach, kept as fallback.
        """
        question_lower = user_question.lower()
        
        if num_cols == 1:
            if 'who won' in question_lower or 'winner' in question_lower:
                return ['Winner']
            elif 'player' in question_lower:
                return ['Player']
            else:
                return ['Result']
        
        elif num_cols == 2:
            if 'compare' in question_lower or 'vs' in question_lower or 'head' in question_lower:
                return ['Player', 'Wins']
            elif 'ranking' in question_lower or 'rank' in question_lower:
                return ['Player', 'Rank']
            else:
                return ['Column_1', 'Column_2']
        
        elif num_cols == 3:
            if 'match' in question_lower or 'beat' in question_lower or 'defeat' in question_lower:
                return ['Winner', 'Loser', 'Score']
            else:
                return ['Column_1', 'Column_2', 'Column_3']
        
        elif num_cols >= 4:
            column_names = []
            for i in range(num_cols):
                column_names.append(f"Column_{i+1}")
            
            if 'match' in question_lower:
                common_match_cols = ['Year', 'Tournament', 'Winner', 'Loser', 'Score', 'Round', 'Surface']
                if num_cols <= len(common_match_cols):
                    return common_match_cols[:num_cols]
            
            return column_names
        
        return [f"Column_{i+1}" for i in range(num_cols)]
