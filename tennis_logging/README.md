"""
Tennis Logging Module

A comprehensive logging system for the AskTennis AI application.

This module provides:
- Structured logging for user queries, LLM interactions, database queries, tool usage, and errors
- Component tracking for better debugging
- Performance metrics aggregation and analysis
- Log filtering and analysis utilities
- Support for both JSON and text log formats
- Session-based logging with unique session IDs

Quick Start:
    from tennis_logging import setup_logging, log_user_query, log_error
    
    # Initialize logging
    logger, log_file = setup_logging()
    
    # Log a user query
    log_user_query("Who won Wimbledon 2022?", component="query_service")
    
    # Log an error
    try:
        result = risky_operation()
    except Exception as e:
        log_error(e, "Failed to execute operation", component="query_service")

For detailed documentation, see docs/LOGGING_DOCUMENTATION.md
"""

