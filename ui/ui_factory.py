"""
Main UI factory for AskTennis AI application.
Orchestrates all UI components to create the complete user interface.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
from ui.display.ui_display import UIDisplay
from ui.formatting.data_formatter import DataFormatter
from ui.processing.query_processor import QueryProcessor


class UIFactory:
    """
    Main factory class for creating and managing UI components.
    Orchestrates all UI modules to provide a cohesive user experience.
    """
    
    def __init__(self):
        """Initialize the UI factory with all components."""
        # Initialize components
        self.data_formatter = DataFormatter()
        self.query_processor = QueryProcessor(self.data_formatter)
        self.ui_display = UIDisplay()
    
    def run_main_app(self, agent_graph, logger):
        """Run the main application logic."""
        # Display example questions
        self.ui_display.display_example_questions()
        
        # Get user input
        user_question = self.ui_display.get_user_input()
        
        # Handle user query if provided
        if user_question:
            self._handle_user_query(user_question, agent_graph, logger)
    
    def _handle_user_query(self, user_question: str, agent_graph, logger):
        """Handle user query processing."""
        # Process the query
        self.query_processor.handle_user_query(user_question, agent_graph, logger)
    
    def get_data_formatter(self) -> DataFormatter:
        """Get the data formatter instance."""
        return self.data_formatter
    
    def get_query_processor(self) -> QueryProcessor:
        """Get the query processor instance."""
        return self.query_processor
    
    
    def get_ui_display(self) -> UIDisplay:
        """Get the UI display instance."""
        return self.ui_display


# Main function for backward compatibility
def run_main_app(agent_graph, logger):
    """
    Main function to run the application.
    Maintains backward compatibility with the original ui_components.py interface.
    """
    factory = UIFactory()
    factory.run_main_app(agent_graph, logger)
