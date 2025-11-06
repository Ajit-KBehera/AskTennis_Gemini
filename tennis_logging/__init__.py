"""
Logging module for AskTennis AI application.
Now uses simplified logging system with BaseLogger.
"""

from .simplified_factory import setup_logging, log_user_query, log_llm_interaction, log_database_query, log_tool_usage, log_final_response, log_error, log_agent_response_parsing, get_session_id, is_logging_enabled
from .setup.logging_setup import LoggingSetup
from .base_logger import BaseLogger
from .log_filter import LogFilter
from .performance_metrics import PerformanceMetrics

__all__ = ['setup_logging', 'log_user_query', 'log_llm_interaction', 'log_database_query', 'log_tool_usage', 'log_final_response', 'log_error', 'log_agent_response_parsing', 'get_session_id', 'is_logging_enabled', 'LoggingSetup', 'BaseLogger', 'LogFilter', 'PerformanceMetrics']
