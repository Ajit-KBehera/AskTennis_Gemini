"""
Base logging class for AskTennis AI application.
Consolidates all logging handlers into a single, configurable class.
"""

import logging
from typing import Any, Optional, List, Dict
from datetime import datetime


class BaseLogger:
    """
    Unified logging class that handles all logging types.
    Replaces individual handler classes with a single, configurable class.
    """
    
    def __init__(self, logger_name: str = "tennis_ai"):
        """Initialize the base logger."""
        self.logger = logging.getLogger(logger_name)
    
    def log_user_query(self, query: str, session_id: Optional[str] = None):
        """Log user queries."""
        self._log_section("USER QUERY", {
            "session_id": session_id,
            "query": query
        })
    
    def log_llm_interaction(self, messages: List[Any], interaction_type: str = "LLM_CALL"):
        """Log LLM interactions."""
        self._log_section("LLM INTERACTION", {
            "interaction_type": interaction_type,
            "message_count": len(messages),
            "messages": messages
        })
    
    def log_database_query(self, sql_query: str, results: Any, execution_time: Optional[float] = None):
        """Log database queries."""
        self._log_section("DATABASE QUERY", {
            "sql_query": sql_query,
            "result_count": len(results) if isinstance(results, list) else "N/A",
            "execution_time": execution_time,
            "results": results
        })
    
    def log_tool_usage(self, tool_name: str, tool_input: Any, tool_output: Any, execution_time: Optional[float] = None):
        """Log tool usage."""
        self._log_section("TOOL USAGE", {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": tool_output,
            "execution_time": execution_time
        })
    
    def log_final_response(self, response: str, processing_time: Optional[float] = None):
        """Log final responses."""
        self._log_section("FINAL RESPONSE", {
            "response": response,
            "processing_time": processing_time
        })
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context."""
        self._log_section("ERROR", {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        })
    
    def _log_section(self, section_name: str, data: Dict[str, Any]):
        """Log a section with structured data."""
        self.logger.info(f"=== {section_name} START ===")
        for key, value in data.items():
            if value is not None:
                self.logger.info(f"{key}: {value}")
        self.logger.info(f"=== {section_name} END ===")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
