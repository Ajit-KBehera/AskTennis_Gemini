import streamlit as st
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
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🎾 AskTennis AI - Clean Player Analyzer</h1>
    <p>Simple search-based tennis analysis</p>
</div>
""", unsafe_allow_html=True)

# --- Agent Setup ---
from agent.agent_factory import setup_langgraph_agent
from ui.display.ui_display import UIDisplay
from ui.formatting.data_formatter import DataFormatter
from ui.processing.query_processor import QueryProcessor
from services.database_service import DatabaseService
from services.analysis_service import AnalysisService
from services.export_service import ExportService
from services.smart_dropdown_service import SmartDropdownService

# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    ui_display = UIDisplay()
    data_formatter = DataFormatter()
    query_processor = QueryProcessor(data_formatter)
    db_service = DatabaseService()
    analysis_service = AnalysisService(db_service)
    export_service = ExportService()
    smart_dropdown = SmartDropdownService(db_service)
    
    # --- Main 3-Column Layout ---
    col1, col2, col3 = st.columns([2, 4, 2])
    
    # =============================================================================
    # COLUMN 1: CLEAN FILTER PANEL (Left Side)
    # =============================================================================
    with col1:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.header("🎾 Player Analyzer")
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
        st.subheader("👤 Player")
        
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
        st.subheader("⚔️ Opponent")
        
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
        st.subheader("🏆 Tournament")
        
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
        st.subheader("📅 Year")
        year_options = ["All Years"] + [str(year) for year in range(2024, 2015, -1)]
        selected_year = st.selectbox("Select Year:", year_options, key="year_select")
        
        st.subheader("🏟️ Surface")
        surface_options = ["All Surfaces", "Hard", "Clay", "Grass", "Carpet"]
        selected_surface = st.selectbox("Select Surface:", surface_options, key="surface_select")
        
        # =============================================================================
        # GENERATE BUTTON
        # =============================================================================
        st.markdown("---")
        generate_button = st.button(
            "🔍 Generate Analysis",
            type="primary",
            width='stretch'
        )
        
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
            
            # Generate analysis context
            df = db_service.get_matches_with_filters(
                player=selected_player,
                opponent=selected_opponent,
                tournament=selected_tournament,
                year=selected_year,
                surface=selected_surface
            )
            st.session_state.analysis_context = analysis_service.generate_analysis_context(
                st.session_state.analysis_filters, df
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =============================================================================
    # COLUMN 2: RESULTS PANEL (Middle)
    # =============================================================================
    with col2:
        st.markdown('<div class="results-panel">', unsafe_allow_html=True)
        st.header("📊 Analysis Results")
        
        if st.session_state.get('analysis_generated', False):
            filters = st.session_state.analysis_filters
            
            # Get real data from database
            df = db_service.get_matches_with_filters(
                player=filters['player'],
                opponent=filters['opponent'],
                tournament=filters['tournament'],
                year=filters['year'],
                surface=filters['surface']
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
            st.info("👈 Use the search boxes on the left to find and analyze tennis data!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =============================================================================
    # COLUMN 3: CHAT PANEL (Right Side)
    # =============================================================================
    with col3:
        st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
        st.header("💬 AskTennis AI")
        
        # Display current analysis context
        if st.session_state.get('analysis_generated', False):
            context = st.session_state.get('analysis_context', {})
            st.markdown("### 🎯 Current Analysis")
            st.markdown(f"**{context.get('summary', 'Analysis')}**")
        
        # Chat interface
        st.markdown("### 💭 Ask Questions")
        
        if st.session_state.get('analysis_generated', False):
            context = st.session_state.get('analysis_context', {})
            suggestions = context.get('suggestions', [])
            
            if suggestions:
                st.markdown("**💡 Suggestions:**")
                for suggestion in suggestions[:3]:
                    if st.button(f"💡 {suggestion}", key=f"suggestion_{suggestion}", width='stretch'):
                        st.session_state.chat_input = suggestion
        else:
            st.info("Generate an analysis first for smart suggestions!")
        
        # Chat input
        chat_input = st.text_input(
            "Ask a question:",
            value=st.session_state.get('chat_input', ''),
            placeholder="e.g., Show me their head-to-head record",
            key="chat_input_field"
        )
        
        if st.button("🚀 Send", type="primary", width='stretch'):
            if chat_input:
                st.session_state.chat_input = chat_input
                try:
                    with st.spinner("AI is analyzing..."):
                        if st.session_state.get('analysis_generated', False):
                            context = st.session_state.get('analysis_context', {})
                            enhanced_query = analysis_service.generate_enhanced_query(chat_input, context)
                            query_processor.handle_user_query(enhanced_query, agent_graph, logger)
                        else:
                            query_processor.handle_user_query(chat_input, agent_graph, logger)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("🗑️ Clear Chat", width='stretch'):
            st.session_state.chat_input = ''
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
