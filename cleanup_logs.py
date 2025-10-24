#!/usr/bin/env python3
"""
Manual log cleanup script for AskTennis AI.
Immediately cleans up logs to keep only the 5 most recent sessions.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from log_management import LogManager

def main():
    """Main cleanup function."""
    # Create log manager with 5 session limit
    log_manager = LogManager(
        logs_dir="logs",
        max_sessions=5,
        max_age_days=7
    )
    
    # Perform cleanup silently
    cleanup_stats = log_manager.cleanup_all()
    
    # Return cleanup results for programmatic use
    return cleanup_stats

if __name__ == "__main__":
    main()
