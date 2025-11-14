"""
UI Display components for AskTennis AI application.
Handles all UI display components and user interface elements.
Extracted from ui_components.py for better modularity.
"""

# Third-party imports
import streamlit as st
import pandas as pd
import numpy as np

# Local application imports
from tennis_logging.simplified_factory import log_error
from serve.combined_serve_charts import create_combined_serve_charts
from return_stats.combined_return_charts import create_combined_return_charts
from rankings.ranking_timeline_chart import create_ranking_timeline_chart
from serve.serve_stats import build_year_suffix
from utils.df_utils import add_player_match_columns


class UIDisplay:
    """
    Centralized UI display class for tennis application.
    Handles all user interface display components.
    
    Method execution order:
    1. render_main_content() - Main entry point, orchestrates layout
    2. render_filter_panel() - Renders filter controls (called by main_content, left column)
    3. render_search_panel() - Renders search input (called by main_content, right column top)
    4. render_results_panel() - Renders results display (called by main_content, right column bottom)
    """
    
    @staticmethod
    def render_main_content(db_service, query_processor, agent_graph, column_layout=None):
        """
        Render the main content area with filter panel on left and search/results panel on right.
        
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
        # COLUMN 1: FILTER PANEL (Left Side)
        # =============================================================================
        with col_left:
            UIDisplay.render_filter_panel(db_service)
        
        # =============================================================================
        # COLUMN 2: SEARCH PANEL + RESULTS PANEL (Right Side)
        # =============================================================================
        with col_remaining:
            # Search panel at the top
            UIDisplay.render_search_panel()
            
            # Results panel below search
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
            column_layout = [8.5, 1.5]  # Search gets 8.5, buttons column gets 1.5   
        
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
        
        # Get all players for search (already includes "All Players" as first element)
        all_players = db_service.get_all_players()
        
        # Use selectbox with search functionality
        selected_player = st.selectbox(
            "Search Player:",
            all_players,
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
            opponent_options,
            key="opponent_select",
            help="Type to search opponents"
        )
        
        # =============================================================================
        # TOURNAMENT SEARCH
        # =============================================================================
        
        # Get tournament options based on selected player
        # get_all_tournaments handles "All Players" case and returns all tournaments when player is None
        tournament_options = db_service.get_all_tournaments(selected_player)
        
        # Use selectbox with search functionality
        selected_tournament = st.selectbox(
            "Search Tournament:",
            tournament_options,
            key="tournament_select",
            help="Type to search tournaments (e.g., Wimbledon, French Open)"
        )
        
        # =============================================================================
        # YEAR SELECTION (Range Slider)
        # =============================================================================
        # Get dynamic year range based on selected player
        if selected_player and selected_player != "All Players":
            min_year, max_year = db_service.get_player_year_range(selected_player)
        else:
            min_year, max_year = (1968, 2024)  # Default range for "All Players"
        
        # Check if year range needs to be reset:
        # 1. Player changed, 2. Year range doesn't exist, 3. Current range is invalid
        player_changed = (
            'previous_player' not in st.session_state or 
            st.session_state.previous_player != selected_player
        )
        year_range_missing = 'year_range' not in st.session_state
        
        # Validate existing year range (only if it exists)
        year_range_invalid = False
        if not year_range_missing:
            current_min, current_max = st.session_state.year_range
            year_range_invalid = (
                current_min < min_year or 
                current_max > max_year or 
                current_min > current_max
            )
        
        # Reset year range if any condition requires it
        if player_changed or year_range_missing or year_range_invalid:
            st.session_state.year_range = (min_year, max_year)
            st.session_state.previous_player = selected_player
        
        # Checkbox for "All Years" option
        use_all_years = st.checkbox(
            "All Years",
            value=False,
            key="year_all_years_checkbox",
            help=f"Select all available years ({min_year}-{max_year})"
        )
        
        if use_all_years:
            # Use full range when "All Years" is selected
            selected_year = None  # None represents "All Years"
            # Display the range but disable slider
            st.info(f"Year Range: {min_year} - {max_year} (All Years)")
        elif min_year == max_year:
            # Only one year available - skip slider and use that year
            selected_year = min_year
            st.info(f"Only one year available: {min_year}")
            st.session_state.year_range = (min_year, max_year)
        else:
            # Year range slider with dynamic min/max values
            year_range = st.slider(
                "Select Year Range:",
                min_value=min_year,
                max_value=max_year,
                value=st.session_state.year_range,
                key="year_range_slider",
                help=f"Drag handles to select start and end year. Drag both to same position for single year. Range: {min_year}-{max_year}"
            )
            # Store the range in session state
            st.session_state.year_range = year_range
            
            # Convert range to appropriate format for database query
            if year_range[0] == year_range[1]:
                # Single year selected
                selected_year = year_range[0]
            else:
                # Year range selected - store as tuple for BETWEEN query
                selected_year = (year_range[0], year_range[1])
            
            # Display selected range
            if year_range[0] == year_range[1]:
                st.caption(f"Selected: {year_range[0]}")
            else:
                st.caption(f"Selected: {year_range[0]} - {year_range[1]} ({year_range[1] - year_range[0] + 1} years)")
        
        # =============================================================================
        # SURFACE SELECTION
        # =============================================================================
        # Get surface options based on selected player
        # get_surfaces_for_player returns all surfaces if no player selected
        surface_options = db_service.get_surfaces_for_player(selected_player)
        
        # Multi-select surface options
        selected_surfaces = st.multiselect(
            "Select Surfaces:",
            surface_options,
            default=surface_options,  # All available surfaces selected by default
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
                return
            
            # Calculate is_winner, opponent, and result columns early if player is selected
            # This avoids recalculating in serve_stats and return_stats functions
            player = filters['player']
            if player and player != 'All Players':
                df_matches = add_player_match_columns(df_matches, player)
            
            # Create tabs for different views
            tab_matches, tab_serve, tab_return, tab_ranking, tab_raw = UIDisplay._create_analysis_tabs()
            
            # Render each tab using dedicated methods
            with tab_matches:
                UIDisplay._render_matches_tab(df_matches)
            
            with tab_serve:
                UIDisplay._render_serve_tab(df_matches, filters)
            
            with tab_return:
                UIDisplay._render_return_tab(df_matches, filters)
            
            with tab_ranking:
                UIDisplay._render_ranking_tab(db_service, filters)
            
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
    def _create_analysis_tabs():
        """
        Create tabs for different analysis views.
        
        Returns:
            tuple: Tuple of tab objects (tab_matches, tab_serve, tab_return, tab_ranking, tab_raw)
        """
        return st.tabs([
            "📊 Matches", 
            "🎾 Serve", 
            "🏓 Return",
            "📈 Ranking",
            "📋 RAW"
        ])
    
    @staticmethod
    def _render_matches_tab(df_matches):
        """
        Render the Matches tab displaying filtered match data.
        
        Args:
            df_matches: DataFrame containing match data
        """
        # Define display columns for table view
        display_columns = ['event_year', 'tourney_date', 'tourney_name', 
                          'round', 'winner_name', 'loser_name', 'surface', 'score']
        
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
        # Extract filter values for chart title/display
        player = filters['player'] if filters['player'] != 'All Players' else None
        opponent = filters['opponent'] if filters['opponent'] != 'All Opponents' else None
        tournament = filters['tournament'] if filters['tournament'] != 'All Tournaments' else None
        surfaces = filters['surfaces'] if filters['surfaces'] else None
        # Handle year: None, int, tuple, or string (backward compatibility)
        year = filters.get('year')
        if year == 'All Years' or year is None:
            year = None
        # year is already in correct format (int, tuple, or None)
        
        if player:
            try:
                # Create and display serve charts using pre-loaded DataFrame
                timeline_fig, ace_df_timeline_fig, bp_timeline_fig, radar_fig = create_combined_serve_charts(
                    player_name=player,
                    df=df_matches,
                    year=year,
                    opponent=opponent,
                    tournament=tournament,
                    surfaces=surfaces
                )

                # Use config parameter for Plotly configuration to show the mode bar
                plotly_config = {'displayModeBar': True, 'width': 'stretch'}
                
                # Display timeline chart
                st.plotly_chart(timeline_fig, config=plotly_config)
                
                # Display ace/DF timeline chart
                st.plotly_chart(ace_df_timeline_fig, config=plotly_config)
                
                # Display break point timeline chart
                st.plotly_chart(bp_timeline_fig, config=plotly_config)
                
                # Display radar chart
                st.plotly_chart(radar_fig, config=plotly_config)

            except Exception as e:
                log_error(e, f"Error generating serve charts for {player}", component="ui_display")
                st.error(f"Error generating serve charts: {e}")
                st.info("Please ensure the player name matches exactly and has matches in the selected filters.")
        else:
            st.info("ℹ️ Please select a player to view serve statistics.")
    
    @staticmethod
    def _render_return_tab(df_matches, filters):
        """
        Render the Return Statistics tab with charts.
        
        Args:
            df_matches: DataFrame containing match data (already filtered)
            filters: Dictionary containing filter values
        """
        # Extract filter values for chart title/display
        player = filters['player'] if filters['player'] != 'All Players' else None
        opponent = filters['opponent'] if filters['opponent'] != 'All Opponents' else None
        tournament = filters['tournament'] if filters['tournament'] != 'All Tournaments' else None
        surfaces = filters['surfaces'] if filters['surfaces'] else None
        # Handle year: None, int, tuple, or string (backward compatibility)
        year = filters.get('year')
        if year == 'All Years' or year is None:
            year = None
        # year is already in correct format (int, tuple, or None)
        
        if player:
            try:
                # Create and display return charts using pre-loaded DataFrame
                return_points_timeline_fig, bp_conversion_timeline_fig, radar_fig = create_combined_return_charts(
                    player_name=player,
                    df=df_matches,
                    year=year,
                    opponent=opponent,
                    tournament=tournament,
                    surfaces=surfaces
                )

                # Use config parameter for Plotly configuration to show the mode bar
                plotly_config = {'displayModeBar': True, 'width': 'stretch'}
                
                # Display return points won % timeline chart
                st.plotly_chart(return_points_timeline_fig, config=plotly_config)
                
                # Display break point conversion timeline chart
                st.plotly_chart(bp_conversion_timeline_fig, config=plotly_config)
                
                # Display radar chart
                st.plotly_chart(radar_fig, config=plotly_config)

            except Exception as e:
                log_error(e, f"Error generating return charts for {player}", component="ui_display")
                st.error(f"Error generating return charts: {e}")
                st.info("Please ensure the player name matches exactly and has matches in the selected filters.")
        else:
            st.info("ℹ️ Please select a player to view return statistics.")
    
    @staticmethod
    def _render_ranking_tab(db_service, filters):
        """
        Render the Ranking Timeline tab.
        
        Shows ranking timeline chart if:
        - 1 player is selected (not "All Players")
        - Opponent is "All Opponents"
        - All available surfaces for the player are selected
        - Tournament is "All Tournaments"
        
        Otherwise shows "Ranking timeline chart not available".
        
        Args:
            db_service: DatabaseService instance for querying ranking data
            filters: Dictionary containing filter values
        """
        # Check conditions for showing ranking timeline
        player = filters.get('player')
        opponent = filters.get('opponent')
        tournament = filters.get('tournament')
        surfaces = filters.get('surfaces', [])
        
        # Get available surfaces for the selected player
        # This handles the case where player may not have played on all surfaces
        available_surfaces = db_service.get_surfaces_for_player(player) if player else ["Hard", "Clay", "Grass", "Carpet"]
        
        # Check if conditions are met
        conditions_met = (
            player and 
            player != db_service.ALL_PLAYERS and
            opponent == db_service.ALL_OPPONENTS and
            tournament == db_service.ALL_TOURNAMENTS and
            set(surfaces) == set(available_surfaces)  # All available surfaces for player selected
        )
        
        if conditions_met:
            try:
                # Get year filter
                year = filters.get('year')
                
                # Get ranking timeline data with year filter
                ranking_df = db_service.get_player_ranking_timeline(player, year=year)
                
                if ranking_df.empty:
                    st.warning(f"No ranking data found for {player}.")
                    st.info("Ranking timeline chart not available.")
                else:
                    # Build chart title with year information
                    year_suffix = build_year_suffix(year)
                    title = f"{player} - Ranking Timeline - {year_suffix}"
                    
                    # Create ranking timeline chart
                    ranking_fig = create_ranking_timeline_chart(player, ranking_df, title=title)
                    
                    if ranking_fig:
                        # Display chart
                        plotly_config = {'displayModeBar': True, 'width': 'stretch'}
                        st.plotly_chart(ranking_fig, config=plotly_config)
                    else:
                        st.info("Ranking timeline chart not available.")
                        
            except Exception as e:
                log_error(e, f"Error generating ranking timeline chart for {player}", component="ui_display")
                st.error(f"Error generating ranking timeline chart: {e}")
                st.info("Ranking timeline chart not available.")
        else:
            st.info("Ranking timeline chart not available.")
            # Show why it's not available
            reasons = []
            if not player or player == db_service.ALL_PLAYERS:
                reasons.append("Please select exactly 1 player")
            if opponent != db_service.ALL_OPPONENTS:
                reasons.append("Opponent must be 'All Opponents'")
            if tournament != db_service.ALL_TOURNAMENTS:
                reasons.append("Tournament must be 'All Tournaments'")
            if set(surfaces) != set(available_surfaces):
                reasons.append(f"All available surfaces must be selected ({', '.join(available_surfaces)})")
            
            if reasons:
                st.caption("Requirements: " + " | ".join(reasons))
    
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
            file_name=f"tennis_matches.csv",
            mime="text/csv",
            key="download_raw_csv"
        )