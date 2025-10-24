"""
Unified configuration management for AskTennis AI application.
Consolidates AgentConfigManager and AgentConfig into a single class.
"""

import streamlit as st
from typing import Optional, Dict, Any


class UnifiedAgentConfig:
    """
    Unified configuration class for the tennis AI agent.
    Consolidates all configuration management into a single class.
    """
    
    def __init__(self):
        """Initialize with default configuration."""
        self.model_name = "gemini-2.5-flash-lite"
        self.temperature = 0
        self.db_path = "sqlite:///tennis_data.db"
        self.api_key = self._get_api_key()
    
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
            "path": self.db_path,
            "engine_kwargs": {}
        }
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present."""
        return self.api_key is not None and self.api_key.strip() != ""
    
    def set_api_key(self, api_key: str):
        """Set the API key for the LLM."""
        self.api_key = api_key
