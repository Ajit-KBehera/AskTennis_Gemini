"""
Logging setup utilities for AskTennis AI application.
Handles logging configuration and initialization.
Extracted from logging_config.py for better modularity.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import uuid
from typing import Tuple, Optional
from datetime import datetime
import streamlit as st
from pathlib import Path

# Consistent logger name across the application
LOGGER_NAME = "tennis_ai"


class LoggingSetup:
    """
    Centralized logging setup class for tennis application.
    Handles logging configuration and initialization.
    """
    
    def __init__(self):
        """Initialize the logging setup."""
        pass
    
    def setup_logging(self) -> Tuple[logging.Logger, str]:
        """Setup comprehensive logging for AI LLM and database interactions.
        
        Logging can be enabled/disabled via:
        - Environment variable: LOG_ENABLED ("true", "false", "1", "0", "yes", "no", "on", "off")
        - Defaults to True (enabled) if not set
        
        Log level can be configured via:
        - Environment variable: LOG_LEVEL (e.g., "DEBUG", "INFO", "WARNING", "ERROR")
        - Defaults to INFO if not set
        
        Log format can be configured via:
        - Environment variable: LOG_FORMAT ("json" for JSON format, "text" for text format)
        - Defaults to "text" if not set
        
        Log rotation can be configured via:
        - Environment variable: LOG_MAX_BYTES (max file size in bytes, default: 10485760 = 10MB)
        - Environment variable: LOG_BACKUP_COUNT (number of backup files to keep, default: 5)
        
        Old log cleanup:
        - Environment variable: LOG_MAX_AGE_DAYS (days to keep old logs, default: 30)
        - Automatically cleans up old log files on initialization
        
        Returns:
            Tuple of (logger instance, log file path)
        """
        # Check if logging is globally disabled
        log_enabled_env = os.getenv('LOG_ENABLED', '').lower()
        if log_enabled_env in ('false', '0', 'no', 'off'):
            # Return a dummy logger and empty log file path when logging is disabled
            logger = logging.getLogger(LOGGER_NAME)
            logger.setLevel(logging.CRITICAL)  # Set to highest level to suppress all logs
            return logger, ""
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Clean up old log files if configured
        self._cleanup_old_logs()
        
        # Use session state to maintain consistent logging across reruns
        if 'tennis_logger_session_id' not in st.session_state:
            st.session_state.tennis_logger_session_id = str(uuid.uuid4())[:8]
            st.session_state.tennis_logger_initialized = False
        
        session_id = st.session_state.tennis_logger_session_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/asktennis_ai_interaction_{timestamp}_{session_id}.log"
        
        # Only configure logging once per session
        if not st.session_state.tennis_logger_initialized:
            # Clear any existing handlers to avoid duplicates
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            
            # Get log level from environment variable or default to INFO
            log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
            
            # Map string level to logging constant
            # Supported levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
            numeric_level = getattr(logging, log_level_str, logging.INFO)
            
            # If invalid level provided, default to INFO and log a warning
            if log_level_str not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                numeric_level = logging.INFO
                # Use print since logging isn't configured yet
                print(f"Warning: Invalid LOG_LEVEL '{log_level_str}', defaulting to INFO")
            
            # Get log format from environment variable or default to text
            log_format_str = os.getenv('LOG_FORMAT', 'text').lower()
            
            # Get log rotation settings from environment variables
            max_bytes = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # Default: 10MB
            backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))  # Default: 5 backup files
            
            # Use rotating file handler for log rotation
            handler = RotatingFileHandler(
                log_filename,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            # Configure logging with rotating handler
            logging.basicConfig(
                level=numeric_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[handler],
                force=True  # Force reconfiguration
            )
            
            st.session_state.tennis_logger_initialized = True
            st.session_state.tennis_log_file = log_filename
            st.session_state.tennis_log_level = log_level_str
            st.session_state.tennis_log_format = log_format_str
        
        return logging.getLogger(LOGGER_NAME), st.session_state.tennis_log_file
    
    def _cleanup_old_logs(self) -> None:
        """Clean up old log files based on LOG_MAX_AGE_DAYS configuration.
        
        Removes log files older than the specified number of days.
        Only runs once per session to avoid excessive file system operations.
        """
        # Check if cleanup has already been done this session
        if getattr(st.session_state, 'tennis_logger_cleanup_done', False):
            return
        
        try:
            # Get max age from environment variable (default: 30 days)
            max_age_days = int(os.getenv('LOG_MAX_AGE_DAYS', '30'))
            
            # Calculate cutoff time
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            
            # Find all log files
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return
            
            log_files = list(logs_dir.glob("asktennis_ai_interaction_*.log*"))
            deleted_count = 0
            
            for log_file in log_files:
                try:
                    # Check file modification time
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                        deleted_count += 1
                except (OSError, FileNotFoundError):
                    # Ignore errors for files that may have been deleted
                    continue
            
            # Mark cleanup as done for this session
            st.session_state.tennis_logger_cleanup_done = True
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} old log file(s) (older than {max_age_days} days)")
        
        except Exception as e:
            # Silently fail - don't break logging setup if cleanup fails
            pass
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance.
        
        Returns:
            The logger instance
        """
        return logging.getLogger(LOGGER_NAME)
    
    def get_log_file(self) -> Optional[str]:
        """Get the current log file path.
        
        Returns:
            Path to the current log file, or None if not initialized
        """
        return getattr(st.session_state, 'tennis_log_file', None)
    
    def is_initialized(self) -> bool:
        """Check if logging is initialized.
        
        Returns:
            True if logging is initialized, False otherwise
        """
        return getattr(st.session_state, 'tennis_logger_initialized', False)
    
    def get_session_id(self) -> str:
        """Get the current session ID, creating one if it doesn't exist.
        
        Returns:
            The session ID (8-character UUID)
        """
        if 'tennis_logger_session_id' not in st.session_state:
            st.session_state.tennis_logger_session_id = str(uuid.uuid4())[:8]
        return st.session_state.tennis_logger_session_id
    
    def get_log_level(self) -> str:
        """Get the current log level.
        
        Returns:
            The current log level (e.g., "DEBUG", "INFO", "WARNING", "ERROR")
        """
        return getattr(st.session_state, 'tennis_log_level', os.getenv('LOG_LEVEL', 'INFO').upper())
    
    def get_log_format(self) -> str:
        """Get the current log format.
        
        Returns:
            The current log format ("json" or "text")
        """
        return getattr(st.session_state, 'tennis_log_format', os.getenv('LOG_FORMAT', 'text').lower())