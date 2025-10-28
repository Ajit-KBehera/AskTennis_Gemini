"""
Modular data loading system for AskTennis.
Provides organized, maintainable data loading components.

This package contains a complete modular system for loading tennis data:
- Configuration management
- Data loaders for different data types
- Data processors for transformation
- Database operations for storage
- Core orchestration classes
"""

# Import main components for easy access
from .core import DataLoader, ProgressTracker
from .config import DataPaths, YEARS, RECENT_YEARS, LOAD_RECENT_ONLY
from .loaders import PlayersLoader, RankingsLoader, MatchesLoader, DoublesLoader
from .processors import DateProcessor, ScoreProcessor, SurfaceProcessor, LevelProcessor
from .database import DatabaseCreator, DatabaseVerifier, DatabaseManager

__version__ = "1.0.0"
__author__ = "AskTennis AI Team"

__all__ = [
    # Core classes
    'DataLoader',
    'ProgressTracker',
    
    # Configuration
    'DataPaths',
    'YEARS',
    'RECENT_YEARS', 
    'LOAD_RECENT_ONLY',
    
    # Data loaders
    'PlayersLoader',
    'RankingsLoader',
    'MatchesLoader',
    'DoublesLoader',
    
    # Data processors
    'DateProcessor',
    'ScoreProcessor',
    'SurfaceProcessor',
    'LevelProcessor',
    
    # Database operations
    'DatabaseCreator',
    'DatabaseVerifier',
    'DatabaseManager'
]
