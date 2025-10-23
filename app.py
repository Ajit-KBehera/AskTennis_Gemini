import streamlit as st

# --- Logging Configuration ---
from tennis_logging.logging_factory import setup_logging

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
from config.constants import APP_TITLE, APP_SUBTITLE
st.set_page_config(page_title="AskTennis AI", layout="wide")
st.title(APP_TITLE)
st.markdown(APP_SUBTITLE)

# --- Agent Setup ---
from agent.agent_factory import setup_langgraph_agent

# --- UI Components ---
from ui.display.ui_display import UIDisplay
from ui.formatting.data_formatter import DataFormatter
from ui.processing.query_processor import QueryProcessor


# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    
    # Initialize UI components directly
    ui_display = UIDisplay()
    data_formatter = DataFormatter()
    query_processor = QueryProcessor(data_formatter)
    
    # Run the main application
    ui_display.display_example_questions()
    user_question = ui_display.get_user_input()
    
    if user_question:
        query_processor.handle_user_query(user_question, agent_graph, logger)
        
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()

