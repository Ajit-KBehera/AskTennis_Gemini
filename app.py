import streamlit as st
from sqlalchemy import create_engine
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import operator

# Modern imports for LangChain & LangGraph
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
# --- NEW: Import for Google Gemini model ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate

# --- NEW: Imports for a standard ReAct Agent ---
from langgraph.checkpoint.memory import MemorySaver

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
    print("--- Initializing LangGraph Agent with Gemini ---")

    # Check for the API key in Streamlit's secrets
    try:
        # --- NEW: Using GOOGLE_API_KEY ---
        google_api_key = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("Google API key not found! Please create a `.streamlit/secrets.toml` file and add your GOOGLE_API_KEY.")
        st.stop()

    # Setup database connection and tools
    db_engine = create_engine("sqlite:///tennis_data.db")
    db = SQLDatabase(engine=db_engine)
    # --- MODEL CHANGE: Switched to Gemini 1.5 Pro ---
    # This model fully supports native tool calling, which is what create_react_agent needs.
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=google_api_key, temperature=0)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    # --- NEW: Manually create a ReAct-style prompt, removing the Hub dependency ---
    # This aligns with best practices for creating custom, reliable agents.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that can answer questions about tennis data by executing SQL queries. Use the provided tools to first understand the database schema and then write a query to answer the question.",
            ),
            ("placeholder", "{messages}"),
        ]
    )

    # --- NEW: Bind the tools to the LLM ---
    # This is the modern way to make tool-calling models aware of the tools they have.
    llm_with_tools = llm.bind_tools(tools)

    # --- Define the Nodes for the LangGraph ---

    # The 'agent' node now combines the prompt and the LLM with bound tools.
    def call_agent(state: AgentState):
        """Calls the LLM to decide the next step."""
        messages = state["messages"]
        # The `invoke` method on a runnable with bound tools will automatically
        # format the tools for the model and handle the response.
        response = llm_with_tools.invoke(prompt.format_prompt(messages=messages))
        return {"messages": [response]}

    # The 'tools' node is the pre-built ToolNode.
    tool_node = ToolNode(tools)

    def should_continue(state: AgentState):
        """Decide whether to continue with tools or finish."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the last message is an AI message with tool calls, we continue to tools.
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        # Otherwise, we're done.
        else:
            return "end"

    # --- Build the LangGraph ---
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("agent", call_agent)
    graph.add_node("tools", tool_node)
    
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
    
    # Compile the graph with memory to remember conversation history
    memory = MemorySaver()
    runnable_graph = graph.compile(checkpointer=memory)
    
    print("--- LangGraph Agent Compiled Successfully with Gemini and Custom Prompt ---")
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
            # --- UPDATED: Simplified invocation for a stateful graph ---
            # The config dictionary ensures each user gets their own conversation history.
            config = {"configurable": {"thread_id": "user_session"}}
            
            # Invoke the graph with the user's input
            response = agent_graph.invoke(
                {"messages": [HumanMessage(content=user_question)]},
                config=config
            )
            
            # The final answer is in the content of the last AIMessage.
            # We need to parse it correctly for Gemini's output format.
            last_message = response["messages"][-1]
            if isinstance(last_message.content, list) and last_message.content:
                # For Gemini, content is a list of dicts. We want the text from the first part.
                final_answer = last_message.content[0].get("text", "")
            else:
                # Fallback for standard string content
                final_answer = last_message.content

            st.success("Here's what I found:")
            st.markdown(final_answer)

            # --- Optional: Show the full conversation history for debugging ---
            with st.expander("🧠 Show Full Conversation Flow", expanded=False):
                st.json(response)

        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")
            st.error(f"Error type: {type(e).__name__}")
            import traceback
            st.error(f"Full traceback: {traceback.format_exc()}")

