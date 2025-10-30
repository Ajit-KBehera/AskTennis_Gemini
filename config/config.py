"""
Unified configuration management for AskTennis AI application.
Consolidates all configuration logic into a single class.
"""

import streamlit as st
from typing import Dict, Any
from constants import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_DB_PATH


class Config:
    """
    Unified configuration class for the AskTennis AI application.
    Handles all configuration including LLM settings, API keys, and database paths.
    """
    
    def __init__(self):
        """Initialize with default configuration."""
        # LLM configuration
        self.model_name = DEFAULT_MODEL
        self.temperature = DEFAULT_TEMPERATURE
        self.api_key = self._get_api_key()
        
        # Database configuration
        self.db_path = DEFAULT_DB_PATH
    
    def _get_api_key(self) -> str:
        """Get the Google API key from Streamlit secrets."""
        try:
            return st.secrets["GOOGLE_API_KEY"]
        except (KeyError, FileNotFoundError):
            st.error(
                "Google API key not found! Please create a `.streamlit/secrets.toml` file "
                "and add your GOOGLE_API_KEY."
            )
            st.stop()
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration parameters."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "api_key": self.api_key
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration parameters."""
        return {
            "db_path": self.db_path
        }
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        # Validate API key
        agent_valid = self.api_key is not None and self.api_key.strip() != ""
        
        # Validate database path
        database_valid = self.db_path is not None and self.db_path.strip() != ""
        
        return agent_valid and database_valid
