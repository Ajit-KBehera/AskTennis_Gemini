"""
UI Display components for AskTennis AI application.
Handles all UI display components and user interface elements.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
import pandas as pd
from typing import Optional


class UIDisplay:
    """
    Centralized UI display class for tennis application.
    Handles all user interface display components.
    
    Method execution order:
    1. render_main_content() - Main entry point, orchestrates layout
    2. render_search_panel() - Renders search input (called separately or by main_content)
    3. render_filter_panel() - Renders filter controls (called by main_content)
    4. render_results_panel() - Renders results display (called by main_content)
    """
    
    @staticmethod
    def _reset_ai_query_state():
        """
        Reset all AI query related session state variables.
        Clears dataframe, structured data, results, and summary.
        """
        state_keys_to_clear = [
            'ai_query_results',
            'ai_query_summary',
            'ai_query_structured_data',
            'ai_query_dataframe',
            'ai_query'  # Clear the query itself
        ]
        for key in state_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def _reset_main_content_state():
        """
        Reset all main content panel state (AI queries and table results).
        Clears both AI query results and table analysis results.
        """
        # Reset AI query state
        UIDisplay._reset_ai_query_state()
        
        # Reset table/analysis state
        if 'analysis_generated' in st.session_state:
            st.session_state.analysis_generated = False
        if 'analysis_context' in st.session_state:
            st.session_state.analysis_context = {}
        if 'show_ai_results' in st.session_state:
            st.session_state.show_ai_results = False
    
    @staticmethod
    def render_main_content(db_service, query_processor, agent_graph, logger, column_layout=None):
        """
        Render the main content area with filter panel on left and results panel on right.
        
        Args:
            db_service: DatabaseService instance for querying data
            query_processor: QueryProcessor instance for handling AI queries
            agent_graph: LangGraph agent instance
            logger: Logger instance for logging
            column_layout: List of column widths [left_width, right_width].
                         Defaults to [1.2, 6.8].
        """
        if column_layout is None:
            column_layout = [1.2, 6.8]
        
        col_left, col_remaining = st.columns(column_layout)
        
        # =============================================================================
        # COLUMN 1: CLEAN FILTER PANEL (Left Side)
        # =============================================================================
        with col_left:
            UIDisplay.render_filter_panel(db_service)
        
        # =============================================================================
        # REMAINING SPACE: RESULTS OR AI QUERY
        # =============================================================================
        with col_remaining:
            UIDisplay.render_results_panel(query_processor, agent_graph, logger, db_service)
    
    @staticmethod
    def render_search_panel(column_layout=None):
        """
        Render the search panel with input field, Send button, and Clear button.
        
        Args:
            column_layout: List of column widths [search_width, buttons_width].
                         Defaults to [8, 4]. Buttons are placed in the second column.
        
        Returns:
            The query string if Send button was clicked, None otherwise.
        """
        if column_layout is None:
            column_layout = [8, 4]  # Search gets 8, buttons column gets 4
        
        # Use a container to ensure the search panel always renders consistently
        search_container = st.container()
        with search_container:
            col_search, col_buttons = st.columns(column_layout)
            
            with col_search:
                ai_query = st.text_input(
                    "AskTennis Search:",
                    placeholder="Ask any tennis question (e.g., Who won Wimbledon 2022?)",
                    key="ai_search_input",
                    label_visibility="visible"
                )
            
            with col_buttons:
                # Put both buttons in the same column to prevent layout collapse
                st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
                btn_col1, btn_col2 = st.columns([1, 1])
                
                with btn_col1:
                    send_clicked = st.button("Send", type="primary", key="search_send_button", use_container_width=True)
                    if send_clicked:
                        if ai_query:
                            # Reset all AI query state and main content panel
                            UIDisplay._reset_main_content_state()
                            
                            # Set new query and show AI results
                            st.session_state.ai_query = ai_query
                            st.session_state.show_ai_results = True
                            st.session_state.analysis_generated = False  # Hide table results
                            st.rerun()
                
                with btn_col2:
                    # Always render the Clear button to ensure it's visible
                    clear_clicked = st.button("Clear", key="search_clear_button", use_container_width=True)
                    if clear_clicked:
                        # Clear the search input
                        st.session_state.ai_search_input = ""
                        
                        # Reset all main content panel state (AI queries and table results)
                        UIDisplay._reset_main_content_state()
                        
                        st.rerun()
        
        # Return query from session state if it exists and show_ai_results is True
        if st.session_state.get('show_ai_results', False) and st.session_state.get('ai_query'):
            return st.session_state.get('ai_query')
        
        return None
    
    @staticmethod
    def render_filter_panel(db_service):
        """
        Render the filter panel with player, opponent, tournament, year, and surface filters.
        Includes Generate and Clear Cache buttons.
        
        Args:
            db_service: DatabaseService instance for querying data
        
        Returns:
            Boolean indicating if Generate button was clicked
        """
        st.markdown("Analyze Tennis data:")
        
        # Initialize session state for filters
        if 'analysis_filters' not in st.session_state:
            st.session_state.analysis_filters = {
                'player': None,
                'opponent': None,
                'tournament': None,
                'year': None,
                'surfaces': []
            }
        
        
        # =============================================================================
        # PLAYER SEARCH
        # =============================================================================
        
        # Get all players for search
        all_players = db_service.get_all_players()
        all_players = [p for p in all_players if p != "All Players"]
        
        # Use selectbox with search functionality
        selected_player = st.selectbox(
            "Search Player:",
            ["All Players"] + all_players,
            key="player_select",
            help="Type to search players (e.g., Federer, Nadal)"
        )
        
        # =============================================================================
        # OPPONENT SEARCH
        # =============================================================================
        
        # Get opponent options based on selected player
        if selected_player and selected_player != "All Players":
            opponent_options = db_service.get_opponents_for_player(selected_player)
        else:
            opponent_options = all_players  # Show all players if no player selected
        
        # Use selectbox with search functionality
        selected_opponent = st.selectbox(
            "Search Opponent:",
            ["All Opponents"] + opponent_options,
            key="opponent_select",
            help="Type to search opponents"
        )
        
        # =============================================================================
        # TOURNAMENT SEARCH
        # =============================================================================
        
        # Get all tournaments for search
        all_tournaments = db_service.get_all_tournaments()
        all_tournaments = [t for t in all_tournaments if t != "All Tournaments"]
        
        # Use selectbox with search functionality
        selected_tournament = st.selectbox(
            "Search Tournament:",
            ["All Tournaments"] + all_tournaments,
            key="tournament_select",
            help="Type to search tournaments (e.g., Wimbledon, French Open)"
        )
        
        # =============================================================================
        # YEAR SELECTION
        # =============================================================================
        year_options = ["All Years"] + [str(year) for year in range(2024, 1968, -1)]
        selected_year = st.selectbox("Select Year:", year_options, key="year_select")
        
        # =============================================================================
        # SURFACE SELECTION
        # =============================================================================
        # Multi-select surface options
        surface_options = ["Hard", "Clay", "Grass", "Carpet"]
        selected_surfaces = st.multiselect(
            "Select Surfaces:",
            surface_options,
            default=surface_options,  # All surfaces selected by default
            key="surface_multiselect",
            help="Select one or more surfaces to filter matches"
        )
        
        # =============================================================================
        # GENERATE BUTTON
        # =============================================================================
        st.markdown("---")
        col_generate, col_clear_cache = st.columns([2, 1])
        
        with col_generate:
            generate_button = st.button(
                "🔍 Generate",
                type="primary",
                key="filter_generate_button",
                use_container_width=True
            )
        
        with col_clear_cache:
            if st.button("🗑️", help="Clear cached data if results seem stale", key="filter_clear_cache_button"):
                db_service.clear_cache()
                st.success("Cache cleared!")
                st.rerun()
        
        # Update session state
        if generate_button:
            st.session_state.analysis_filters = {
                'player': selected_player,
                'opponent': selected_opponent,
                'tournament': selected_tournament,
                'year': selected_year,
                'surfaces': selected_surfaces
            }
            st.session_state.analysis_generated = True
            st.session_state.show_ai_results = False  # Reset AI results to show table
            # Add cache busting
            st.session_state.cache_bust = st.session_state.get('cache_bust', 0) + 1
            return True
        
        return False
    
    @staticmethod
    def render_results_panel(query_processor, agent_graph, logger, db_service):
        """
        Render the results panel displaying either AI query results or table/filter results.
        Handles conditional rendering based on session state flags.
        
        Args:
            query_processor: QueryProcessor instance for handling AI queries
            agent_graph: LangGraph agent instance
            logger: Logger instance for logging
            db_service: DatabaseService instance for querying data
        """
        # Handle AI Query Results
        if st.session_state.get('show_ai_results', False) and st.session_state.get('ai_query'):
            # Check if we already have processed results
            if st.session_state.get('ai_query_results'):
                # Display the results
                UIDisplay._render_ai_query_results()
            else:
                # Process the query
                try:
                    with st.spinner("AI is analyzing your question..."):
                        query_processor.handle_user_query(st.session_state.ai_query, agent_graph, logger)
                        # After processing, render the results
                        UIDisplay._render_ai_query_results()
                except Exception as e:
                    st.error(f"Error processing query: {e}")
        
        # Handle Table Results
        elif st.session_state.get('analysis_generated', False):
            filters = st.session_state.analysis_filters
            
            # Get data from database
            df = db_service.get_matches_with_filters(
                player=filters['player'],
                opponent=filters['opponent'],
                tournament=filters['tournament'],
                year=filters['year'],
                surfaces=filters['surfaces'],
                _cache_bust=st.session_state.get('cache_bust', 0)
            )
            
            if not df.empty:
                # Display results table
                st.dataframe(df, width='stretch')
                
                # Clear button
                if st.button("🗑️ Clear Results"):
                    st.session_state.analysis_generated = False
                    st.session_state.analysis_context = {}
                    st.rerun()
            else:
                st.warning("No matches found for the selected criteria.")
        else:
            pass
    
    @staticmethod
    def _render_ai_query_results():
        """
        Render AI query results with summary and table (if applicable).
        Handles display of both text-only and table responses.
        """
        summary = st.session_state.get('ai_query_summary', '')
        dataframe = st.session_state.get('ai_query_dataframe')
        is_table_candidate = st.session_state.get('ai_query_results', {}).get('is_table_candidate', False)
        current_query = st.session_state.get('ai_query', '')
        
        if not summary and not dataframe:
            st.warning("I processed your request but couldn't generate a clear response.")
            return
        
        # Display summary
        if summary:
            st.success("Here's what I found:")
            st.markdown(summary)
        
        # Display table if applicable
        # IMPORTANT: Only show dataframe if is_table_candidate is True AND dataframe exists
        # This prevents showing stale dataframes from previous queries
        if dataframe is not None and is_table_candidate and not dataframe.empty:
            # Use a unique key based on query text to prevent caching issues
            import hashlib
            query_hash = hashlib.md5(current_query.encode()).hexdigest()[:8]
            dataframe_key = f"ai_query_df_{query_hash}"
            
            # Render dataframe with unique key
            st.dataframe(dataframe, width='stretch', key=dataframe_key)
        else:
            # No table to show - this could be:
            # 1. Text-only response (is_table_candidate = False)
            # 2. No structured data for current query
            # In either case, ensure we don't show stale dataframes
            pass