"""
Response logging utilities for AskTennis AI application.
Handles final response logging functionality.
Extracted from logging_config.py for better modularity.
"""

import logging


class ResponseLogger:
    """
    Centralized response logging class for tennis application.
    Handles final response logging functionality.
    """
    
    def __init__(self):
        """Initialize the response logger."""
        self.logger = logging.getLogger(__name__)
    
    def log_final_response(self, response, processing_time=None):
        """Log the final response to the user."""
        self.logger.info(f"=== FINAL RESPONSE START ===")
        self.logger.info(f"Response: {response}")
        if processing_time:
            self.logger.info(f"Processing Time: {processing_time:.3f} seconds")
        self.logger.info(f"=== FINAL RESPONSE END ===")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
