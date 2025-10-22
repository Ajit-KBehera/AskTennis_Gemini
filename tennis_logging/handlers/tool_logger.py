"""
Tool logging utilities for AskTennis AI application.
Handles tool usage logging functionality.
Extracted from logging_config.py for better modularity.
"""

import logging


class ToolLogger:
    """
    Centralized tool logging class for tennis application.
    Handles tool usage logging functionality.
    """
    
    def __init__(self):
        """Initialize the tool logger."""
        self.logger = logging.getLogger(__name__)
    
    def log_tool_usage(self, tool_name, tool_input, tool_output, execution_time=None):
        """Log tool usage and results."""
        self.logger.info(f"=== TOOL USAGE START ===")
        self.logger.info(f"Tool: {tool_name}")
        self.logger.info(f"Input: {tool_input}")
        self.logger.info(f"Output: {tool_output}")
        if execution_time:
            self.logger.info(f"Execution Time: {execution_time:.3f} seconds")
        self.logger.info(f"=== TOOL USAGE END ===")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
