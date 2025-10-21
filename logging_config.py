"""
Logging configuration and utilities for AskTennis AI application.
Handles comprehensive logging for AI LLM and database interactions.
"""

import logging
import os
import uuid
from datetime import datetime
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage


def setup_logging():
    """Setup comprehensive logging for AI LLM and database interactions."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Use session state to maintain consistent logging across reruns
    if 'tennis_logger_session_id' not in st.session_state:
        st.session_state.tennis_logger_session_id = str(uuid.uuid4())[:8]
        st.session_state.tennis_logger_initialized = False
    
    session_id = st.session_state.tennis_logger_session_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/asktennis_ai_interaction_{timestamp}_{session_id}.log"
    
    # Only configure logging once per session
    if not st.session_state.tennis_logger_initialized:
        # Clear any existing handlers to avoid duplicates
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8')
                # Removed StreamHandler to prevent terminal printing
            ],
            force=True  # Force reconfiguration
        )
        
        st.session_state.tennis_logger_initialized = True
        st.session_state.tennis_log_file = log_filename
    
    return logging.getLogger(__name__), st.session_state.tennis_log_file


def log_user_query(query, session_id=None):
    """Log the user's input query."""
    logger = logging.getLogger(__name__)
    logger.info(f"=== USER QUERY START ===")
    logger.info(f"Query: {query}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    if session_id:
        logger.info(f"Session ID: {session_id}")
    logger.info(f"=== USER QUERY END ===")


def log_llm_interaction(messages, interaction_type="LLM_CALL"):
    """Log LLM interactions and responses."""
    logger = logging.getLogger(__name__)
    logger.info(f"=== {interaction_type} START ===")
    for i, message in enumerate(messages):
        if isinstance(message, HumanMessage):
            logger.info(f"Human Message {i+1}: {message.content}")
        elif isinstance(message, AIMessage):
            logger.info(f"AI Message {i+1}: {message.content}")
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info(f"Tool Calls: {[tool_call for tool_call in message.tool_calls]}")
        else:
            logger.info(f"Message {i+1} ({type(message).__name__}): {message.content}")
    logger.info(f"=== {interaction_type} END ===")


def log_database_query(sql_query, results, execution_time=None):
    """Log database queries and results."""
    logger = logging.getLogger(__name__)
    logger.info(f"=== DATABASE QUERY START ===")
    logger.info(f"SQL Query: {sql_query}")
    if execution_time:
        logger.info(f"Execution Time: {execution_time:.3f} seconds")
    logger.info(f"Results Count: {len(results) if results else 0}")
    if results and len(results) > 0:
        logger.info(f"Sample Results: {results[:3]}")  # Log first 3 results
    logger.info(f"=== DATABASE QUERY END ===")


def log_tool_usage(tool_name, tool_input, tool_output, execution_time=None):
    """Log tool usage and results."""
    logger = logging.getLogger(__name__)
    logger.info(f"=== TOOL USAGE START ===")
    logger.info(f"Tool: {tool_name}")
    logger.info(f"Input: {tool_input}")
    logger.info(f"Output: {tool_output}")
    if execution_time:
        logger.info(f"Execution Time: {execution_time:.3f} seconds")
    logger.info(f"=== TOOL USAGE END ===")


def log_final_response(response, processing_time=None):
    """Log the final response to the user."""
    logger = logging.getLogger(__name__)
    logger.info(f"=== FINAL RESPONSE START ===")
    logger.info(f"Response: {response}")
    if processing_time:
        logger.info(f"Total Processing Time: {processing_time:.3f} seconds")
    logger.info(f"=== FINAL RESPONSE END ===")


def log_error(error, context=""):
    """Log errors with context."""
    logger = logging.getLogger(__name__)
    logger.error(f"=== ERROR START ===")
    logger.error(f"Context: {context}")
    logger.error(f"Error: {str(error)}")
    logger.error(f"=== ERROR END ===")
