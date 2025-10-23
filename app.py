import streamlit as st

# --- Logging Configuration ---
from tennis_logging.logging_factory import (
    setup_logging, log_user_query, log_llm_interaction, 
    log_database_query, log_tool_usage, log_final_response, log_error
)

# Initialize logging
logger, log_file = setup_logging()

# --- Page Configuration ---
st.set_page_config(page_title="AskTennis AI", layout="wide")
st.title("🎾 AskTennis: The Advanced AI Engine")
st.markdown("#### Powered by Gemini & LangGraph (Stateful Agent)")

# --- Database Utilities ---
from database_utils import get_all_player_names, get_all_tournament_names, suggest_corrections

# --- Agent Setup ---
from agent.agent_factory import setup_langgraph_agent

# --- UI Components ---
from ui.ui_factory import run_main_app


# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
    # Run the main application
    run_main_app(agent_graph, logger)
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()

