import streamlit as st  # pyright: ignore[reportMissingImports]

# --- Logging Configuration ---
from tennis_logging.logging_factory import setup_logging

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
from constants import APP_TITLE, APP_SUBTITLE

st.set_page_config(page_title="AskTennis AI-Basic", layout="wide")
st.title(APP_TITLE)
st.markdown(APP_SUBTITLE)

# --- Agent Setup ---
from agent.agent_factory import setup_langgraph_agent

# --- UI Components ---
from ui.display.ui_display import UIDisplay
from ui.formatting.consolidated_formatter import ConsolidatedFormatter
from ui.processing.query_processor import QueryProcessor

# Services
from services.database_service import DatabaseService


# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    data_formatter = ConsolidatedFormatter()
    query_processor = QueryProcessor(data_formatter)
    db_service = DatabaseService()
    ui_display = UIDisplay()
    
    # --- Top Panel: AskTennis Search ---
    ui_display.render_search_panel()
    
    # --- Results Panel: Process and Display Query Results ---
    ui_display.render_results_panel(query_processor, agent_graph, logger, db_service)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()

