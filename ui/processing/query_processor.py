"""
Query processing utilities for AskTennis AI application.
Handles query processing, agent interaction, and response handling.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
import ast
import json
import os
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from tennis_logging.logging_factory import log_user_query, log_llm_interaction, log_final_response, log_error
from ui.formatting.data_formatter import DataFormatter


class QueryProcessor:
    """
    Centralized query processing class for tennis queries.
    Handles agent interaction, response processing, and error handling.
    """
    
    def __init__(self, data_formatter: DataFormatter):
        """
        Initialize the query processor.
        
        Args:
            data_formatter: DataFormatter instance for formatting responses
        """
        self.data_formatter = data_formatter
    
    def process_agent_response(self, response: dict, logger, user_question: str = "") -> str:
        """Process and format the agent's response."""
        # The final answer is in the content of the last AIMessage.
        # Parse Gemini's structured output format
        last_message = response["messages"][-1]
        logger.info(f"Last message type: {type(last_message)}")
        logger.info(f"Last message content: {last_message.content}")
        logger.info(f"Last message content type: {type(last_message.content)}")
        
        if isinstance(last_message.content, list) and last_message.content:
            # For Gemini, content is a list of dicts. We want the text from the first part.
            final_answer = last_message.content[0].get("text", "")
            if logger is not None:
                logger.info(f"Extracted from list content: {final_answer}")
        else:
            # Fallback for standard string content
            final_answer = last_message.content
            if logger is not None:
                logger.info(f"Using string content: {final_answer}")
        
        # If no final answer found, try to extract from tool messages and format properly
        if not final_answer or not final_answer.strip():
            if logger is not None:
                logger.info("No clear final answer found, attempting to parse database results...")
            # First, try to parse database results from AI messages
            for i, message in enumerate(reversed(response["messages"])):
                if isinstance(message, AIMessage) and message.content:
                    if logger is not None:
                        logger.info(f"Checking AI message {i}: {message.content}")
                    try:
                        content_str = str(message.content)
                        if logger is not None:
                            logger.info(f"Content string: {content_str}")
                        if content_str.startswith('[') and content_str.endswith(']'):
                            if logger is not None:
                                logger.info("Found list-like content, attempting to parse...")
                            data = ast.literal_eval(content_str)
                            if logger is not None:
                                logger.info(f"Parsed data: {data}")
                            if data and len(data) > 0:
                                # Format the result properly based on the query type
                                if len(data) == 1 and len(data[0]) == 1:
                                    # Single result (like winner name)
                                    result = data[0][0]
                                    final_answer = f"The answer is: {result}"
                                    if logger is not None:
                                        logger.info(f"✅ Formatted single result: {final_answer}")
                                elif len(data) == 1 and len(data[0]) > 1:
                                    # Multiple columns, single row - use improved formatting
                                    final_answer = self.data_formatter.format_with_context(data, user_question)
                                    if logger is not None:
                                        logger.info(f"✅ Formatted multi-column result: {final_answer}")
                                else:
                                    # Multiple rows - use improved formatting
                                    final_answer = self.data_formatter.format_with_context(data, user_question)
                                    if logger is not None:
                                        logger.info(f"✅ Formatted multi-row result: {final_answer}")
                                break
                    except Exception as e:
                        if logger is not None:
                            logger.info(f"Failed to parse message {i}: {e}")
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
    
    def log_feedback(self, feedback_type: str, user_question: str, response: str, processing_time: float):
        """
        Log user feedback for ML analytics improvement.
        
        Args:
            feedback_type: 'positive' or 'negative'
            user_question: The original user query
            response: The AI response
            processing_time: Time taken to process the query
        """
        try:
            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback_type,
                "user_question": user_question,
                "response_length": len(response),
                "processing_time": processing_time,
                "session_id": "user_session"  # Could be made dynamic later
            }
            
            # Create feedback directory if it doesn't exist
            feedback_dir = "logs/feedback"
            os.makedirs(feedback_dir, exist_ok=True)
            
            # Log to feedback file
            feedback_file = os.path.join(feedback_dir, f"feedback_{datetime.now().strftime('%Y%m%d')}.jsonl")
            
            # Ensure the file exists and is writable
            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback_data, ensure_ascii=False) + "\n")
                f.flush()  # Ensure data is written immediately
            
            # Also log to console for debugging
            print(f"✅ Feedback logged: {feedback_type} for query: {user_question[:50]}...")
                
        except Exception as e:
            # Don't let feedback logging break the main flow
            print(f"❌ Error logging feedback: {e}")
            import traceback
            traceback.print_exc()
    
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
                
                # Process the response
                final_answer = self.process_agent_response(response, logger, user_question)
                
                # Calculate total processing time
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                if final_answer and final_answer.strip():
                    # Log successful response
                    log_final_response(final_answer, processing_time)
                    st.success("Here's what I found:")
                    st.markdown(final_answer)
                    
                    # Add feedback buttons (only show if not already given feedback for this query)
                    feedback_key = f"feedback_given_{hash(user_question)}"
                    if feedback_key not in st.session_state:
                        st.markdown("---")
                        st.markdown("**Was this response helpful?**")
                        col1, col2, col3 = st.columns([1, 1, 4])
                        
                        with col1:
                            if st.button("👍 Helpful", key=f"positive_{hash(user_question)}"):
                                self.log_feedback("positive", user_question, final_answer, processing_time)
                                st.session_state[feedback_key] = "positive"
                                st.success("Thank you for your feedback! 👍")
                                st.rerun()
                        
                        with col2:
                            if st.button("👎 Not Helpful", key=f"negative_{hash(user_question)}"):
                                self.log_feedback("negative", user_question, final_answer, processing_time)
                                st.session_state[feedback_key] = "negative"
                                st.warning("Thank you for your feedback! 👎")
                                st.rerun()
                    else:
                        # Show feedback confirmation
                        feedback_type = st.session_state[feedback_key]
                        emoji = "👍" if feedback_type == "positive" else "👎"
                        st.markdown("---")
                        st.info(f"Thank you for your feedback! {emoji}")
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
