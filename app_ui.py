import streamlit as st 
import pandas as pd
from datetime import datetime

# --- Logging Configuration ---
from tennis_logging.logging_factory import setup_logging

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
from ui.utils.style_loader import load_css

st.set_page_config(page_title="AskTennis AI - Clean UI", layout="wide")

# Load custom CSS from external file
st.markdown(load_css(), unsafe_allow_html=True)

# --- Top Panel: AskTennis Search ---
from ui.display.ui_display import UIDisplay

ui_display = UIDisplay()
ui_display.render_search_panel()

# --- Agent Setup ---
from agent.agent_factory import setup_langgraph_agent
from ui.formatting.consolidated_formatter import ConsolidatedFormatter
from ui.processing.query_processor import QueryProcessor
from services.database_service import DatabaseService

# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    data_formatter = ConsolidatedFormatter()
    query_processor = QueryProcessor(data_formatter)
    db_service = DatabaseService()
    
    # --- Main Layout: Left Panel + Remaining Space ---
    col_left, col_remaining = st.columns([1.4, 6.6])
    
    # =============================================================================
    # COLUMN 1: CLEAN FILTER PANEL (Left Side)
    # =============================================================================
    with col_left:
        st.markdown("Search and analyze tennis data:")
        
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
        # YEAR AND SURFACE
        # =============================================================================
        year_options = ["All Years"] + [str(year) for year in range(2024, 1968, -1)]
        selected_year = st.selectbox("Select Year:", year_options, key="year_select")
        
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
        
    
    # =============================================================================
    # REMAINING SPACE: RESULTS OR AI QUERY
    # =============================================================================
    with col_remaining:
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
        
        
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        🎾 AskTennis AI - Clean Player Analyzer | 
        <a href="https://github.com/Ajit-KBehera/AskTennis_Streamlit" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()
