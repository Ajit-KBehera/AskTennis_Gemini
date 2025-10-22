"""
Database logging utilities for AskTennis AI application.
Handles database query logging functionality.
Extracted from logging_config.py for better modularity.
"""

import logging


class DatabaseLogger:
    """
    Centralized database logging class for tennis application.
    Handles database query logging functionality.
    """
    
    def __init__(self):
        """Initialize the database logger."""
        self.logger = logging.getLogger(__name__)
    
    def log_database_query(self, sql_query, results, execution_time=None):
        """Log database queries and results."""
        self.logger.info(f"=== DATABASE QUERY START ===")
        self.logger.info(f"SQL Query: {sql_query}")
        if execution_time:
            self.logger.info(f"Execution Time: {execution_time:.3f} seconds")
        self.logger.info(f"Results Count: {len(results)}")
        if results:
            self.logger.info(f"Sample Results: {results[:3]}")  # Log first 3 results
        self.logger.info(f"=== DATABASE QUERY END ===")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
