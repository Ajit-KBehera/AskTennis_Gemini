"""
Agent configuration and settings management.
Handles API key validation and configuration loading.
"""

import streamlit as st
from typing import Optional


class AgentConfigManager:
    """
    Manages configuration for the tennis AI agent.
    Handles API key validation and configuration loading.
    """
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.model_name = "gemini-2.5-flash-lite"
        self.temperature = 0
        self.db_path = "sqlite:///tennis_data_new.db"
    
    def _get_api_key(self) -> str:
        """
        Get the Google API key from Streamlit secrets.
        Raises an error if the key is not found.
        """
        try:
            return st.secrets["GOOGLE_API_KEY"]
        except (KeyError, FileNotFoundError):
            st.error(
                "Google API key not found! Please create a `.streamlit/secrets.toml` file "
                "and add your GOOGLE_API_KEY."
            )
            st.stop()
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration parameters."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "api_key": self.api_key
        }
    
    def get_database_config(self) -> dict:
        """Get database configuration parameters."""
        return {
            "path": self.db_path,
            "engine_kwargs": {}
        }
    
    def validate_config(self) -> bool:
        """
        Validate that all required configuration is present.
        Returns True if valid, False otherwise.
        """
        return self.api_key is not None and self.api_key.strip() != ""
