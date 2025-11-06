"""
LangGraph construction and node definitions.
Extracted from agent_setup.py for better modularity.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from datetime import datetime
from tennis_logging.simplified_factory import log_tool_usage, log_database_query, log_error
from agent.agent_state import AgentState
from typing import List, Any


class LangGraphBuilder:
    """
    Builder class for constructing the LangGraph agent.
    Centralizes all graph construction logic.
    
    Method execution order:
    1. __init__() - Initialize the graph builder
    2. build_graph() - Main entry point, builds and compiles the graph
    3. create_agent_node() - Creates agent node (called by build_graph)
    4. create_tool_node() - Creates tool node (called by build_graph)
    5. create_conditional_edges() - Creates routing logic (called by build_graph)
    """
    
    def __init__(self, tools: List[Any], llm_with_tools, prompt):
        """
        Initialize the graph builder.
        
        Args:
            tools: List of tools available to the agent
            llm_with_tools: LLM instance with bound tools
            prompt: Prompt template for the agent
        """
        self.tools = tools
        self.llm_with_tools = llm_with_tools
        self.prompt = prompt
    
    def build_graph(self):
        """
        Build the complete LangGraph.
        
        Returns:
            Compiled LangGraph instance
        """
        # Create the graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("agent", self.create_agent_node())
        graph.add_node("tools", self.create_tool_node())
        
        # Set entry point
        graph.set_entry_point("agent")
        
        # Add conditional edges
        graph.add_conditional_edges(
            "agent", 
            self.create_conditional_edges(), 
            {"tools": "tools", "end": END}
        )
        
        # Add edge from tools back to agent
        graph.add_edge("tools", "agent")
        
        # Compile with memory
        memory = MemorySaver()
        runnable_graph = graph.compile(checkpointer=memory)
        
        return runnable_graph
    
    def create_agent_node(self):
        """
        Create the agent node that calls the LLM.
        
        Returns:
            Agent node function
        """
        def call_agent(state: AgentState):
            """Calls the LLM to decide the next step."""
            messages = state["messages"]
            response = self.llm_with_tools.invoke(
                self.prompt.format_prompt(messages=messages)
            )
            return {"messages": [response]}
        
        return call_agent
    
    def create_tool_node(self):
        """
        Create the tool node that executes tools with logging.
        
        Returns:
            Tool node function
        """
        def logged_tool_node(state: AgentState):
            """Custom tool node that logs tool usage."""
            messages = state["messages"]
            last_message = messages[-1]
            
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    tool_name = tool_call["name"]
                    tool_input = tool_call["args"]
                    
                    # Log tool usage start
                    log_tool_usage(tool_name, tool_input, "Executing...", None, component="langgraph_builder")
                    
                    # Find the tool and execute it
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                start_time = datetime.now()
                                result = tool.invoke(tool_input)
                                end_time = datetime.now()
                                execution_time = (end_time - start_time).total_seconds()
                                
                                # Log tool result
                                log_tool_usage(tool_name, tool_input, result, execution_time, component="langgraph_builder")
                                
                                # If it's a database query, log it separately
                                if tool_name == "sql_db_query":
                                    log_database_query(
                                        tool_input.get("query", ""), 
                                        result, 
                                        execution_time,
                                        component="langgraph_builder"
                                    )
                                
                                return {"messages": [AIMessage(content=str(result), tool_calls=[])]}
                            except Exception as e:
                                log_error(e, f"Tool execution failed: {tool_name}", component="langgraph_builder")
                                return {
                                    "messages": [
                                        AIMessage(
                                            content=f"Error executing {tool_name}: {str(e)}", 
                                            tool_calls=[]
                                        )
                                    ]
                                }
            
            return {"messages": []}
        
        return logged_tool_node
    
    def create_conditional_edges(self):
        """
        Create the conditional edges function for the graph.
        
        Returns:
            Conditional edges function
        """
        def should_continue(state: AgentState):
            """Decide whether to continue with tools or finish."""
            # The ReAct agent returns an AIMessage with tool_calls if it needs to act.
            if isinstance(state["messages"][-1], AIMessage) and \
               hasattr(state["messages"][-1], 'tool_calls') and \
               state["messages"][-1].tool_calls:
                return "tools"
            return "end"
        
        return should_continue
