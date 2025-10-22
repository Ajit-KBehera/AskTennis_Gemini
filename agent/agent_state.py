"""
Agent state definitions and management for LangGraph.
Extracted from agent_setup.py for better modularity.
"""

from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Defines the state structure for the LangGraph agent.
    Contains messages that accumulate during the conversation.
    """
    messages: Annotated[List[BaseMessage], operator.add]


class AgentConfig:
    """
    Configuration class for the tennis AI agent.
    Centralizes all configuration settings.
    """
    
    def __init__(self):
        self.model_name = "gemini-2.5-flash-lite"
        self.temperature = 0
        self.db_path = "sqlite:///tennis_data.db"
        self.api_key = None  # Will be set by setup method
    
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
    
    def set_api_key(self, api_key: str):
        """Set the API key for the LLM."""
        self.api_key = api_key
