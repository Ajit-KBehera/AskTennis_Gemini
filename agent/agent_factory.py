"""
Main factory for creating and configuring the tennis AI agent.
Orchestrates all components to create the complete LangGraph agent.
"""

import streamlit as st
from agent.agent_state import AgentState
from agent.agent_config import AgentConfigManager
from llm.llm_setup import LLMFactory
from tennis.tennis_core import TennisMappingTools, TennisPromptBuilder, PerformanceMonitor
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
    config_manager = AgentConfigManager()
    
    # Validate configuration
    if not config_manager.validate_config():
        st.error("Invalid configuration detected!")
        st.stop()
    
    # Setup LLM and database components
    llm_config = config_manager.get_llm_config()
    db_config = config_manager.get_database_config()
    
    # Create LLM components
    llm, db, toolkit = LLMFactory.setup_llm_components({
        **llm_config,
        **db_config
    })
    
    # Get base tools from toolkit
    base_tools = toolkit.get_tools()
    
    # Add cached tennis mapping tools for better performance
    tennis_tools = TennisMappingTools.create_all_mapping_tools()
    
    # Note: Optimized database tools removed to prevent infinite loops
    # The original sql_db_query tool from base_tools is sufficient
    
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


class AgentFactory:
    """
    Factory class for creating tennis AI agents.
    Provides alternative methods for agent creation.
    """
    
    @staticmethod
    def create_agent_with_custom_config(config: dict):
        """
        Create an agent with custom configuration.
        
        Args:
            config: Custom configuration dictionary
            
        Returns:
            Compiled LangGraph agent
        """
        # Create LLM components with custom config
        llm, db, toolkit = LLMFactory.setup_llm_components(config)
        
        # Get tools
        base_tools = toolkit.get_tools()
        tennis_tools = TennisMappingTools.create_all_mapping_tools()
        # Note: Optimized database tools removed to prevent infinite loops
        all_tools = base_tools + tennis_tools
        
        # Create optimized prompt
        db_schema = db.get_table_info()
        system_prompt = TennisPromptBuilder.create_system_prompt(db_schema)
        prompt = TennisPromptBuilder.create_optimized_prompt_template(system_prompt)
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(all_tools)
        
        # Build graph
        graph_builder = LangGraphBuilder(all_tools, llm_with_tools, prompt)
        return graph_builder.build_graph()
    
    @staticmethod
    def create_agent_with_custom_tools(tools: list):
        """
        Create an agent with custom tools.
        
        Args:
            tools: List of custom tools
            
        Returns:
            Compiled LangGraph agent
        """
        # Load default configuration
        config_manager = AgentConfigManager()
        
        # Setup LLM components
        llm_config = config_manager.get_llm_config()
        db_config = config_manager.get_database_config()
        
        llm, db, toolkit = LLMFactory.setup_llm_components({
            **llm_config,
            **db_config
        })
        
        # Use custom tools
        all_tools = tools
        
        # Create optimized prompt
        db_schema = db.get_table_info()
        system_prompt = TennisPromptBuilder.create_system_prompt(db_schema)
        prompt = TennisPromptBuilder.create_optimized_prompt_template(system_prompt)
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(all_tools)
        
        # Build graph
        graph_builder = LangGraphBuilder(all_tools, llm_with_tools, prompt)
        return graph_builder.build_graph()
