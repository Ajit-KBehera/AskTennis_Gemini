"""
Logging module for AskTennis AI application.
Now uses simplified logging system with BaseLogger.
"""

from .logging_factory import setup_logging, log_user_query, log_llm_interaction, log_database_query, log_tool_usage, log_final_response, log_error
from .setup.logging_setup import LoggingSetup
from .base_logger import BaseLogger

__all__ = ['setup_logging', 'log_user_query', 'log_llm_interaction', 'log_database_query', 'log_tool_usage', 'log_final_response', 'log_error', 'LoggingSetup', 'BaseLogger']
