import streamlit as st
from sqlalchemy import create_engine
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import operator

# Modern imports for LangChain & LangGraph
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_perplexity.chat_models import ChatPerplexity
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate

# --- Page Configuration ---
st.set_page_config(page_title="AskTennis AI", layout="wide")
st.title("🎾 AskTennis: The Advanced AI Engine")
st.markdown("#### Powered by Perplexity & LangGraph (Stateful Agent)")
st.markdown("This app uses a state-of-the-art AI agent to answer natural language questions about tennis data.")

# --- Define the Agent's State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# --- Database and LLM Setup (Cached for performance) ---

@st.cache_resource
def setup_langgraph_agent():
    """
    Sets up the database, LLM, tools, and compiles the LangGraph ReAct agent.
    This is cached to avoid re-initializing on every interaction.
    """
    print("--- Initializing LangGraph Agent ---")

    # Check for the API key in Streamlit's secrets
    try:
        pplx_api_key = st.secrets["PPLX_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("Perplexity API key not found! Please create a `.streamlit/secrets.toml` file and add your key.")
        st.stop()

    # Setup database connection and tools
    db_engine = create_engine("sqlite:///tennis_data.db")
    db = SQLDatabase(engine=db_engine)
    llm = ChatPerplexity(pplx_api_key=pplx_api_key, model="sonar-reasoning-pro", temperature=0)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    tool_node = ToolNode(tools)

    # Create a custom ReAct prompt that works with Perplexity
    db_schema = db.get_table_info()
    available_tools = [tool.name for tool in tools]
    system_prompt = f"""You are a helpful assistant that can answer questions about tennis data using SQL queries.

    Database Schema:
    {db_schema}

    Available Tools: {available_tools}

    You have access to SQL tools to query the database. When answering questions:
    1. Think step by step about what information you need
    2. Use the available SQL tools to query the database
    3. Analyze the results and provide a clear, helpful answer
    4. If you need to make multiple queries, do so systematically

    IMPORTANT: You MUST use the SQL tools to answer questions. Do not provide general answers without querying the database.

    To use a tool, respond with EXACTLY this format:
    TOOL: sql_db_query
    INPUT: SELECT COUNT(*) FROM matches;

    When you have enough information to answer the question, respond with:
    FINAL_ANSWER: your answer"""

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # --- Define the Nodes for the LangGraph ---

    def call_model(state: AgentState):
        """Call the LLM with the current state"""
        messages = state["messages"]
        # Get the last human message as input
        human_input = messages[-1].content if messages else ""
        
        # Create the full prompt with proper agent_scratchpad
        prompt_text = prompt.format(input=human_input, agent_scratchpad=[])
        
        # Get LLM response
        response = llm.invoke(prompt_text)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse the response to determine if it's a tool call or final answer
        if "TOOL:" in response_text and "INPUT:" in response_text:
            # Extract tool name and input
            import re
            tool_match = re.search(r"TOOL:\s*(\w+)\s*\nINPUT:\s*(.+)", response_text, re.DOTALL)
            if tool_match:
                tool_name = tool_match.group(1).strip()
                tool_input = tool_match.group(2).strip()
                
                # Validate that we have actual tool name and input
                if tool_name != "tool_name" and tool_input != "tool_input":
                    # Create a tool message
                    tool_message = ToolMessage(
                        content=f"Tool call: {tool_name} with input: {tool_input}",
                        tool_call_id=f"{tool_name}_{len(messages)}"
                    )
                    return {"messages": [tool_message]}
        
        # If it's a final answer, extract it
        if "FINAL_ANSWER:" in response_text:
            import re
            answer_match = re.search(r"FINAL_ANSWER:\s*(.+)", response_text, re.DOTALL)
            if answer_match:
                final_answer = answer_match.group(1).strip()
                ai_message = AIMessage(content=final_answer)
                return {"messages": [ai_message]}
        
        # If it's a regular response, return as is
        ai_message = AIMessage(content=response_text)
        return {"messages": [ai_message]}

    def should_continue(state: AgentState):
        """Decide whether to continue with tools or finish"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the last message is a tool message, continue to tools
        if isinstance(last_message, ToolMessage):
            return "tools"
        # If it's an AI message with tool call, continue to tools
        elif hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        # Otherwise, we're done
        else:
            return "end"

    def execute_tools(state: AgentState):
        """Execute the tools based on the last message"""
        messages = state["messages"]
        last_message = messages[-1]
        
        if isinstance(last_message, ToolMessage):
            # Extract tool name and input from the tool message
            content = last_message.content
            if "Tool call:" in content:
                # Parse the tool call
                import re
                tool_match = re.search(r"Tool call:\s*(\w+)\s*with input:\s*(.+)", content)
                if tool_match:
                    tool_name = tool_match.group(1).strip()
                    tool_input = tool_match.group(2).strip()
                    
                    # Find and execute the tool
                    tool_lookup = {tool.name: tool for tool in tools}
                    if tool_name in tool_lookup:
                        try:
                            tool = tool_lookup[tool_name]
                            result = tool.invoke(tool_input)
                            # Create a tool result message
                            tool_result = ToolMessage(
                                content=str(result),
                                tool_call_id=last_message.tool_call_id
                            )
                            return {"messages": [tool_result]}
                        except Exception as e:
                            error_result = ToolMessage(
                                content=f"Error executing {tool_name}: {str(e)}",
                                tool_call_id=last_message.tool_call_id
                            )
                            return {"messages": [error_result]}
                    else:
                        # Try to find a tool that matches the pattern
                        for tool in tools:
                            if tool_name.lower() in tool.name.lower() or "sql" in tool.name.lower():
                                try:
                                    result = tool.invoke(tool_input)
                                    tool_result = ToolMessage(
                                        content=str(result),
                                        tool_call_id=last_message.tool_call_id
                                    )
                                    return {"messages": [tool_result]}
                                except Exception as e:
                                    error_result = ToolMessage(
                                        content=f"Error executing {tool.name}: {str(e)}",
                                        tool_call_id=last_message.tool_call_id
                                    )
                                    return {"messages": [error_result]}
        
        return {"messages": []}

    # --- Build the LangGraph ---
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("agent", call_model)
    graph.add_node("tools", execute_tools)
    
    # Set entry point
    graph.set_entry_point("agent")
    
    # Add conditional edges
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Add edge from tools back to agent
    graph.add_edge("tools", "agent")
    
    # Compile the graph
    runnable_graph = graph.compile()
    
    print("--- LangGraph Agent Compiled Successfully ---")
    return runnable_graph

# Initialize the LangGraph agent
try:
    agent_graph = setup_langgraph_agent()
except Exception as e:
    st.error(f"Failed to initialize the AI agent: {e}")
    st.stop()

# --- Main App UI & Logic ---

st.markdown("##### Example Questions:")
st.markdown("""
- *How many matches did Roger Federer win in 2006?*
- *Who won the most matches on clay in 2010?*
- *What was the score of the Wimbledon final in 2008?*
""")

user_question = st.text_input(
    "Ask your tennis question:",
    placeholder="e.g., 'How many tournaments did Serena Williams win on hard court?'"
)

if user_question:
    with st.spinner("The AI is analyzing your question and querying the database..."):
        try:
            # Invoke the LangGraph with the user's input
            response = agent_graph.invoke({
                "messages": [HumanMessage(content=user_question)]
            })
            
            # Extract the final answer from the response
            if "messages" in response and response["messages"]:
                # Get the last AI message (final answer)
                ai_messages = [msg for msg in response["messages"] if isinstance(msg, AIMessage)]
                if ai_messages:
                    answer = ai_messages[-1].content
                else:
                    # Fallback to last message
                    answer = str(response["messages"][-1].content)
            else:
                answer = str(response)
            
            # Parse thinking and final answer
            thinking_content = ""
            final_answer = answer
            
            if "<think>" in answer and "</think>" in answer:
                import re
                thinking_match = re.search(r"<think>(.*?)</think>", answer, re.DOTALL)
                if thinking_match:
                    thinking_content = thinking_match.group(1).strip()
                    # Remove thinking from final answer
                    final_answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
            
            st.success("Here's what I found:")
            st.markdown(final_answer)
            
            # Show thinking section if present
            if thinking_content:
                with st.expander("🧠 Show AI Thinking Process", expanded=False):
                    st.markdown(thinking_content)

        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")
            st.error(f"Error type: {type(e).__name__}")
            import traceback
            st.error(f"Full traceback: {traceback.format_exc()}")

