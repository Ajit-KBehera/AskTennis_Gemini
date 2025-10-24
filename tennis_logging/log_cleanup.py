"""
Automatic log cleanup integration for AskTennis AI.
Integrates with the existing logging system to automatically manage log files.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from .log_management import LogManager

class AutomaticLogCleanup:
    """Automatic log cleanup that integrates with the logging system."""
    
    def __init__(self, max_sessions=5, max_age_days=7):
        """
        Initialize automatic log cleanup.
        
        Args:
            max_sessions (int): Maximum number of sessions to keep
            max_age_days (int): Maximum age of logs in days
        """
        self.max_sessions = max_sessions
        self.max_age_days = max_age_days
        self.logs_dir = Path("logs")
        self.cleanup_logger = self._setup_cleanup_logger()
        
        # Create log manager
        self.log_manager = LogManager(
            logs_dir=str(self.logs_dir),
            max_sessions=max_sessions,
            max_age_days=max_age_days
        )
    
    def _setup_cleanup_logger(self):
        """Setup logger for cleanup operations."""
        logger = logging.getLogger('automatic_cleanup')
        logger.setLevel(logging.INFO)
        
        # Create handler
        handler = logging.FileHandler(self.logs_dir / 'cleanup.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Disable console output
        logger.propagate = False
        
        return logger
    
    def should_cleanup(self):
        """
        Check if cleanup should be performed.
        
        Returns:
            bool: True if cleanup should be performed
        """
        stats = self.log_manager.get_log_statistics()
        
        # Cleanup if we have more than max_sessions or files are too old
        return (stats['total_sessions'] > self.max_sessions or 
                stats['total_files'] > self.max_sessions * 2)
    
    def perform_cleanup(self):
        """
        Perform automatic cleanup.
        
        Returns:
            dict: Cleanup statistics
        """
        self.cleanup_logger.info("Starting automatic log cleanup")
        
        if not self.should_cleanup():
            self.cleanup_logger.info("No cleanup needed")
            return {'status': 'no_cleanup_needed'}
        
        stats = self.log_manager.cleanup_all()
        self.cleanup_logger.info(f"Automatic cleanup completed: {stats}")
        
        return stats
    
    def get_cleanup_status(self):
        """
        Get current cleanup status.
        
        Returns:
            dict: Current status information
        """
        stats = self.log_manager.get_log_statistics()
        sessions = self.log_manager.list_sessions()
        
        return {
            'current_files': stats['total_files'],
            'current_sessions': stats['total_sessions'],
            'current_size_mb': stats['total_size_mb'],
            'max_sessions': self.max_sessions,
            'max_age_days': self.max_age_days,
            'cleanup_needed': self.should_cleanup(),
            'sessions': sessions
        }

def setup_automatic_cleanup(max_sessions=5, max_age_days=7):
    """
    Setup automatic log cleanup.
    
    Args:
        max_sessions (int): Maximum number of sessions to keep
        max_age_days (int): Maximum age of logs in days
        
    Returns:
        AutomaticLogCleanup: Cleanup instance
    """
    return AutomaticLogCleanup(max_sessions=max_sessions, max_age_days=max_age_days)

def cleanup_logs_on_startup():
    """
    Cleanup logs when the application starts.
    This should be called at the beginning of the application.
    """
    cleanup = setup_automatic_cleanup()
    return cleanup.perform_cleanup()

def cleanup_logs_on_shutdown():
    """
    Cleanup logs when the application shuts down.
    This should be called at the end of the application.
    """
    cleanup = setup_automatic_cleanup()
    return cleanup.perform_cleanup()

def get_log_status():
    """
    Get current log status.
    
    Returns:
        dict: Current log status
    """
    cleanup = setup_automatic_cleanup()
    return cleanup.get_cleanup_status()

if __name__ == "__main__":
    # Test the cleanup system silently
    cleanup = setup_automatic_cleanup()
    status = cleanup.get_cleanup_status()
    
    if status['cleanup_needed']:
        result = cleanup.perform_cleanup()
        # Return result for programmatic use
        exit(0 if result.get('status') != 'error' else 1)
    else:
        # No cleanup needed
        exit(0)
