# --- Third-party Imports ---
import streamlit as st 

# --- Local Application Imports ---
# Logging
from tennis_logging.simplified_factory import setup_logging, log_error

# UI Components
from ui.utils.style_loader import load_css
from ui.display.ui_display import UIDisplay

# Agent and Processing
from agent.agent_factory import setup_langgraph_agent
from utils.formatters import ConsolidatedFormatter
from services.query_service import QueryProcessor

# Services
from services.database_service import DatabaseService

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
st.set_page_config(page_title="AskTennis", layout="wide")

# Load custom CSS from external file
st.markdown(load_css(), unsafe_allow_html=True)

# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    data_formatter = ConsolidatedFormatter()
    query_processor = QueryProcessor(data_formatter)
    db_service = DatabaseService()
    ui_display = UIDisplay()
    
    # --- Main Layout: Filter Panel (Left) + Search & Results Panel (Right) ---
    ui_display.render_main_content(db_service, query_processor, agent_graph)
        
except Exception as e:
    log_error(e, "Failed to initialize the AI agent in app_ui", component="app_ui")
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()
