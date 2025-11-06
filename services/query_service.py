"""
Query processing service for AskTennis AI application.
Handles query processing, agent interaction, and response handling.
Moved from ui/processing/ for better architectural separation.
"""

import streamlit as st
import ast
from datetime import datetime
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from tennis_logging.simplified_factory import log_user_query, log_llm_interaction, log_final_response, log_error, log_agent_response_parsing, get_session_id
from utils.formatters import ConsolidatedFormatter
from config.config import Config


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
    
    @staticmethod
    @st.cache_resource
    def _get_summary_llm():
        """
        Get or create a lightweight LLM instance for summary generation.
        Cached to avoid re-initializing on every request.
        
        Returns:
            ChatGoogleGenerativeAI instance configured for summary generation
        """
        config = Config()
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",  # Fast model for quick summaries
            google_api_key=config.api_key,
            temperature=0.3  # Slightly higher temperature for more natural summaries
        )
    
    def _generate_summary(self, response_text: str) -> Optional[str]:
        """
        Generate an intelligent 1-line summary using LLM if response is longer than 5 lines.
        
        Args:
            response_text: The full AI response text
            
        Returns:
            Summary string if response is long enough, None otherwise
        """
        if not response_text or not response_text.strip():
            return None
        
        # Split response into lines (excluding empty lines)
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        
        # Only generate summary if response is longer than 5 lines
        if len(lines) <= 5:
            return None
        
        try:
            # Get cached LLM instance for summary generation
            summary_llm = self._get_summary_llm()
            
            # Create a prompt for summary generation
            # Limit response text to avoid token limits
            limited_text = response_text[:2000]
            summary_prompt = f"""Generate a concise, informative one-line summary (maximum 120 characters) of the following tennis-related response. 
The summary should capture the main point or key information in a single sentence.

Response to summarize:
{limited_text}

Summary (one line, max 120 chars):"""
            
            # Generate summary using LLM
            response = summary_llm.invoke(summary_prompt)
            
            # Extract summary from response
            if hasattr(response, 'content'):
                summary = response.content.strip()
            else:
                summary = str(response).strip()
            
            # Ensure summary is not too long (safety check)
            if len(summary) > 150:
                summary = summary[:147].rsplit(' ', 1)[0] + "..."
            
            # Fallback to simple extraction if LLM fails or returns empty
            if not summary or len(summary) < 10:
                return self._fallback_summary(response_text, lines)
            
            return summary
            
        except Exception as e:
            # Fallback to simple string-based summary if LLM fails
            return self._fallback_summary(response_text, lines)
    
    def _fallback_summary(self, response_text: str, lines: list) -> Optional[str]:
        """
        Fallback method for summary generation using string manipulation.
        Used when LLM summarization fails.
        
        Args:
            response_text: The full AI response text
            lines: List of non-empty lines from the response
            
        Returns:
            Summary string or None
        """
        # Try to extract first meaningful sentence(s)
        sentences = response_text.split('. ')
        
        if len(sentences) >= 2:
            # Take first 1-2 sentences as summary
            summary = '. '.join(sentences[:2])
            if not summary.endswith('.'):
                summary += '.'
            # Ensure it's not too long
            if len(summary) > 150:
                summary = summary[:147].rsplit(' ', 1)[0] + "..."
            return summary.strip()
        elif len(sentences) == 1:
            # Single sentence - take first part if too long
            first_sentence = sentences[0]
            if len(first_sentence) > 150:
                return first_sentence[:147].rsplit(' ', 1)[0] + "..."
            return first_sentence
        
        # Final fallback: take first line
        return lines[0] if lines else None
    
    def handle_user_query(self, user_question: str, agent_graph):
        """Handle user query processing and store results in session state."""
        # Get session ID from session state (set in logging_setup)
        # Use helper function to ensure session ID is always available
        session_id = get_session_id()
        
        # Log the user query with actual session ID
        log_user_query(user_question, session_id, component="query_service")
        
        with st.spinner("The AI is analyzing your question and querying the database..."):
            try:
                start_time = datetime.now()
                
                # The config dictionary ensures each user gets their own conversation history.
                # Use the same session ID for thread_id to maintain conversation context per session
                config = {"configurable": {"thread_id": session_id}}
                
                # Log the initial LLM interaction
                log_llm_interaction([HumanMessage(content=user_question)], "INITIAL_USER_QUERY", component="query_service")
                
                # Only pass the new message - LangGraph's checkpointer automatically loads
                # conversation history from memory based on the thread_id in config
                response = agent_graph.invoke(
                    {"messages": [HumanMessage(content=user_question)]},
                    config=config
                )
                
                # Log the complete conversation flow
                log_llm_interaction(response["messages"], "COMPLETE_CONVERSATION_FLOW", component="query_service")
                
                # Process the response
                final_answer = self.process_agent_response(response, user_question)
                
                # Calculate total processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Generate summary if response is long enough
                summary = self._generate_summary(final_answer) if final_answer else None
                
                # Store response and summary in session state for display
                st.session_state.ai_query_response = final_answer
                st.session_state.ai_query_summary = summary
                
                if final_answer and final_answer.strip():
                    # Log successful response
                    log_final_response(final_answer, processing_time, component="query_service")
                else:
                    # Log warning case
                    log_final_response("No clear response generated", processing_time, component="query_service")

            except Exception as e:
                # Log error
                log_error(e, f"Processing user query: {user_question}", component="query_service")
                st.error(f"An error occurred while processing your request: {e}")
    
    def process_agent_response(self, response: dict, user_question: str = "") -> str:
        """Process and format the agent's response."""
        # The final answer is in the content of the last AIMessage.
        # Parse Gemini's structured output format
        last_message = response["messages"][-1]
        log_agent_response_parsing(
            step="initial_parse",
            message_type=type(last_message).__name__,
            content_preview=str(last_message.content),
            details={"content_type": type(last_message.content).__name__},
            component="query_service"
        )
        
        if isinstance(last_message.content, list) and last_message.content:
            # For Gemini, content is a list of dicts. We want the text from the first part.
            final_answer = last_message.content[0].get("text", "")
            log_agent_response_parsing(
                step="list_extraction",
                message_type="AIMessage",
                content_preview=final_answer,
                details={"extraction_method": "list_content"},
                component="query_service"
            )
        else:
            # Fallback for standard string content
            final_answer = last_message.content
            log_agent_response_parsing(
                step="string_extraction",
                message_type="AIMessage",
                content_preview=final_answer,
                details={"extraction_method": "string_content"},
                component="query_service"
            )
        
        # If no final answer found, try to extract from tool messages and format properly
        if not final_answer or not final_answer.strip():
            log_agent_response_parsing(
                step="fallback_parse_initiated",
                details={"reason": "no_clear_answer_found"},
                component="query_service"
            )
            # First, try to parse database results from AI messages
            for i, message in enumerate(reversed(response["messages"])):
                if isinstance(message, AIMessage) and message.content:
                    log_agent_response_parsing(
                        step="checking_ai_message",
                        message_type="AIMessage",
                        details={"message_index": i, "total_messages": len(response["messages"])},
                        component="query_service"
                    )
                    try:
                        content_str = str(message.content)
                        log_agent_response_parsing(
                            step="content_string_conversion",
                            content_preview=content_str,
                            component="query_service"
                        )
                        if content_str.startswith('[') and content_str.endswith(']'):
                            log_agent_response_parsing(
                                step="list_parsing_attempt",
                                details={"content_format": "list_like"},
                                component="query_service"
                            )
                            data = ast.literal_eval(content_str)
                            log_agent_response_parsing(
                                step="data_parsed",
                                details={
                                    "data_length": len(data) if isinstance(data, list) else "N/A",
                                    "first_row_length": len(data[0]) if isinstance(data, list) and data else "N/A"
                                },
                                component="query_service"
                            )
                            if data and len(data) > 0:
                                # Format the result properly based on the query type
                                if len(data) == 1 and len(data[0]) == 1:
                                    # Single result (like winner name)
                                    result = data[0][0]
                                    final_answer = f"The answer is: {result}"
                                    log_agent_response_parsing(
                                        step="formatting_complete",
                                        details={"format_type": "single_result", "result_preview": str(result)[:100]},
                                        component="query_service"
                                    )
                                elif len(data) == 1 and len(data[0]) > 1:
                                    # Multiple columns, single row - use improved formatting
                                    final_answer = self.data_formatter.format_with_context(data, user_question)
                                    log_agent_response_parsing(
                                        step="formatting_complete",
                                        details={"format_type": "multi_column_single_row"},
                                        component="query_service"
                                    )
                                else:
                                    # Multiple rows - use improved formatting
                                    final_answer = self.data_formatter.format_with_context(data, user_question)
                                    log_agent_response_parsing(
                                        step="formatting_complete",
                                        details={"format_type": "multi_row"},
                                        component="query_service"
                                    )
                                break
                    except Exception as e:
                        log_agent_response_parsing(
                            step="parse_error",
                            details={"error": str(e), "message_index": i},
                            component="query_service"
                        )
                        continue
            
            # If still no answer, try tool messages
            if not final_answer or not final_answer.strip():
                for message in reversed(response["messages"]):
                    if hasattr(message, 'type') and message.type == 'tool' and 'sql_db_query' in str(message.name):
                        try:
                            if message.content.startswith('[') and message.content.endswith(']'):
                                data = ast.literal_eval(message.content)
                                if data and len(data) > 0:
                                    # Format the result properly based on the query type
                                    if len(data) == 1 and len(data[0]) == 1:
                                        # Single result (like winner name)
                                        result = data[0][0]
                                        final_answer = f"The answer is: {result}"
                                    elif len(data) == 1 and len(data[0]) > 1:
                                        # Multiple columns, single row - use improved formatting
                                        final_answer = self.data_formatter.format_with_context(data, user_question)
                                    else:
                                        # Multiple rows - use improved formatting
                                        final_answer = self.data_formatter.format_with_context(data, user_question)
                                    break
                        except:
                            continue
        
        return final_answer

