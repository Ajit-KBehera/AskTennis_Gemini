import streamlit as st
from sqlalchemy import create_engine
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import pandas as pd
from difflib import get_close_matches
import sqlite3
import logging
import json
import os
from datetime import datetime
import uuid

# Modern imports for LangChain & LangGraph
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
# Removed create_react_agent import - using custom agent pattern instead
from langgraph.checkpoint.memory import MemorySaver

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
st.markdown("This app uses a state-of-the-art AI agent to answer natural language questions about tennis data.")

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

# Run the main application
run_main_app(agent_graph, logger)

