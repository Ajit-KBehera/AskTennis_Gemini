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
    col_left, col_remaining = st.columns([1.2, 6.8])
    
    # =============================================================================
    # COLUMN 1: CLEAN FILTER PANEL (Left Side)
    # =============================================================================
    with col_left:
        ui_display.render_filter_panel(db_service)
        
    
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
