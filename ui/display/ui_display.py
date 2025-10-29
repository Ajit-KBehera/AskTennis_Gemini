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
    def render_search_panel(column_layout=None):
        """
        Render the search panel with input field, Send button, and Clear button.
        
        Args:
            column_layout: List of column widths [search_width, send_width, clear_width].
                         Defaults to [10, 1, 1].
        
        Returns:
            The query string if Send button was clicked, None otherwise.
        """
        if column_layout is None:
            column_layout = [10, 1, 1]
        
        col_search, col_send, col_clear = st.columns(column_layout)
        
        with col_search:
            ai_query = st.text_input(
                "AskTennis Search:",
                placeholder="Ask any tennis question (e.g., Who won Wimbledon 2022?)",
                key="ai_search_input",
                width='stretch'
            )
        
        with col_send:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
            if st.button("Send", type="primary", width='stretch'):
                if ai_query:
                    st.session_state.ai_query = ai_query
                    st.session_state.show_ai_results = True
                    st.session_state.analysis_generated = False  # Hide table results
                    return ai_query
        
        with col_clear:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
            if st.button("Clear", width='stretch'):
                st.session_state.ai_search_input = ""
                st.session_state.ai_query_results = None
                st.session_state.show_ai_results = False
                st.session_state.analysis_generated = False
                st.rerun()
        
        # Return query from session state if it exists and show_ai_results is True
        if st.session_state.get('show_ai_results', False) and st.session_state.get('ai_query'):
            return st.session_state.get('ai_query')
        
        return None