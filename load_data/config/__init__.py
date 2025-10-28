"""
Configuration package for AskTennis data loading.
Provides centralized configuration management.
"""

from .settings import (
    PROJECT_ROOT,
    DATA_DIRS,
    DB_FILE,
    YEARS,
    LOAD_RECENT_ONLY,
    RECENT_YEARS,
    PROGRESS_UPDATE_INTERVAL,
    PROGRESS_DISPLAY_INTERVAL,
    BATCH_SIZE,
    CHUNK_SIZE,
    CREATE_INDEXES,
    INDEX_BATCH_SIZE,
    VERBOSE_LOGGING,
    LOG_FILE
)

from .paths import DataPaths

__all__ = [
    'PROJECT_ROOT',
    'DATA_DIRS', 
    'DB_FILE',
    'YEARS',
    'LOAD_RECENT_ONLY',
    'RECENT_YEARS',
    'PROGRESS_UPDATE_INTERVAL',
    'PROGRESS_DISPLAY_INTERVAL',
    'BATCH_SIZE',
    'CHUNK_SIZE',
    'CREATE_INDEXES',
    'INDEX_BATCH_SIZE',
    'VERBOSE_LOGGING',
    'LOG_FILE',
    'DataPaths'
]
