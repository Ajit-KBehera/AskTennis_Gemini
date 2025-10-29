"""
Query processing utilities for AskTennis AI application.
Handles query processing, agent interaction, and response handling.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
import ast
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from tennis_logging.logging_factory import log_user_query, log_llm_interaction, log_final_response, log_error
from ui.formatting.consolidated_formatter import ConsolidatedFormatter


class QueryProcessor:
    """
    Centralized query processing class for tennis queries.
    Handles agent interaction, response processing, and error handling.
    """
    
    def __init__(self, data_formatter: ConsolidatedFormatter):
        """
        Initialize the query processor.
        
        Args:
            data_formatter: ConsolidatedFormatter instance for formatting responses
        """
        self.data_formatter = data_formatter
    
    def process_agent_response(self, response: dict, logger, user_question: str = "") -> Dict[str, Any]:
        """
        Process and format the agent's response.
        
        Returns:
            Dictionary with keys: 'text', 'should_display_table', 'data', 'columns'
        """
        # The final answer is in the content of the last AIMessage.
        # Parse Gemini's structured output format
        last_message = response["messages"][-1]
        logger.info(f"Last message type: {type(last_message)}")
        logger.info(f"Last message content: {last_message.content}")
        logger.info(f"Last message content type: {type(last_message.content)}")
        
        final_answer = ""
        raw_data = None
        sql_query = None
        
        # Check if last message is raw data (tuple list) - if so, look for text response in earlier messages
        last_content_str = str(last_message.content) if last_message.content else ""
        is_raw_data = last_content_str.startswith('[') and ('(' in last_content_str and ')' in last_content_str)
        
        if isinstance(last_message.content, list) and last_message.content:
            # For Gemini, content is a list of dicts. We want the text from the first part.
            final_answer = last_message.content[0].get("text", "")
            if logger is not None:
                logger.info(f"Extracted from list content: {final_answer}")
        elif not is_raw_data:
            # Fallback for standard string content (but not raw data)
            final_answer = last_message.content
            if logger is not None:
                logger.info(f"Using string content: {final_answer}")
        else:
            # Last message is raw data, look for text response in earlier messages
            if logger is not None:
                logger.info("Last message is raw data, searching for text response in earlier messages...")
            # Look backwards through messages for a text response
            for message in reversed(response["messages"][:-1]):
                if isinstance(message, AIMessage) and message.content:
                    content_str = str(message.content)
                    # Skip raw data and markdown code blocks
                    if not (content_str.startswith('[') and '(' in content_str) and not content_str.startswith('```'):
                        if isinstance(message.content, list):
                            final_answer = message.content[0].get("text", "")
                        else:
                            final_answer = message.content
                        if final_answer and len(final_answer) > 20:  # Only use if substantial
                            if logger is not None:
                                logger.info(f"Found text response in earlier message: {final_answer[:100]}...")
                            break
        
        # Extract SQL query from tool messages to get column names
        # Only look at messages from the current query (after the last HumanMessage)
        last_human_message_idx = None
        for i, message in enumerate(response["messages"]):
            if isinstance(message, HumanMessage):
                last_human_message_idx = i
        
        # Only process messages from the current query onwards
        current_query_messages = response["messages"][last_human_message_idx+1:] if last_human_message_idx is not None else response["messages"]
        
        # Extract SQL query from the most recent tool call in current query
        for message in reversed(current_query_messages):
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.get('name') == 'sql_db_query':
                        args = tool_call.get('args', {})
                        sql_query = args.get('query', '')
                        if sql_query:
                            break
                if sql_query:
                    break
        
        # Always try to extract raw data from tool messages for better formatting
        # Only look at messages from the current query
        # First, try to parse database results from AI messages (in reverse, most recent first)
        # Use the FIRST valid data result found (most recent)
        for i, message in enumerate(reversed(current_query_messages)):
            if isinstance(message, AIMessage) and message.content:
                if logger is not None:
                    logger.info(f"Checking AI message {i} from current query: {message.content}")
                try:
                    content_str = str(message.content)
                    if logger is not None:
                        logger.info(f"Content string: {content_str}")
                    if content_str.startswith('[') and content_str.endswith(']'):
                        if logger is not None:
                            logger.info("Found list-like content, attempting to parse...")
                        parsed_data = ast.literal_eval(content_str)
                        if logger is not None:
                            logger.info(f"Parsed data: {parsed_data}")
                        if parsed_data and len(parsed_data) > 0:
                            # Use the first (most recent) valid data found
                            raw_data = parsed_data
                            if logger is not None:
                                logger.info(f"✅ Using data from current query message {i}")
                            break
                except Exception as e:
                    if logger is not None:
                        logger.info(f"Failed to parse message {i}: {e}")
                    continue
        
        # If no data found in AI messages, try tool messages (only from current query)
        # Use the MOST RECENT tool result
        if raw_data is None:
            for message in reversed(current_query_messages):
                if hasattr(message, 'type') and message.type == 'tool' and 'sql_db_query' in str(message.name):
                    try:
                        if isinstance(message.content, str) and message.content.startswith('[') and message.content.endswith(']'):
                            parsed_data = ast.literal_eval(message.content)
                            if parsed_data and len(parsed_data) > 0:
                                raw_data = parsed_data
                                if logger is not None:
                                    logger.info("✅ Using data from current query tool message")
                                # Use the first (most recent) valid result
                                break
                    except Exception as e:
                        if logger is not None:
                            logger.info(f"Failed to parse tool message: {e}")
                        continue
        
        # If we have raw data, use format_for_display
        if raw_data:
            formatted_result = self.data_formatter.format_for_display(raw_data, user_question, sql_query)
            # Merge text answer if available (use LLM's formatted answer if it's substantial)
            if final_answer and final_answer.strip():
                # If LLM provided a good summary, use it; otherwise use formatter's text
                if len(final_answer) > 20:  # Use LLM answer if substantial
                    formatted_result['text'] = final_answer
            return formatted_result
        
        # If we have a text answer but no raw data, return text format
        if final_answer and final_answer.strip():
            return {
                'format': 'text',
                'text': final_answer,
                'data': [],
                'columns': []
            }
        
        # If no final answer found, try to extract from tool messages and format properly
        if not final_answer or not final_answer.strip():
            if logger is not None:
                logger.info("No clear final answer found, returning empty response")
            return {
                'format': 'text',
                'text': "No response generated",
                'data': [],
                'columns': []
            }
    
    def _extract_summary_and_notes(self, text: str) -> Dict[str, str]:
        """
        Extract summary and notes from LLM response text.
        Removes bullet point sections as they're redundant with dataframe.
        
        Args:
            text: Full text response from LLM
            
        Returns:
            Dictionary with 'summary' and 'notes' keys
        """
        if not text:
            return {'summary': '', 'notes': ''}
        
        lines = text.split('\n')
        summary_lines = []
        notes_lines = []
        in_bullet_section = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check if this is a bullet point line (starts with *, -, or numbered)
            is_bullet = (stripped.startswith('*') and not stripped.startswith('**') and len(stripped) > 1) or \
                       (stripped.startswith('-') and len(stripped) > 1) or \
                       (stripped and stripped[0].isdigit() and '.' in stripped[:3])
            
            # Check if this is a note line
            is_note = '*note:' in stripped.lower() or 'note:' in stripped.lower()
            
            # Check if this is a markdown table
            is_table = stripped.startswith('|') and '---' not in stripped
            
            # Check if this is a bold header (like "**Roger Federer wins (16):**")
            is_bold_header = stripped.startswith('**') and stripped.endswith('**') and ':' in stripped
            
            # If we hit a markdown table, stop processing
            if is_table:
                break
            
            # If we hit a bold header or bullet point, mark that we're in bullet section
            if (is_bold_header or is_bullet) and not in_bullet_section:
                in_bullet_section = True
                # Don't add bold headers to summary - they're section markers
                continue
            
            # If we're in bullet section
            if in_bullet_section:
                if is_note:
                    # Note found - start collecting notes
                    notes_lines.append(line)
                    # Notes typically come after bullets, so we can continue processing
                elif is_bullet or is_bold_header:
                    # Still in bullet section, skip it
                    continue
                elif stripped:
                    # Non-bullet content after bullets - could be notes
                    if 'note' in stripped.lower():
                        notes_lines.append(line)
                    # Otherwise we've left the bullet section
                    # But don't add non-note content after bullets to summary
            else:
                # Not in bullet section yet
                if is_bullet or is_bold_header:
                    # First bullet/bold header encountered - start skipping
                    in_bullet_section = True
                    continue
                elif is_note:
                    # Note found before bullets
                    notes_lines.append(line)
                else:
                    # Regular text - add to summary
                    summary_lines.append(line)
        
        # Join summary and notes
        summary = '\n'.join(summary_lines).strip()
        notes = '\n'.join(notes_lines).strip()
        
        # Clean up summary - remove empty lines at end
        summary = summary.rstrip()
        
        return {
            'summary': summary,
            'notes': notes
        }
    
    
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
                
                # --- REFINEMENT 3: The stateful graph only needs the new human message. ---
                # It loads the history from memory automatically via the checkpointer.
                response = agent_graph.invoke(
                    {"messages": [HumanMessage(content=user_question)]},
                    config=config
                )
                
                # Log the complete conversation flow
                log_llm_interaction(response["messages"], "COMPLETE_CONVERSATION_FLOW")
                
                # Process the response (now returns structured object)
                response_obj = self.process_agent_response(response, logger, user_question)
                
                # Calculate total processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Extract response components
                final_answer = response_obj.get('text', '')
                format_type = response_obj.get('format', 'text')
                should_display_table = format_type == 'table'
                table_data = response_obj.get('data', [])
                table_columns = response_obj.get('columns', [])
                
                if final_answer and final_answer.strip():
                    # Log successful response
                    log_final_response(final_answer, processing_time)
                    st.success("Here's what I found:")
                    
                    # Display based on format
                    if should_display_table and table_data and len(table_data) > 0:
                        # Display as table with extracted summary and notes
                        try:
                            # Extract summary and notes (excluding bullet points)
                            parsed_content = self._extract_summary_and_notes(final_answer)
                            summary_text = parsed_content['summary']
                            notes_text = parsed_content['notes']
                            
                            # Display summary first (if available)
                            if summary_text and len(summary_text) > 10:
                                st.markdown(summary_text)
                            
                            # Display notes before table (if available)
                            if notes_text and len(notes_text) > 5:
                                st.markdown(notes_text)
                            
                            # Create DataFrame from data
                            if table_columns and len(table_columns) == len(table_data[0]):
                                df = pd.DataFrame(table_data, columns=table_columns)
                            else:
                                # Fallback: use generic column names
                                df = pd.DataFrame(table_data)
                            
                            # Ensure proper types - pandas will handle None correctly:
                            # - None becomes NaN for numeric columns (compatible with PyArrow)
                            # - None stays as None for object columns
                            # DataFrame type inference handles this automatically
            
                            # Display table after summary and notes
                            st.dataframe(df, width='stretch')
                        except Exception as e:
                            # Fallback to text if table creation fails
                            logger.error(f"Error creating table: {e}")
                            st.markdown(final_answer)
                    else:
                        # Display as text (for non-table responses)
                        st.markdown(final_answer)
                else:
                    # Log warning case
                    log_final_response("No clear response generated", processing_time)
                    st.warning("I processed your request but couldn't generate a clear response. Please check the conversation flow below for details.")
                    
                    # Check if this might be a misspelling issue
                    if "no results" in str(final_answer).lower() or "not found" in str(final_answer).lower():
                        st.info("💡 **Tip**: If you didn't find what you're looking for, try checking the spelling of player or tournament names. The system is case-sensitive and requires exact matches.")

            except Exception as e:
                # Log error
                log_error(e, f"Processing user query: {user_question}")
                st.error(f"An error occurred while processing your request: {e}")
