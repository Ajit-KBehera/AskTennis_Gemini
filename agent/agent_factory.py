"""
Main factory for creating and configuring the tennis AI agent.
Orchestrates all components to create the complete LangGraph agent.
"""

import streamlit as st
from config.config import Config
from llm.llm_setup import LLMFactory
from tennis.tennis_core import TennisMappingTools, TennisPromptBuilder
from graph.langgraph_builder import LangGraphBuilder


@st.cache_resource
def setup_langgraph_agent():
    """
    Main factory function to create the complete LangGraph agent.
    This is cached to avoid re-initializing on every interaction.
    
    Returns:
        Compiled LangGraph agent ready for use
    """
    print("--- Initializing LangGraph Agent with Gemini ---")
    
    # Load configuration
    config = Config()
    
    # Validate configuration
    if not config.validate_config():
        st.error("Invalid configuration detected!")
        st.stop()
    
    # Get LLM configuration
    llm_config = config.get_llm_config()

    # Get database configuration
    db_config = config.get_database_config()
    
    # Create LLM components
    llm, db, toolkit = LLMFactory.setup_llm_components({
        **llm_config,
        **db_config
    })
    
    # Get base tools from toolkit
    base_tools = toolkit.get_tools()
    
    # Add cached tennis mapping tools for better performance
    tennis_tools = TennisMappingTools.create_all_mapping_tools()
    all_tools = base_tools + tennis_tools
    
    # Create optimized prompt
    db_schema = db.get_table_info()
    system_prompt = TennisPromptBuilder.create_system_prompt(db_schema)
    prompt = TennisPromptBuilder.create_optimized_prompt_template(system_prompt)
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(all_tools)
    
    # Build graph
    graph_builder = LangGraphBuilder(all_tools, llm_with_tools, prompt)
    runnable_graph = graph_builder.build_graph()
    
    print("--- LangGraph Agent Compiled Successfully with Gemini ---")
    return runnable_graph


# Removed redundant AgentFactory class - using direct setup_langgraph_agent() function
