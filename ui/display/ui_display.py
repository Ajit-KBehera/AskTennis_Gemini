"""
UI Display components for AskTennis AI application.
Handles all UI display components and user interface elements.
Extracted from ui_components.py for better modularity.
"""

# Third-party imports
import streamlit as st

# Local application imports
from tennis_logging.simplified_factory import log_error
from serve.combined_serve_charts import create_combined_serve_charts


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
    def render_main_content(db_service, query_processor, agent_graph, column_layout=None):
        """
        Render the main content area with filter panel on left and results panel on right.
        
        Args:
            db_service: DatabaseService instance for querying data
            query_processor: QueryProcessor instance for handling AI queries
            agent_graph: LangGraph agent instance
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
            UIDisplay.render_results_panel(query_processor, agent_graph, db_service)
    
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
                # Handle clearing search input if flag is set
                # Must clear before widget is created to avoid Streamlit error
                if st.session_state.get('clear_search_input', False):
                    # Clear the flag and reset the input value
                    del st.session_state.clear_search_input
                    if 'ai_search_input' in st.session_state:
                        del st.session_state.ai_search_input
                
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
                    send_clicked = st.button("Send", type="primary", key="search_send_button")
                    if send_clicked:
                        if ai_query:
                            st.session_state.ai_query = ai_query
                            st.session_state.show_ai_results = True
                            st.session_state.analysis_generated = False  # Hide table results
                            st.rerun()
                
                with btn_col2:
                    # Always render the Clear button to ensure it's visible
                    clear_clicked = st.button("Clear", key="search_clear_button")
                    if clear_clicked:
                        # Clear all related session state
                        st.session_state.ai_query_results = None
                        st.session_state.show_ai_results = False
                        st.session_state.analysis_generated = False
                        # Use flag-based approach to clear search input (must clear before widget creation)
                        st.session_state.clear_search_input = True
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
                key="filter_generate_button"
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
    def render_results_panel(query_processor, agent_graph, db_service):
        """
        Render the results panel displaying either AI query results or table/filter results.
        Handles conditional rendering based on session state flags.
        
        Args:
            query_processor: QueryProcessor instance for handling AI queries
            agent_graph: LangGraph agent instance
            db_service: DatabaseService instance for querying data
        """
        # Handle AI Query Results
        if st.session_state.get('show_ai_results', False) and st.session_state.get('ai_query'):
            UIDisplay._render_ai_query_results(query_processor, agent_graph)
        
        # Handle Table/Chart Results with Tabs
        elif st.session_state.get('analysis_generated', False):
            filters = st.session_state.analysis_filters
            
            # Load filtered match data
            df_matches = UIDisplay._load_filtered_matches(db_service, filters)
            if df_matches is None:
                return
            
            # Define display columns for table view
            display_columns = ['event_year', 'tourney_date', 'tourney_name', 
                              'round', 'winner_name', 'loser_name', 'surface', 'score']
            
            # Create tabs for different views
            tab_matches, tab_serve, tab_return, tab_raw = UIDisplay._create_analysis_tabs()
            
            # Render each tab using dedicated methods
            with tab_matches:
                UIDisplay._render_matches_tab(df_matches, display_columns)
            
            with tab_serve:
                UIDisplay._render_serve_tab(df_matches, filters)
            
            with tab_return:
                UIDisplay._render_return_tab()
            
            with tab_raw:
                UIDisplay._render_raw_tab(df_matches, filters)
        else:
            pass
    
    # ============================================================================
    # Private Helper Methods
    # ============================================================================
    
    @staticmethod
    def _render_ai_query_results(query_processor, agent_graph):
        """
        Render AI query results including summary and response.
        
        Args:
            query_processor: QueryProcessor instance for handling AI queries
            agent_graph: LangGraph agent instance
        """
        try:
            with st.spinner("AI is analyzing your question..."):
                query_processor.handle_user_query(st.session_state.ai_query, agent_graph)
            
            # Display summary and response if available
            summary = st.session_state.get('ai_query_summary')
            response = st.session_state.get('ai_query_response')
            
            if response:
                # Show summary if available (only generated for responses > 5 lines)
                if summary:
                    st.markdown("### Summary")
                    st.info(summary)
                
                # Show full response
                st.markdown(response)
            else:
                st.warning("I processed your request but couldn't generate a clear response. Please check the conversation flow below for details.")
                
                # Check if this might be a misspelling issue
                if "no results" in str(response).lower() or "not found" in str(response).lower():
                    st.info("💡 **Tip**: If you didn't find what you're looking for, try checking the spelling of player or tournament names. The system is case-sensitive and requires exact matches.")
        
        except Exception as e:
            log_error(e, f"Error processing query in UI display: {st.session_state.get('ai_query', 'unknown')}", component="ui_display")
            st.error(f"Error processing query: {e}")
    
    @staticmethod
    def _load_filtered_matches(db_service, filters):
        """
        Load match data based on filters and handle empty results.
        
        Args:
            db_service: DatabaseService instance for querying data
            filters: Dictionary containing filter values
            
        Returns:
            pandas.DataFrame: DataFrame containing filtered matches, or None if empty
        """
        df_matches = db_service.get_matches_with_filters(
            player=filters['player'],
            opponent=filters['opponent'],
            tournament=filters['tournament'],
            year=filters['year'],
            surfaces=filters['surfaces'],
            return_all_columns=True,  # Get all columns for charts/tables Statistics
            _cache_bust=st.session_state.get('cache_bust', 0)
        )
        
        if df_matches.empty:
            st.warning("No matches found for the selected criteria.")
            return None
        
        return df_matches
    
    @staticmethod
    def _create_analysis_tabs():
        """
        Create tabs for different analysis views.
        
        Returns:
            tuple: Tuple of tab objects (tab_matches, tab_serve, tab_return, tab_raw)
        """
        return st.tabs([
            "📊 Matches", 
            "🎾 Serve", 
            "🏓 Return", 
            "📋 RAW"
        ])
    
    @staticmethod
    def _render_matches_tab(df_matches, display_columns):
        """
        Render the Matches tab displaying filtered match data.
        
        Args:
            df_matches: DataFrame containing match data
            display_columns: List of column names to display
        """
        st.dataframe(df_matches[display_columns], width='stretch')
        if st.button("🗑️ Clear Results", key="clear_matches"):
            st.session_state.analysis_generated = False
            st.session_state.analysis_context = {}
            st.rerun()
    
    @staticmethod
    def _render_serve_tab(df_matches, filters):
        """
        Render the Serve Statistics tab with charts.
        
        Args:
            df_matches: DataFrame containing match data (already filtered)
            filters: Dictionary containing filter values
        """
        if filters['player'] and filters['player'] != 'All Players':
            try:
                # Extract filter values for chart title/display
                opponent = filters['opponent'] if filters['opponent'] != 'All Opponents' else None
                tournament = filters['tournament'] if filters['tournament'] != 'All Tournaments' else None
                surfaces = filters['surfaces'] if filters['surfaces'] else None
                year = filters['year'] if filters['year'] != 'All Years' else None
                
                # Create and display serve charts using pre-loaded DataFrame
                timeline_fig, radar_fig = create_combined_serve_charts(
                    filters['player'], 
                    year,  # Can be str (single year) or None (career view)
                    df=df_matches,
                    opponent=opponent,
                    tournament=tournament,
                    surfaces=surfaces
                )

                # Use config parameter for Plotly configuration to show the mode bar
                plotly_config = {'displayModeBar': True, 'width': 'stretch'}
                
                # Display timeline chart
                st.plotly_chart(timeline_fig, config=plotly_config)
                
                # Display radar chart
                st.plotly_chart(radar_fig, config=plotly_config)

            except Exception as e:
                log_error(e, f"Error generating serve charts for {filters['player']}", component="ui_display")
                st.error(f"Error generating serve charts: {e}")
                st.info("Please ensure the player name matches exactly and has matches in the selected filters.")
        else:
            st.info("ℹ️ Please select a player to view serve statistics.")
    
    @staticmethod
    def _render_return_tab():
        """
        Render the Return Statistics tab (placeholder for future implementation).
        """
        st.info("🚧 Return statistics visualization coming soon...")
    
    @staticmethod
    def _render_raw_tab(df_matches, filters):
        """
        Render the RAW tab displaying full DataFrame and CSV download.
        
        Args:
            df_matches: DataFrame containing match data
            filters: Dictionary containing filter values (for CSV filename)
        """
        st.dataframe(df_matches, width='stretch')
        # Download button for CSV export
        csv_data = df_matches.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"tennis_matches_{filters.get('year', 'all')}.csv",
            mime="text/csv",
            key="download_raw_csv"
        )