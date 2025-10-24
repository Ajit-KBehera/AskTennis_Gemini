"""
Simplified logging factory for AskTennis AI application.
Replaces complex factory pattern with a simple, direct approach.
"""

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
    
    def setup_logging(self):
        """Setup comprehensive logging for AI LLM and database interactions."""
        return self.setup.setup_logging()
    
    def log_user_query(self, query, session_id=None):
        """Log the user's input query."""
        return self.base_logger.log_user_query(query, session_id)
    
    def log_llm_interaction(self, messages, interaction_type="LLM_CALL"):
        """Log LLM interactions and responses."""
        return self.base_logger.log_llm_interaction(messages, interaction_type)
    
    def log_database_query(self, sql_query, results, execution_time=None):
        """Log database queries and results."""
        return self.base_logger.log_database_query(sql_query, results, execution_time)
    
    def log_tool_usage(self, tool_name, tool_input, tool_output, execution_time=None):
        """Log tool usage and results."""
        return self.base_logger.log_tool_usage(tool_name, tool_input, tool_output, execution_time)
    
    def log_final_response(self, response, processing_time=None):
        """Log the final response to the user."""
        return self.base_logger.log_final_response(response, processing_time)
    
    def log_error(self, error, context=""):
        """Log errors with context."""
        return self.base_logger.log_error(error, context)


# Create global factory instance
_simplified_factory = SimplifiedLoggingFactory()

# Main functions for backward compatibility
def setup_logging():
    """Setup comprehensive logging for AI LLM and database interactions."""
    return _simplified_factory.setup_logging()

def log_user_query(query, session_id=None):
    """Log the user's input query."""
    return _simplified_factory.log_user_query(query, session_id)

def log_llm_interaction(messages, interaction_type="LLM_CALL"):
    """Log LLM interactions and responses."""
    return _simplified_factory.log_llm_interaction(messages, interaction_type)

def log_database_query(sql_query, results, execution_time=None):
    """Log database queries and results."""
    return _simplified_factory.log_database_query(sql_query, results, execution_time)

def log_tool_usage(tool_name, tool_input, tool_output, execution_time=None):
    """Log tool usage and results."""
    return _simplified_factory.log_tool_usage(tool_name, tool_input, tool_output, execution_time)

def log_final_response(response, processing_time=None):
    """Log the final response to the user."""
    return _simplified_factory.log_final_response(response, processing_time)

def log_error(error, context=""):
    """Log errors with context."""
    return _simplified_factory.log_error(error, context)
