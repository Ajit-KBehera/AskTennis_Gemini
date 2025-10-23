import streamlit as st
import pandas as pd
from datetime import datetime

# --- Logging Configuration ---
from tennis_logging.logging_factory import setup_logging

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
from config.constants import APP_TITLE, APP_SUBTITLE
st.set_page_config(page_title="AskTennis AI - Smart UI", layout="wide")

# Custom CSS for better layout
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
    .quick-filter-btn {
        margin: 2px;
        font-size: 0.8rem;
    }
    .search-container {
        background-color: #ffffff;
        padding: 0.5rem;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🎾 AskTennis AI - Smart Player Analyzer</h1>
    <p>Intelligent tennis analysis with smart search and quick filters</p>
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
    # COLUMN 1: SMART FILTER PANEL (Left Side)
    # =============================================================================
    with col1:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.header("🎾 Smart Player Analyzer")
        st.markdown("Use smart search and quick filters:")
        
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
        # PLAYER SELECTION WITH SMART SEARCH
        # =============================================================================
        st.subheader("👤 Player Selection")
        
        # Search functionality
        player_search = st.text_input(
            "🔍 Search Player",
            key="player_search",
            placeholder="Type player name (e.g., Federer, Nadal, Djokovic)",
            help="Type 2+ characters to search players"
        )
        
        # Show search results when user types
        if player_search and len(player_search) >= 2:
            search_results = smart_dropdown.get_search_results(player_search, "players")
            if search_results:
                selected_player = st.selectbox(
                    "Search Results:",
                    ["All Players"] + search_results,
                    key="player_search_results"
                )
            else:
                st.info("No players found. Try a different search term.")
                selected_player = "All Players"
        else:
            selected_player = "All Players"
        
        # Display selected player
        if selected_player and selected_player != "All Players":
            st.success(f"✅ Selected: {selected_player}")
        
        # =============================================================================
        # OPPONENT SELECTION (Dynamic based on player)
        # =============================================================================
        st.subheader("⚔️ Opponent Selection")
        
        if selected_player and selected_player != "All Players":
            # Search functionality for opponents
            opponent_search = st.text_input(
                "🔍 Search Opponent",
                key="opponent_search",
                placeholder=f"Type opponent name for {selected_player}",
                help="Type 2+ characters to search opponents"
            )
            
            # Show search results when user types
            if opponent_search and len(opponent_search) >= 2:
                # Get opponents for selected player
                opponent_options = db_service.get_opponents_for_player(selected_player)
                search_results = [o for o in opponent_options if opponent_search.lower() in o.lower()]
                if search_results:
                    selected_opponent = st.selectbox(
                        "Opponent Results:",
                        ["All Opponents"] + search_results[:20],
                        key="opponent_search_results"
                    )
                else:
                    st.info("No opponents found. Try a different search term.")
                    selected_opponent = "All Opponents"
            else:
                selected_opponent = "All Opponents"
        else:
            selected_opponent = "All Opponents"
        
        # =============================================================================
        # TOURNAMENT SELECTION WITH SMART SEARCH
        # =============================================================================
        st.subheader("🏆 Tournament Selection")
        
        # Tournament search
        tournament_search = st.text_input(
            "🔍 Search Tournament",
            key="tournament_search",
            placeholder="Type tournament name (e.g., Wimbledon, French Open)",
            help="Type 2+ characters to search tournaments"
        )
        
        # Show search results when user types
        if tournament_search and len(tournament_search) >= 2:
            search_results = smart_dropdown.get_search_results(tournament_search, "tournaments")
            if search_results:
                selected_tournament = st.selectbox(
                    "Tournament Results:",
                    ["All Tournaments"] + search_results,
                    key="tournament_search_results"
                )
            else:
                st.info("No tournaments found. Try a different search term.")
                selected_tournament = "All Tournaments"
        else:
            selected_tournament = "All Tournaments"
        
        # =============================================================================
        # YEAR AND SURFACE (Simplified)
        # =============================================================================
        st.subheader("📅 Year Selection")
        year_options = ["All Years"] + smart_dropdown.recent_years
        selected_year = st.selectbox(
            "Select Year:",
            year_options,
            key="year_selector"
        )
        
        st.subheader("🏟️ Surface Selection")
        surface_options = ["All Surfaces", "Hard", "Clay", "Grass", "Carpet"]
        selected_surface = st.selectbox(
            "Select Surface:",
            surface_options,
            key="surface_selector"
        )
        
        # =============================================================================
        # GENERATE BUTTON
        # =============================================================================
        st.markdown("---")
        generate_button = st.button(
            "🔍 Generate Smart Analysis",
            type="primary",
            use_container_width=True,
            help="Generate analysis with smart filtering"
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
    # COLUMN 2: RESULTS PANEL (Middle) - Same as before
    # =============================================================================
    with col2:
        st.markdown('<div class="results-panel">', unsafe_allow_html=True)
        st.header("📊 Smart Analysis Results")
        
        if st.session_state.get('analysis_generated', False):
            # Display analysis results
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
                # Get player statistics
                if filters['player'] and filters['player'] != "All Players":
                    stats = db_service.get_player_statistics(filters['player'])
                    
                    # Display summary metrics
                    col2_1, col2_2, col2_3, col2_4 = st.columns(4)
                    with col2_1:
                        st.metric("Total Matches", stats['total_matches'])
                    with col2_2:
                        st.metric("Win Rate", f"{stats['win_rate']}%")
                    with col2_3:
                        st.metric("Wins", stats['wins'])
                    with col2_4:
                        st.metric("Losses", stats['losses'])
                else:
                    # Display basic metrics
                    col2_1, col2_2, col2_3, col2_4 = st.columns(4)
                    with col2_1:
                        st.metric("Total Matches", len(df))
                    with col2_2:
                        st.metric("Unique Players", df['winner_name'].nunique() + df['loser_name'].nunique())
                    with col2_3:
                        st.metric("Tournaments", df['tourney_name'].nunique())
                    with col2_4:
                        st.metric("Years", df['event_year'].nunique())
                
                # Display results table
                st.dataframe(df, use_container_width=True)
                
                # Action buttons
                col_export_csv, col_export_excel, col_viz, col_clear = st.columns(4)
                
                with col_export_csv:
                    if st.button("📥 Export CSV"):
                        csv_data = export_service.export_to_csv(df)
                        if csv_data:
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name="tennis_analysis.csv",
                                mime="text/csv"
                            )
                
                with col_export_excel:
                    if st.button("📊 Export Excel"):
                        excel_data = export_service.export_to_excel(df)
                        if excel_data:
                            st.download_button(
                                label="Download Excel",
                                data=excel_data,
                                file_name="tennis_analysis.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                
                with col_viz:
                    if st.button("📈 Visualize"):
                        context = st.session_state.get('analysis_context', {})
                        viz_data = export_service.create_visualization_data(df, context)
                        
                        if viz_data:
                            st.success("Visualization data prepared!")
                            st.json(viz_data)
                        else:
                            st.info("No visualization data available")
                
                with col_clear:
                    if st.button("🗑️ Clear Results"):
                        st.session_state.analysis_generated = False
                        st.session_state.analysis_context = {}
                        st.rerun()
            else:
                st.warning("No matches found for the selected criteria. Try adjusting your filters.")
        else:
            st.info("👈 Use the smart filters on the left to generate your analysis!")
            
            # Show smart features
            st.markdown("### 🚀 Smart Features")
            st.markdown("""
            **Smart Search:**
            - Type 2+ characters to search players/tournaments
            - Intelligent search with type-ahead functionality
            - Dynamic opponent filtering based on selected player
            
            **Intelligent Analysis:**
            - Context-aware suggestions
            - Real-time database queries
            - Export and visualization options
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =============================================================================
    # COLUMN 3: CHAT PANEL (Right Side) - Same as before
    # =============================================================================
    with col3:
        st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
        st.header("💬 AskTennis AI")
        st.markdown("Ask intelligent questions about your analysis:")
        
        # Display current analysis context
        if st.session_state.get('analysis_generated', False):
            context = st.session_state.get('analysis_context', {})
            
            st.markdown("### 🎯 Current Analysis")
            st.markdown(f"**{context.get('summary', 'Analysis')}**")
            
            # Show insights
            if context.get('insights'):
                st.markdown("**💡 Key Insights:**")
                for insight in context['insights'][:3]:
                    st.markdown(f"• {insight}")
        
        # Chat interface
        st.markdown("### 💭 Ask Questions")
        
        # Smart suggestions based on context
        if st.session_state.get('analysis_generated', False):
            context = st.session_state.get('analysis_context', {})
            suggestions = context.get('suggestions', [])
            
            if suggestions:
                st.markdown("**💡 Smart Suggestions:**")
                for suggestion in suggestions[:4]:
                    if st.button(f"💡 {suggestion}", key=f"suggestion_{suggestion}", use_container_width=True):
                        st.session_state.chat_input = suggestion
            else:
                st.info("Generate an analysis first for smart suggestions!")
        else:
            st.info("👈 Generate an analysis first to get smart suggestions!")
        
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
                    with st.spinner("AI is analyzing your question..."):
                        if st.session_state.get('analysis_generated', False):
                            context = st.session_state.get('analysis_context', {})
                            enhanced_query = analysis_service.generate_enhanced_query(chat_input, context)
                            query_processor.handle_user_query(enhanced_query, agent_graph, logger)
                        else:
                            query_processor.handle_user_query(chat_input, agent_graph, logger)
                except Exception as e:
                    st.error(f"Error processing query: {e}")
        
        # Clear chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_input = ''
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =============================================================================
    # FOOTER
    # =============================================================================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🎾 AskTennis AI - Smart Player Analyzer | 
        <a href="https://github.com/Ajit-KBehera/AskTennis_Streamlit" target="_blank">GitHub</a> |
        Powered by AI
    </div>
    """, unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()
