"""
LangGraph construction and node definitions.
Extracted from agent_setup.py for better modularity.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, SystemMessage
from datetime import datetime
from tennis_logging.logging_factory import log_tool_usage, log_database_query, log_error
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
            {"tools": "tools", "agent": "agent", "end": END}
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
            
            # Check if sql_db_query_checker was called but sql_db_query wasn't executed
            # This enforces the workflow: checker -> query execution
            checker_called = False
            query_executed = False
            
            # Check recent messages (last 10 to avoid scanning entire history)
            recent_messages = messages[-10:] if len(messages) > 10 else messages
            
            for msg in recent_messages:
                # Check if sql_db_query_checker was called
                if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        if tool_call.get('name') == 'sql_db_query_checker':
                            checker_called = True
                        elif tool_call.get('name') == 'sql_db_query':
                            query_executed = True
                
                # Check tool results (AIMessage content from tool execution)
                if isinstance(msg, AIMessage) and msg.content:
                    content_str = str(msg.content)
                    # Look for sql_db_query_checker result pattern (SQL code block)
                    if '```sqlite' in content_str or '```sql' in content_str:
                        # Extract SQL query from the code block
                        if 'SELECT' in content_str.upper():
                            checker_called = True
                    # Look for sql_db_query result pattern (list of tuples)
                    # Check for pattern like [('value1',), ('value2',)] which indicates query results
                    if content_str.startswith('[') and content_str.endswith(']') and \
                       ('(' in content_str and ')' in content_str) and \
                       len(content_str) > 50:  # Actual query results are longer than validation messages
                        query_executed = True
            
            # If checker was called but query wasn't executed, inject reminder
            # But only if we haven't already added a reminder (check for SystemMessage)
            # Also limit to prevent infinite loops (max 3 reminders)
            if checker_called and not query_executed:
                # Check if reminder was already added and count reminders
                reminder_count = 0
                for msg in messages:
                    if isinstance(msg, SystemMessage) and 'sql_db_query_checker' in str(msg.content):
                        reminder_count += 1
                
                # Only add reminder if we haven't added too many (max 3)
                if reminder_count < 3:
                    # Find the SQL query from the checker result
                    sql_query = None
                    for msg in reversed(recent_messages):
                        if isinstance(msg, AIMessage) and msg.content:
                            content_str = str(msg.content)
                            if '```sqlite' in content_str or '```sql' in content_str:
                                # Extract SQL from code block
                                lines = content_str.split('\n')
                                for line in lines:
                                    if 'SELECT' in line.upper():
                                        sql_query = line.strip().strip('`').strip()
                                        if sql_query.startswith('sqlite'):
                                            sql_query = sql_query[6:].strip()
                                        if sql_query.startswith('sql'):
                                            sql_query = sql_query[3:].strip()
                                        break
                                if sql_query:
                                    break
                    
                    reminder = SystemMessage(
                        content=f"CRITICAL: You validated a SQL query with sql_db_query_checker, but you MUST execute it with sql_db_query to get actual results before responding. Execute this query now: {sql_query if sql_query else 'the validated query'}"
                    )
                    messages = list(messages) + [reminder]
            
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
                    log_tool_usage(tool_name, tool_input, "Executing...", None)
                    
                    # Find the tool and execute it
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                start_time = datetime.now()
                                result = tool.invoke(tool_input)
                                end_time = datetime.now()
                                execution_time = (end_time - start_time).total_seconds()
                                
                                # Log tool result
                                log_tool_usage(tool_name, tool_input, result, execution_time)
                                
                                # If it's a database query, log it separately
                                if tool_name == "sql_db_query":
                                    log_database_query(
                                        tool_input.get("query", ""), 
                                        result, 
                                        execution_time
                                    )
                                
                                return {"messages": [AIMessage(content=str(result), tool_calls=[])]}
                            except Exception as e:
                                log_error(e, f"Tool execution failed: {tool_name}")
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
            messages = state["messages"]
            last_message = messages[-1]
            
            # The ReAct agent returns an AIMessage with tool_calls if it needs to act.
            if isinstance(last_message, AIMessage) and \
               hasattr(last_message, 'tool_calls') and \
               last_message.tool_calls:
                return "tools"
            
            # CRITICAL: Check if sql_db_query_checker was called but sql_db_query wasn't executed
            # This enforces the workflow: checker -> query execution
            checker_called = False
            query_executed = False
            
            # Check recent messages (last 10 to avoid scanning entire history)
            recent_messages = messages[-10:] if len(messages) > 10 else messages
            
            for msg in recent_messages:
                # Check if sql_db_query_checker was called
                if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        if tool_call.get('name') == 'sql_db_query_checker':
                            checker_called = True
                        elif tool_call.get('name') == 'sql_db_query':
                            query_executed = True
                
                # Check tool results (AIMessage content from tool execution)
                if isinstance(msg, AIMessage) and msg.content:
                    content_str = str(msg.content)
                    # Look for sql_db_query_checker result pattern (SQL code block)
                    if '```sqlite' in content_str or '```sql' in content_str:
                        if 'SELECT' in content_str.upper():
                            checker_called = True
                    # Look for sql_db_query result pattern (list of tuples)
                    if content_str.startswith('[') and content_str.endswith(']') and \
                       ('(' in content_str and ')' in content_str) and \
                       len(content_str) > 50:  # Actual results are longer
                        query_executed = True
            
            # If checker was called but query wasn't executed, route back to agent
            # The agent node will inject a reminder message
            if checker_called and not query_executed:
                return "agent"
            
            return "end"
        
        return should_continue
