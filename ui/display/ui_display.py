"""
UI Display components for AskTennis AI application.
Handles all UI display components and user interface elements.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
from config.constants import EXAMPLE_QUESTIONS


class UIDisplay:
    """
    Centralized UI display class for tennis application.
    Handles all user interface display components.
    """
    
    @staticmethod
    def display_example_questions():
        """Display example questions for users."""
        st.markdown("##### Example Questions:")
        st.markdown(EXAMPLE_QUESTIONS)
    
    @staticmethod
    def get_user_input():
        """Get user input question."""
        return st.text_input(
            "Ask your tennis question:",
            placeholder="e.g., 'How many tournaments did Serena Williams win on hard court?'"
        )
    
    @staticmethod
    def display_success_message(message: str):
        """Display success message to user."""
        st.success(message)
    
    @staticmethod
    def display_warning_message(message: str):
        """Display warning message to user."""
        st.warning(message)
    
    @staticmethod
    def display_info_message(message: str):
        """Display info message to user."""
        st.info(message)
    
    @staticmethod
    def display_error_message(message: str):
        """Display error message to user."""
        st.error(message)
    
    @staticmethod
    def display_markdown(content: str):
        """Display markdown content to user."""
        st.markdown(content)
    
    @staticmethod
    def display_spinner(message: str):
        """Display spinner with message."""
        return st.spinner(message)
    
    @staticmethod
    def display_tip_message(message: str):
        """Display tip message to user."""
        st.info(f"💡 **Tip**: {message}")
    
