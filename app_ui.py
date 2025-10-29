# --- Third-party Imports ---
import streamlit as st 

# --- Local Application Imports ---
# Logging
from tennis_logging.logging_factory import setup_logging

# UI Components
from ui.utils.style_loader import load_css
from ui.display.ui_display import UIDisplay

# Agent and Processing
from agent.agent_factory import setup_langgraph_agent
from ui.formatting.consolidated_formatter import ConsolidatedFormatter
from ui.processing.query_processor import QueryProcessor

# Services
from services.database_service import DatabaseService

# --- Logging Configuration ---
# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
st.set_page_config(page_title="AskTennis AI - Clean UI", layout="wide")

# Load custom CSS from external file
st.markdown(load_css(), unsafe_allow_html=True)

# --- Agent Setup ---
# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    data_formatter = ConsolidatedFormatter()
    query_processor = QueryProcessor(data_formatter)
    db_service = DatabaseService()
    ui_display = UIDisplay()
    
    # --- Top Panel: AskTennis Search ---
    ui_display.render_search_panel()
    
    # --- Main Layout: Main Content (Filter + Results) ---
    ui_display.render_main_content(db_service, query_processor, agent_graph, logger)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()
