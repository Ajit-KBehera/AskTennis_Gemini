"""
Query processing utilities for AskTennis AI application.
Handles query processing, agent interaction, and response handling.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
import ast
import pandas as pd
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
        
        # Convert structured data to DataFrame if applicable
        dataframe = None
        if structured_data and is_table_candidate:
            try:
                dataframe = self._convert_to_dataframe(structured_data, user_question)
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
    
    def _convert_to_dataframe(self, structured_data: List[List], user_question: str) -> pd.DataFrame:
        """
        Convert structured data (list of lists) to pandas DataFrame.
        Attempts to infer column names from query context or use generic names.
        """
        if not structured_data:
            return pd.DataFrame()
        
        num_cols = len(structured_data[0]) if structured_data else 0
        if num_cols == 0:
            return pd.DataFrame()
        
        # Try to infer column names based on common patterns
        column_names = self._infer_column_names(structured_data, num_cols, user_question)
        
        # Create DataFrame
        df = pd.DataFrame(structured_data, columns=column_names)
        
        return df
    
    def _infer_column_names(self, structured_data: List[List], num_cols: int, user_question: str) -> List[str]:
        """
        Infer column names from data patterns or query context.
        Returns list of column names.
        """
        # Common column name patterns based on data structure
        if num_cols == 1:
            question_lower = user_question.lower()
            if 'who won' in question_lower or 'winner' in question_lower:
                return ['Winner']
            elif 'player' in question_lower:
                return ['Player']
            else:
                return ['Result']
        
        elif num_cols == 2:
            # Common two-column patterns
            question_lower = user_question.lower()
            if 'compare' in question_lower or 'vs' in question_lower or 'head' in question_lower:
                return ['Player', 'Wins']
            elif 'ranking' in question_lower or 'rank' in question_lower:
                return ['Player', 'Rank']
            else:
                return ['Column_1', 'Column_2']
        
        elif num_cols == 3:
            # Common three-column patterns (winner, loser, score)
            question_lower = user_question.lower()
            if 'match' in question_lower or 'beat' in question_lower or 'defeat' in question_lower:
                return ['Winner', 'Loser', 'Score']
            else:
                return ['Column_1', 'Column_2', 'Column_3']
        
        elif num_cols >= 4:
            # Multi-column patterns - try to infer from first row values
            # Use generic names but could be improved with SQL parsing
            column_names = []
            for i in range(num_cols):
                column_names.append(f"Column_{i+1}")
            
            # Try common patterns based on question
            question_lower = user_question.lower()
            if 'match' in question_lower and num_cols >= 4:
                # Could be: Year, Tournament, Winner, Loser, Score, etc.
                common_match_cols = ['Year', 'Tournament', 'Winner', 'Loser', 'Score', 'Round', 'Surface']
                if num_cols <= len(common_match_cols):
                    return common_match_cols[:num_cols]
            
            return column_names
        
        # Fallback: generic column names
        return [f"Column_{i+1}" for i in range(num_cols)]
