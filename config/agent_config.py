"""
Agent configuration management for AskTennis AI application.
Handles LLM and agent-specific configuration.
"""

import streamlit as st
from typing import Dict, Any
from constants import DEFAULT_MODEL, DEFAULT_TEMPERATURE


class AgentConfig:
    """
    Configuration class for the tennis AI agent.
    Handles LLM model configuration and API key management.
    """
    
    def __init__(self):
        """Initialize with default configuration."""
        self.model_name = DEFAULT_MODEL
        self.temperature = DEFAULT_TEMPERATURE
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
    
    def validate_config(self) -> bool:
        """Validate that all required agent configuration is present."""
        return self.api_key is not None and self.api_key.strip() != ""

