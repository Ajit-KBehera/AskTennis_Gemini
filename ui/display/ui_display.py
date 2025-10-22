"""
UI Display components for AskTennis AI application.
Handles all UI display components and user interface elements.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st


class UIDisplay:
    """
    Centralized UI display class for tennis application.
    Handles all user interface display components.
    """
    
    @staticmethod
    def display_example_questions():
        """Display example questions for users."""
        st.markdown("##### Example Questions:")
        st.markdown("""
        - *How many matches did Roger Federer win in 2006?*
        - *Who won the most matches on clay in 2010?*
        - *What was the score of the Wimbledon final in 2008?*
        """)
    
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
    
    @staticmethod
    def display_coverage_insights(ml_integration):
        """Display coverage insights if available."""
        if ml_integration.has_coverage_issues():
            coverage_summary = ml_integration.get_coverage_summary()
            st.info(f"📊 **Coverage Analysis**: {coverage_summary}")
    
    @staticmethod
    def display_performance_insights(ml_integration):
        """Display performance insights if available."""
        performance_summary = ml_integration.get_performance_summary()
        if performance_summary != "No performance data available.":
            st.info(f"⚡ **Performance**: {performance_summary}")
    
    @staticmethod
    def display_session_insights(ml_integration):
        """Display session insights if available."""
        # Display coverage insights
        UIDisplay.display_coverage_insights(ml_integration)
        
        # Display performance insights
        UIDisplay.display_performance_insights(ml_integration)
