"""
Main configuration management for AskTennis AI application.
Combines AgentConfig and DatabaseConfig into a unified configuration interface.
"""

from .agent_config import AgentConfig
from .database_config import DatabaseConfig
from typing import Dict, Any


class Config:
    """
    Main configuration class that combines AgentConfig and DatabaseConfig.
    Provides unified access to all application configuration.
    """
    
    def __init__(self):
        """Initialize configuration components."""
        self.agent_config = AgentConfig()
        self.database_config = DatabaseConfig()
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration parameters from AgentConfig."""
        return self.agent_config.get_llm_config()
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration parameters from DatabaseConfig."""
        return self.database_config.get_database_config()
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        agent_valid = self.agent_config.validate_config()
        database_valid = self.database_config.validate_config()
        return agent_valid and database_valid

