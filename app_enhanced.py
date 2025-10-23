import streamlit as st
import pandas as pd
from datetime import datetime

# --- Logging Configuration ---
from tennis_logging.logging_factory import setup_logging

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
from config.constants import APP_TITLE, APP_SUBTITLE
st.set_page_config(page_title="AskTennis AI - Enhanced", layout="wide")

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
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🎾 AskTennis AI - Enhanced Player Analyzer</h1>
    <p>Analyze tennis players with structured filters and AI-powered insights</p>
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

# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    ui_display = UIDisplay()
    data_formatter = DataFormatter()
    query_processor = QueryProcessor(data_formatter)
    db_service = DatabaseService()
    analysis_service = AnalysisService(db_service)
    export_service = ExportService()
    
    # --- Main 3-Column Layout ---
    col1, col2, col3 = st.columns([2, 4, 2])
    
    # =============================================================================
    # COLUMN 1: FILTER PANEL (Left Side)
    # =============================================================================
    with col1:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.header("🎾 Player Analyzer")
        st.markdown("Configure your analysis parameters:")
        
        # Initialize session state for filters
        if 'analysis_filters' not in st.session_state:
            st.session_state.analysis_filters = {
                'player': None,
                'opponent': None,
                'tournament': None,
                'year': None,
                'surface': None
            }
        
        # Player Selection
        st.subheader("👤 Player")
        player_options = db_service.get_all_players()
        selected_player = st.selectbox(
            "Select Player",
            player_options,
            key="player_selector",
            help="Choose the player to analyze"
        )
        
        # Opponent Selection (dynamic based on selected player)
        st.subheader("⚔️ Opponent")
        if selected_player and selected_player != "All Players":
            opponent_options = db_service.get_opponents_for_player(selected_player)
        else:
            opponent_options = db_service.get_all_players()
        
        selected_opponent = st.selectbox(
            "Select Opponent",
            opponent_options,
            key="opponent_selector",
            help="Choose specific opponent (optional)"
        )
        
        # Tournament Selection
        st.subheader("🏆 Tournament")
        tournament_options = db_service.get_all_tournaments()
        selected_tournament = st.selectbox(
            "Select Tournament",
            tournament_options,
            key="tournament_selector",
            help="Choose specific tournament (optional)"
        )
        
        # Year Selection
        st.subheader("📅 Year")
        year_options = db_service.get_available_years()
        selected_year = st.selectbox(
            "Select Year",
            year_options,
            key="year_selector",
            help="Choose specific year (optional)"
        )
        
        # Surface Selection
        st.subheader("🏟️ Surface")
        surface_options = db_service.get_available_surfaces()
        selected_surface = st.selectbox(
            "Select Surface",
            surface_options,
            key="surface_selector",
            help="Choose specific surface (optional)"
        )
        
        # Generate Button
        st.markdown("---")
        generate_button = st.button(
            "🔍 Generate Analysis",
            type="primary",
            use_container_width=True,
            help="Generate match analysis based on selected filters"
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
        st.header("📊 Match Results")
        
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
            else:
                st.warning("No matches found for the selected criteria. Try adjusting your filters.")
            
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
                    # Create visualization data
                    context = st.session_state.get('analysis_context', {})
                    viz_data = export_service.create_visualization_data(df, context)
                    
                    if viz_data:
                        st.success("Visualization data prepared! Charts coming soon!")
                        st.json(viz_data)  # Show data structure for now
                    else:
                        st.info("No visualization data available")
            
            with col_clear:
                if st.button("🗑️ Clear Results"):
                    st.session_state.analysis_generated = False
                    st.session_state.analysis_context = {}
                    st.rerun()
        else:
            st.info("👈 Configure your analysis parameters in the left panel and click 'Generate Analysis' to see results.")
            
            # Show example of what the results will look like
            st.markdown("### 📋 Example Results Preview")
            st.markdown("""
            When you generate an analysis, you'll see:
            - **Summary Metrics**: Win rate, total matches, average sets
            - **Detailed Match Table**: Date, tournament, opponent, score, result
            - **Export Options**: Download data as CSV or Excel
            - **Visualization**: Charts and graphs of performance
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =============================================================================
    # COLUMN 3: CHAT PANEL (Right Side)
    # =============================================================================
    with col3:
        st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
        st.header("💬 AskTennis AI")
        st.markdown("Ask follow-up questions about your analysis:")
        
        # Display current analysis context
        if st.session_state.get('analysis_generated', False):
            context = st.session_state.get('analysis_context', {})
            filters = st.session_state.analysis_filters
            
            st.markdown("### 🎯 Current Analysis")
            st.markdown(f"**{context.get('summary', 'Analysis')}**")
            
            # Show insights
            if context.get('insights'):
                st.markdown("**💡 Key Insights:**")
                for insight in context['insights'][:3]:  # Show top 3 insights
                    st.markdown(f"• {insight}")
        
        # Chat interface
        st.markdown("### 💭 Ask Questions")
        
        # Smart suggestions based on context
        if st.session_state.get('analysis_generated', False):
            context = st.session_state.get('analysis_context', {})
            suggestions = context.get('suggestions', [])
            
            if suggestions:
                st.markdown("**💡 Smart Suggestions:**")
                for suggestion in suggestions[:4]:  # Show top 4 suggestions
                    if st.button(f"💡 {suggestion}", key=f"suggestion_{suggestion}", use_container_width=True):
                        st.session_state.chat_input = suggestion
            else:
                # Fallback suggestions
                st.markdown("**💡 Try asking:**")
                example_questions = [
                    "Show me their clay court record",
                    "Who are their toughest opponents?",
                    "What's their best tournament?",
                    "Compare their performance by surface"
                ]
                
                for question in example_questions:
                    if st.button(f"💡 {question}", key=f"example_{question}", use_container_width=True):
                        st.session_state.chat_input = question
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
                # Process the chat query with context enhancement
                try:
                    with st.spinner("AI is analyzing your question..."):
                        # Enhance query with context if available
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
        🎾 AskTennis AI - Enhanced Player Analyzer | 
        <a href="https://github.com/Ajit-KBehera/AskTennis_Streamlit" target="_blank">GitHub</a> |
        Powered by AI
    </div>
    """, unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()
