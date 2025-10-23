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
        player_search = st.text_input(
            "Search Player",
            key="player_search",
            placeholder="Type player name (e.g., Federer, Nadal)",
            help="Type 2+ characters to search"
        )
        
        if player_search and len(player_search) >= 2:
            search_results = smart_dropdown.get_search_results(player_search, "players")
            if search_results:
                selected_player = st.selectbox(
                    "Select Player:",
                    ["All Players"] + search_results,
                    key="player_select"
                )
            else:
                st.info("No players found")
                selected_player = "All Players"
        else:
            selected_player = "All Players"
        
        # =============================================================================
        # OPPONENT SEARCH
        # =============================================================================
        st.subheader("⚔️ Opponent")
        opponent_search = st.text_input(
            "Search Opponent",
            key="opponent_search",
            placeholder="Type opponent name",
            help="Type 2+ characters to search"
        )
        
        if opponent_search and len(opponent_search) >= 2:
            if selected_player and selected_player != "All Players":
                opponent_options = db_service.get_opponents_for_player(selected_player)
                search_results = [o for o in opponent_options if opponent_search.lower() in o.lower()]
            else:
                search_results = smart_dropdown.get_search_results(opponent_search, "players")
            
            if search_results:
                selected_opponent = st.selectbox(
                    "Select Opponent:",
                    ["All Opponents"] + search_results[:20],
                    key="opponent_select"
                )
            else:
                st.info("No opponents found")
                selected_opponent = "All Opponents"
        else:
            selected_opponent = "All Opponents"
        
        # =============================================================================
        # TOURNAMENT SEARCH
        # =============================================================================
        st.subheader("🏆 Tournament")
        tournament_search = st.text_input(
            "Search Tournament",
            key="tournament_search",
            placeholder="Type tournament name (e.g., Wimbledon)",
            help="Type 2+ characters to search"
        )
        
        if tournament_search and len(tournament_search) >= 2:
            search_results = smart_dropdown.get_search_results(tournament_search, "tournaments")
            if search_results:
                selected_tournament = st.selectbox(
                    "Select Tournament:",
                    ["All Tournaments"] + search_results,
                    key="tournament_select"
                )
            else:
                st.info("No tournaments found")
                selected_tournament = "All Tournaments"
        else:
            selected_tournament = "All Tournaments"
        
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
            use_container_width=True
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
                # Display metrics
                if filters['player'] and filters['player'] != "All Players":
                    stats = db_service.get_player_statistics(filters['player'])
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Matches", stats['total_matches'])
                    with col2:
                        st.metric("Win Rate", f"{stats['win_rate']}%")
                    with col3:
                        st.metric("Wins", stats['wins'])
                    with col4:
                        st.metric("Losses", stats['losses'])
                else:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Matches", len(df))
                    with col2:
                        st.metric("Unique Players", df['winner_name'].nunique() + df['loser_name'].nunique())
                    with col3:
                        st.metric("Tournaments", df['tourney_name'].nunique())
                    with col4:
                        st.metric("Years", df['event_year'].nunique())
                
                # Display results table
                st.dataframe(df, use_container_width=True)
                
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
            
            if context.get('insights'):
                st.markdown("**💡 Key Insights:**")
                for insight in context['insights'][:3]:
                    st.markdown(f"• {insight}")
        
        # Chat interface
        st.markdown("### 💭 Ask Questions")
        
        if st.session_state.get('analysis_generated', False):
            context = st.session_state.get('analysis_context', {})
            suggestions = context.get('suggestions', [])
            
            if suggestions:
                st.markdown("**💡 Suggestions:**")
                for suggestion in suggestions[:3]:
                    if st.button(f"💡 {suggestion}", key=f"suggestion_{suggestion}", use_container_width=True):
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
        
        if st.button("🚀 Send", type="primary", use_container_width=True):
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
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
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
