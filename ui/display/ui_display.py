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
                width='stretch'
            )
        
        with col_clear_cache:
            if st.button("🗑️", help="Clear cached data if results seem stale"):
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
            try:
                with st.spinner("AI is analyzing your question..."):
                    query_processor.handle_user_query(st.session_state.ai_query, agent_graph, logger)
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