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