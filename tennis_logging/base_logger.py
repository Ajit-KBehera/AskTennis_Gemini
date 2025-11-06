"""
Base logging class for AskTennis AI application.
Consolidates all logging handlers into a single, configurable class.
"""

import logging
import traceback
import json
import os
from typing import Any, Optional, List, Dict
from datetime import datetime

# Consistent logger name across the application
LOGGER_NAME = "tennis_ai"

# Global logging enable/disable flag
# Reads from LOG_ENABLED environment variable or defaults to True
# Set LOG_ENABLED=false to disable all logging
def _is_logging_enabled() -> bool:
    """Check if logging is globally enabled.
    
    Returns:
        True if logging is enabled, False otherwise
    """
    log_enabled_env = os.getenv('LOG_ENABLED', '').lower()
    # If explicitly set to 'false', '0', or 'no', disable logging
    if log_enabled_env in ('false', '0', 'no', 'off'):
        return False
    # Default to enabled if not set or set to 'true', '1', 'yes', 'on'
    return True


class BaseLogger:
    """
    Unified logging class that handles all logging types.
    Replaces individual handler classes with a single, configurable class.
    """
    
    # Class-level flag to check if logging is enabled
    _logging_enabled = None
    
    def __init__(self, logger_name: str = LOGGER_NAME, json_format: Optional[bool] = None):
        """Initialize the base logger.
        
        Args:
            logger_name: Name for the logger instance (defaults to LOGGER_NAME constant)
            json_format: If True, use JSON format for logs. If None, reads from LOG_FORMAT env var.
                       'json' enables JSON, anything else uses text format.
        """
        self.logger = logging.getLogger(logger_name)
        # Determine log format: check parameter, then environment variable, default to text
        if json_format is not None:
            self.json_format = json_format
        else:
            log_format_env = os.getenv('LOG_FORMAT', 'text').lower()
            self.json_format = log_format_env == 'json'
        
        # Cache logging enabled status
        if BaseLogger._logging_enabled is None:
            BaseLogger._logging_enabled = _is_logging_enabled()
    
    def _is_logging_enabled(self) -> bool:
        """Check if logging is enabled.
        
        Returns:
            True if logging is enabled, False otherwise
        """
        return BaseLogger._logging_enabled
    
    def log_user_query(self, query: str, session_id: Optional[str] = None, component: Optional[str] = None) -> None:
        """Log user queries.
        
        Args:
            query: The user's query string
            session_id: Session ID for tracking
            component: Component/module name where logging occurs (e.g., "query_service")
        """
        if not self._is_logging_enabled():
            return
        self._log_section("USER QUERY", {
            "session_id": session_id,
            "query": query,
            "component": component
        })
    
    def log_llm_interaction(self, messages: List[Any], interaction_type: str = "LLM_CALL", component: Optional[str] = None) -> None:
        """Log LLM interactions.
        
        Args:
            messages: List of messages in the interaction
            interaction_type: Type of interaction (e.g., "LLM_CALL", "INITIAL_USER_QUERY")
            component: Component/module name where logging occurs
        """
        if not self._is_logging_enabled():
            return
        self._log_section("LLM INTERACTION", {
            "interaction_type": interaction_type,
            "message_count": len(messages),
            "messages": messages,
            "component": component
        })
    
    def log_database_query(self, sql_query: str, results: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None:
        """Log database queries.
        
        Args:
            sql_query: The SQL query string
            results: Query results
            execution_time: Execution time in seconds
            component: Component/module name where logging occurs
        """
        if not self._is_logging_enabled():
            return
        self._log_section("DATABASE QUERY", {
            "sql_query": sql_query,
            "result_count": len(results) if isinstance(results, list) else "N/A",
            "execution_time": execution_time,
            "results": results,
            "component": component
        })
    
    def log_tool_usage(self, tool_name: str, tool_input: Any, tool_output: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None:
        """Log tool usage.
        
        Args:
            tool_name: Name of the tool being used
            tool_input: Input to the tool
            tool_output: Output from the tool
            execution_time: Execution time in seconds
            component: Component/module name where logging occurs
        """
        if not self._is_logging_enabled():
            return
        self._log_section("TOOL USAGE", {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": tool_output,
            "execution_time": execution_time,
            "component": component
        })
    
    def log_final_response(self, response: str, processing_time: Optional[float] = None, component: Optional[str] = None) -> None:
        """Log final responses.
        
        Args:
            response: The final response text
            processing_time: Total processing time in seconds
            component: Component/module name where logging occurs
        """
        if not self._is_logging_enabled():
            return
        self._log_section("FINAL RESPONSE", {
            "response": response,
            "processing_time": processing_time,
            "component": component
        })
    
    def log_error(self, error: Exception, context: str = "", component: Optional[str] = None) -> None:
        """Log errors with full context and stack trace.
        
        Args:
            error: The exception that was raised
            context: Additional context about where/why the error occurred
            component: Component/module name where logging occurs
        """
        if not self._is_logging_enabled():
            return
        # Extract error details
        error_type = type(error).__name__
        error_message = str(error)
        
        # Extract file location and line number from traceback
        error_file = None
        error_line = None
        error_function = None
        
        if error.__traceback__ is not None:
            tb = error.__traceback__
            # Get the last frame in the traceback (where error occurred)
            while tb.tb_next:
                tb = tb.tb_next
            
            frame = tb.tb_frame
            error_file = frame.f_code.co_filename
            error_line = tb.tb_lineno
            error_function = frame.f_code.co_name
        
        # Get full stack trace
        # Use format_exception to get traceback from exception object
        if error.__traceback__ is not None:
            stack_trace_lines = traceback.format_exception(
                type(error),
                error,
                error.__traceback__
            )
            stack_trace = ''.join(stack_trace_lines)
        else:
            # Fallback if no traceback available
            stack_trace = f"{error_type}: {error_message}\n(No traceback available)"
        
        # Build error data dictionary
        error_data = {
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "component": component
        }
        
        # Add location information if available
        if error_file:
            error_data["error_file"] = error_file
        if error_line:
            error_data["error_line"] = error_line
        if error_function:
            error_data["error_function"] = error_function
        
        # Add stack trace
        error_data["stack_trace"] = stack_trace
        
        # Log with structured format
        self._log_section("ERROR", error_data)
        
        # Also log at ERROR level for proper severity handling
        # This ensures errors are properly filtered by log level
        error_summary = f"{error_type}: {error_message}"
        if context:
            error_summary = f"{error_summary} (Context: {context})"
        
        self.logger.error(error_summary, exc_info=True)
    
    def log_agent_response_parsing(self, step: str, message_type: Optional[str] = None, 
                                  content_preview: Optional[str] = None, 
                                  details: Optional[Dict[str, Any]] = None,
                                  component: Optional[str] = None) -> None:
        """Log agent response parsing steps with structured format.
        
        Args:
            step: The parsing step (e.g., "initial_parse", "list_extraction", "formatting")
            message_type: Type of message being parsed
            content_preview: Preview of content (limited to 200 chars)
            details: Additional details dict
            component: Component/module name where logging occurs
        """
        if not self._is_logging_enabled():
            return
        log_data = {
            "step": step,
            "message_type": message_type,
            "component": component
        }
        
        if content_preview:
            # Limit content preview to avoid log bloat
            log_data["content_preview"] = str(content_preview)[:200]
        
        if details:
            log_data.update(details)
        
        self._log_section("AGENT_RESPONSE_PARSING", log_data)
    
    def _log_section(self, section_name: str, data: Dict[str, Any]) -> None:
        """Log a section with structured data.
        
        Supports both text format (human-readable) and JSON format (machine-parseable).
        Format is determined by the json_format instance variable.
        
        Args:
            section_name: Name of the log section
            data: Dictionary of key-value pairs to log
        """
        if self.json_format:
            # JSON format for structured logging (machine-parseable)
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "section": section_name,
                "data": self._sanitize_for_json(data)
            }
            self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        else:
            # Text format for human-readable logs (backward compatible)
            self.logger.info(f"=== {section_name} START ===")
            for key, value in data.items():
                if value is not None:
                    self.logger.info(f"{key}: {value}")
            self.logger.info(f"=== {section_name} END ===")
    
    def _sanitize_for_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for JSON serialization.
        
        Handles non-serializable objects by converting them to strings.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary suitable for JSON serialization
        """
        sanitized = {}
        for key, value in data.items():
            if value is None:
                continue
            try:
                # Try to serialize the value to check if it's JSON-compatible
                json.dumps(value)
                sanitized[key] = value
            except (TypeError, ValueError):
                # If not JSON-serializable, convert to string
                sanitized[key] = str(value)
        return sanitized
    
    def get_logger(self) -> logging.Logger:
        """Get the logger instance.
        
        Returns:
            The logger instance
        """
        return self.logger
