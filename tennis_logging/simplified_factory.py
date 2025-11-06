"""
Simplified logging factory for AskTennis AI application.
Replaces complex factory pattern with a simple, direct approach.
"""

from typing import Any, Optional, List, Dict, Tuple
import logging
import os
from .base_logger import BaseLogger
from .setup.logging_setup import LoggingSetup


class SimplifiedLoggingFactory:
    """
    Simplified logging factory that provides all logging functionality.
    Replaces the complex factory pattern with a simple, direct approach.
    """
    
    def __init__(self):
        """Initialize the simplified logging factory."""
        self.base_logger = BaseLogger()
        self.setup = LoggingSetup()
    
    def setup_logging(self) -> Tuple[logging.Logger, str]:
        """Setup comprehensive logging for AI LLM and database interactions.
        
        Returns:
            Tuple of (logger instance, log file path)
        """
        return self.setup.setup_logging()
    
    def log_user_query(self, query: str, session_id: Optional[str] = None, component: Optional[str] = None) -> None:
        """Log the user's input query.
        
        Args:
            query: The user's query string
            session_id: Session ID for tracking
            component: Component/module name where logging occurs
        """
        return self.base_logger.log_user_query(query, session_id, component)
    
    def log_llm_interaction(self, messages: List[Any], interaction_type: str = "LLM_CALL", component: Optional[str] = None) -> None:
        """Log LLM interactions and responses.
        
        Args:
            messages: List of messages in the interaction
            interaction_type: Type of interaction
            component: Component/module name where logging occurs
        """
        return self.base_logger.log_llm_interaction(messages, interaction_type, component)
    
    def log_database_query(self, sql_query: str, results: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None:
        """Log database queries and results.
        
        Args:
            sql_query: The SQL query string
            results: Query results
            execution_time: Execution time in seconds
            component: Component/module name where logging occurs
        """
        return self.base_logger.log_database_query(sql_query, results, execution_time, component)
    
    def log_tool_usage(self, tool_name: str, tool_input: Any, tool_output: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None:
        """Log tool usage and results.
        
        Args:
            tool_name: Name of the tool being used
            tool_input: Input to the tool
            tool_output: Output from the tool
            execution_time: Execution time in seconds
            component: Component/module name where logging occurs
        """
        return self.base_logger.log_tool_usage(tool_name, tool_input, tool_output, execution_time, component)
    
    def log_final_response(self, response: str, processing_time: Optional[float] = None, component: Optional[str] = None) -> None:
        """Log the final response to the user.
        
        Args:
            response: The final response text
            processing_time: Total processing time in seconds
            component: Component/module name where logging occurs
        """
        return self.base_logger.log_final_response(response, processing_time, component)
    
    def log_error(self, error: Exception, context: str = "", component: Optional[str] = None) -> None:
        """Log errors with context.
        
        Args:
            error: The exception that was raised
            context: Additional context about where/why the error occurred
            component: Component/module name where logging occurs
        """
        return self.base_logger.log_error(error, context, component)
    
    def log_agent_response_parsing(self, step: str, message_type: Optional[str] = None, content_preview: Optional[str] = None, details: Optional[Dict[str, Any]] = None, component: Optional[str] = None) -> None:
        """Log agent response parsing steps.
        
        Args:
            step: The parsing step
            message_type: Type of message being parsed
            content_preview: Preview of content (limited to 200 chars)
            details: Additional details dict
            component: Component/module name where logging occurs
        """
        return self.base_logger.log_agent_response_parsing(step, message_type, content_preview, details, component)


# Create global factory instance
_simplified_factory = SimplifiedLoggingFactory()

# Main functions for backward compatibility
def setup_logging() -> Tuple[logging.Logger, str]:
    """Setup comprehensive logging for AI LLM and database interactions.
    
    Returns:
        Tuple of (logger instance, log file path)
    """
    return _simplified_factory.setup_logging()

def log_user_query(query: str, session_id: Optional[str] = None, component: Optional[str] = None) -> None:
    """Log the user's input query.
    
    Args:
        query: The user's query string
        session_id: Session ID for tracking
        component: Component/module name where logging occurs
    """
    return _simplified_factory.log_user_query(query, session_id, component)

def log_llm_interaction(messages: List[Any], interaction_type: str = "LLM_CALL", component: Optional[str] = None) -> None:
    """Log LLM interactions and responses.
    
    Args:
        messages: List of messages in the interaction
        interaction_type: Type of interaction
        component: Component/module name where logging occurs
    """
    return _simplified_factory.log_llm_interaction(messages, interaction_type, component)

def log_database_query(sql_query: str, results: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None:
    """Log database queries and results.
    
    Args:
        sql_query: The SQL query string
        results: Query results
        execution_time: Execution time in seconds
        component: Component/module name where logging occurs
    """
    return _simplified_factory.log_database_query(sql_query, results, execution_time, component)

def log_tool_usage(tool_name: str, tool_input: Any, tool_output: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None:
    """Log tool usage and results.
    
    Args:
        tool_name: Name of the tool being used
        tool_input: Input to the tool
        tool_output: Output from the tool
        execution_time: Execution time in seconds
        component: Component/module name where logging occurs
    """
    return _simplified_factory.log_tool_usage(tool_name, tool_input, tool_output, execution_time, component)

def log_final_response(response: str, processing_time: Optional[float] = None, component: Optional[str] = None) -> None:
    """Log the final response to the user.
    
    Args:
        response: The final response text
        processing_time: Total processing time in seconds
        component: Component/module name where logging occurs
    """
    return _simplified_factory.log_final_response(response, processing_time, component)

def log_error(error: Exception, context: str = "", component: Optional[str] = None) -> None:
    """Log errors with context.
    
    Args:
        error: The exception that was raised
        context: Additional context about where/why the error occurred
        component: Component/module name where logging occurs
    """
    return _simplified_factory.log_error(error, context, component)

def log_agent_response_parsing(step: str, message_type: Optional[str] = None, content_preview: Optional[str] = None, details: Optional[Dict[str, Any]] = None, component: Optional[str] = None) -> None:
    """Log agent response parsing steps.
    
    Args:
        step: The parsing step
        message_type: Type of message being parsed
        content_preview: Preview of content (limited to 200 chars)
        details: Additional details dict
        component: Component/module name where logging occurs
    """
    return _simplified_factory.log_agent_response_parsing(step, message_type, content_preview, details, component)

def get_session_id() -> str:
    """Get the current session ID from logging setup.
    
    Returns:
        The session ID (8-character UUID)
    """
    return _simplified_factory.setup.get_session_id()

def is_logging_enabled() -> bool:
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
