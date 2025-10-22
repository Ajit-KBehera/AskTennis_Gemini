"""
LLM logging utilities for AskTennis AI application.
Handles LLM interaction logging functionality.
Extracted from logging_config.py for better modularity.
"""

import logging
from langchain_core.messages import HumanMessage, AIMessage


class LLMLogger:
    """
    Centralized LLM logging class for tennis application.
    Handles LLM interaction logging functionality.
    """
    
    def __init__(self):
        """Initialize the LLM logger."""
        self.logger = logging.getLogger(__name__)
    
    def log_llm_interaction(self, messages, interaction_type="LLM_CALL"):
        """Log LLM interactions and responses."""
        self.logger.info(f"=== {interaction_type} START ===")
        for i, message in enumerate(messages):
            if isinstance(message, HumanMessage):
                self.logger.info(f"Human Message {i+1}: {message.content}")
            elif isinstance(message, AIMessage):
                self.logger.info(f"AI Message {i+1}: {message.content}")
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    self.logger.info(f"Tool Calls: {[tool_call for tool_call in message.tool_calls]}")
            else:
                self.logger.info(f"Message {i+1} ({type(message).__name__}): {message.content}")
        self.logger.info(f"=== {interaction_type} END ===")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger
