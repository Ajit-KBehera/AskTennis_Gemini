"""
Query logging utilities for AskTennis AI application.
Handles user query logging functionality.
Extracted from logging_config.py for better modularity.
"""

import logging


class QueryLogger:
    """
    Centralized query logging class for tennis application.
    Handles user query logging functionality.
    """
    
    def __init__(self):
        """Initialize the query logger."""
        self.logger = logging.getLogger(__name__)
    
    def log_user_query(self, query, session_id=None):
        """Log the user's input query."""
        self.logger.info(f"=== USER QUERY START ===")
        if session_id:
            self.logger.info(f"Session ID: {session_id}")
        self.logger.info(f"Query: {query}")
        self.logger.info(f"=== USER QUERY END ===")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
