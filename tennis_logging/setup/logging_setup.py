"""
Logging setup utilities for AskTennis AI application.
Handles logging configuration and initialization.
Extracted from logging_config.py for better modularity.
"""

import logging
import os
import uuid
from datetime import datetime
import streamlit as st


class LoggingSetup:
    """
    Centralized logging setup class for tennis application.
    Handles logging configuration and initialization.
    """
    
    def __init__(self):
        """Initialize the logging setup."""
        pass
    
    def setup_logging(self):
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
    
    def get_logger(self):
        """Get the configured logger instance."""
        return logging.getLogger(__name__)
    
    def get_log_file(self):
        """Get the current log file path."""
        return getattr(st.session_state, 'tennis_log_file', None)
    
    def is_initialized(self):
        """Check if logging is initialized."""
        return getattr(st.session_state, 'tennis_logger_initialized', False)
