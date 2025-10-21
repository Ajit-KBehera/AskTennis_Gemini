import streamlit as st

# --- Logging Configuration ---
from logging_config import (
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
from agent_setup import setup_langgraph_agent

# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()

# --- UI Components ---
from ui_components import run_main_app

# --- ML Analytics ---
from ml_analytics import TennisLogAnalyzer

# Run the main application
run_main_app(agent_graph, logger)

