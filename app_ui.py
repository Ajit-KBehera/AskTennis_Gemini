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
        ui_display.render_results_panel(query_processor, agent_graph, logger, db_service)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()
