"""
Main logging factory for AskTennis AI application.
Orchestrates all logging components to provide comprehensive logging functionality.
Extracted from logging_config.py for better modularity.
"""

from .setup.logging_setup import LoggingSetup
from .handlers.query_logger import QueryLogger
from .handlers.llm_logger import LLMLogger
from .handlers.database_logger import DatabaseLogger
from .handlers.tool_logger import ToolLogger
from .handlers.response_logger import ResponseLogger
from .handlers.error_logger import ErrorLogger


class LoggingFactory:
    """
    Main logging factory class for tennis application.
    Orchestrates all logging components to provide comprehensive logging functionality.
    """
    
    def __init__(self):
        """Initialize the logging factory with all components."""
        # Initialize all logging components
        self.setup = LoggingSetup()
        self.query_logger = QueryLogger()
        self.llm_logger = LLMLogger()
        self.database_logger = DatabaseLogger()
        self.tool_logger = ToolLogger()
        self.response_logger = ResponseLogger()
        self.error_logger = ErrorLogger()
    
    def setup_logging(self):
        """Setup comprehensive logging for AI LLM and database interactions."""
        return self.setup.setup_logging()
    
    def log_user_query(self, query, session_id=None):
        """Log the user's input query."""
        return self.query_logger.log_user_query(query, session_id)
    
    def log_llm_interaction(self, messages, interaction_type="LLM_CALL"):
        """Log LLM interactions and responses."""
        return self.llm_logger.log_llm_interaction(messages, interaction_type)
    
    def log_database_query(self, sql_query, results, execution_time=None):
        """Log database queries and results."""
        return self.database_logger.log_database_query(sql_query, results, execution_time)
    
    def log_tool_usage(self, tool_name, tool_input, tool_output, execution_time=None):
        """Log tool usage and results."""
        return self.tool_logger.log_tool_usage(tool_name, tool_input, tool_output, execution_time)
    
    def log_final_response(self, response, processing_time=None):
        """Log the final response to the user."""
        return self.response_logger.log_final_response(response, processing_time)
    
    def log_error(self, error, context=""):
        """Log errors with context."""
        return self.error_logger.log_error(error, context)
    
    def get_setup(self):
        """Get the logging setup instance."""
        return self.setup
    
    def get_query_logger(self):
        """Get the query logger instance."""
        return self.query_logger
    
    def get_llm_logger(self):
        """Get the LLM logger instance."""
        return self.llm_logger
    
    def get_database_logger(self):
        """Get the database logger instance."""
        return self.database_logger
    
    def get_tool_logger(self):
        """Get the tool logger instance."""
        return self.tool_logger
    
    def get_response_logger(self):
        """Get the response logger instance."""
        return self.response_logger
    
    def get_error_logger(self):
        """Get the error logger instance."""
        return self.error_logger


# Create global factory instance
_logging_factory = LoggingFactory()

# Main functions for backward compatibility
def setup_logging():
    """Setup comprehensive logging for AI LLM and database interactions."""
    return _logging_factory.setup_logging()

def log_user_query(query, session_id=None):
    """Log the user's input query."""
    return _logging_factory.log_user_query(query, session_id)

def log_llm_interaction(messages, interaction_type="LLM_CALL"):
    """Log LLM interactions and responses."""
    return _logging_factory.log_llm_interaction(messages, interaction_type)

def log_database_query(sql_query, results, execution_time=None):
    """Log database queries and results."""
    return _logging_factory.log_database_query(sql_query, results, execution_time)

def log_tool_usage(tool_name, tool_input, tool_output, execution_time=None):
    """Log tool usage and results."""
    return _logging_factory.log_tool_usage(tool_name, tool_input, tool_output, execution_time)

def log_final_response(response, processing_time=None):
    """Log the final response to the user."""
    return _logging_factory.log_final_response(response, processing_time)

def log_error(error, context=""):
    """Log errors with context."""
    return _logging_factory.log_error(error, context)
