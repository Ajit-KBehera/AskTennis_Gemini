"""
Database configuration management for AskTennis AI application.
Handles database connection and query configuration.
"""

from typing import Dict, Any
from constants import DEFAULT_DB_PATH


class DatabaseConfig:
    """
    Configuration class for database connections.
    Handles database path and connection parameters.
    """
    
    def __init__(self):
        """Initialize with default database configuration."""
        self.db_path = DEFAULT_DB_PATH
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration parameters."""
        return {
            "db_path": self.db_path
        }
    
    def validate_config(self) -> bool:
        """Validate that all required database configuration is present."""
        # Basic validation - check if path is set
        return self.db_path is not None and self.db_path.strip() != ""

