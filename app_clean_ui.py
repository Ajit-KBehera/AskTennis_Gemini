import streamlit as st  # pyright: ignore[reportMissingImports]
import pandas as pd
from datetime import datetime

# --- Logging Configuration ---
from tennis_logging.logging_factory import setup_logging

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
from config.constants import APP_TITLE, APP_SUBTITLE
st.set_page_config(page_title="AskTennis AI - Clean UI", layout="wide")

# Custom CSS for clean layout
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .filter-panel {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .results-panel {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .chat-panel {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .search-box {
        background-color: #ffffff;
        border: 2px solid #007bff;
        border-radius: 5px;
        padding: 0.5rem;
    }
    
    /* Remove margins and make full width */
    .main .block-container {
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    
    /* Remove column gaps */
    div[data-testid="column"] {
        gap: 0rem;
    }
    
    /* Full width layout */
    .stApp {
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- Top Panel: AskTennis Search ---
col_search, col_send, col_clear = st.columns([6, 1, 1])

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

with col_clear:
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    if st.button("Clear", width='stretch'):
        st.session_state.ai_search_input = ""
        st.session_state.ai_query_results = None
        st.session_state.show_ai_results = False
        st.session_state.analysis_generated = False
        st.rerun()

# --- Agent Setup ---
from agent.agent_factory import setup_langgraph_agent
from ui.display.ui_display import UIDisplay
from ui.formatting.data_formatter import DataFormatter
from ui.processing.query_processor import QueryProcessor
from services.database_service import DatabaseService
from services.analysis_service import AnalysisService
from services.export_service import ExportService

# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    ui_display = UIDisplay()
    data_formatter = DataFormatter()
    query_processor = QueryProcessor(data_formatter)
    db_service = DatabaseService()
    analysis_service = AnalysisService(db_service)
    export_service = ExportService()
    
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
                'surface': None
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
        
        surface_options = ["All Surfaces", "Hard", "Clay", "Grass", "Carpet"]
        selected_surface = st.selectbox("Select Surface:", surface_options, key="surface_select")
        
        # =============================================================================
        # GENERATE BUTTON
        # =============================================================================
        st.markdown("---")
        col_generate, col_clear_cache = st.columns([2, 1])
        
        with col_generate:
            generate_button = st.button(
                "🔍 Generate Analysis",
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
                'surface': selected_surface
            }
            st.session_state.analysis_generated = True
            st.session_state.show_ai_results = False  # Reset AI results to show table
            # Add cache busting
            st.session_state.cache_bust = st.session_state.get('cache_bust', 0) + 1
            
            # Generate analysis context
            df = db_service.get_matches_with_filters(
                player=selected_player,
                opponent=selected_opponent,
                tournament=selected_tournament,
                year=selected_year,
                surface=selected_surface,
                _cache_bust=st.session_state.get('cache_bust', 0)
            )
            st.session_state.analysis_context = analysis_service.generate_analysis_context(
                st.session_state.analysis_filters, df
            )
        
    
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
            
            # Get real data from database
            df = db_service.get_matches_with_filters(
                player=filters['player'],
                opponent=filters['opponent'],
                tournament=filters['tournament'],
                year=filters['year'],
                surface=filters['surface'],
                _cache_bust=st.session_state.get('cache_bust', 0)
            )
            
            if not df.empty:
                # Display results table
                st.dataframe(df, width='stretch')
                
                # Export buttons
                col_export, col_clear = st.columns(2)
                with col_export:
                    if st.button("📥 Export CSV"):
                        csv_data = export_service.export_to_csv(df)
                        if csv_data:
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name="tennis_analysis.csv",
                                mime="text/csv"
                            )
                with col_clear:
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
    <div style="text-align: center; color: #666; padding: 1rem;">
        🎾 AskTennis AI - Clean Player Analyzer | 
        <a href="https://github.com/Ajit-KBehera/AskTennis_Streamlit" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()
