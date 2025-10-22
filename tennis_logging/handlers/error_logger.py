"""
Error logging utilities for AskTennis AI application.
Handles error logging functionality.
Extracted from logging_config.py for better modularity.
"""

import logging


class ErrorLogger:
    """
    Centralized error logging class for tennis application.
    Handles error logging functionality.
    """
    
    def __init__(self):
        """Initialize the error logger."""
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, error, context=""):
        """Log errors with context."""
        self.logger.error(f"=== ERROR START ===")
        self.logger.error(f"Context: {context}")
        self.logger.error(f"Error: {str(error)}")
        self.logger.error(f"=== ERROR END ===")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
