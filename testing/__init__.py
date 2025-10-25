"""
Automated Testing Framework for AskTennis AI
Provides comprehensive testing capabilities for tennis AI system.
"""

__version__ = "1.0.0"
__author__ = "AskTennis AI Team"

# Import main testing components
from .test_runner import TennisTestRunner
from .test_executor import TestExecutor
from .result_analyzer import ResultAnalyzer
from .database.test_db_manager import TestDatabaseManager

__all__ = [
    'TennisTestRunner',
    'TestExecutor', 
    'ResultAnalyzer',
    'TestDatabaseManager'
]
