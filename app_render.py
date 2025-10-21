#!/usr/bin/env python3
"""
AskTennis App configured for Render PostgreSQL deployment
"""

import streamlit as st
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, ToolMessage
import json

# Configure Streamlit page
st.set_page_config(
    page_title="AskTennis - AI Tennis Database Assistant",
    page_icon="🎾",
    layout="wide"
)

# Database connection for Render
def get_database_connection():
    """
    Get database connection for Render PostgreSQL
    """
    try:
        # Option 1: Use Render's DATABASE_URL environment variable
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Render provides DATABASE_URL in format: postgresql://user:pass@host:port/db
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            engine = create_engine(database_url)
            return engine
        
        # Option 2: Manual connection (for local testing)
        else:
            # Replace with your Render database credentials
            engine = create_engine(
                "postgresql://username:password@hostname:port/database_name"
            )
            return engine
            
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Initialize database
@st.cache_resource
def setup_database():
    """Setup database connection"""
    engine = get_database_connection()
    if engine:
        return SQLDatabase(engine)
    return None

# Initialize the database
db = setup_database()

if db is None:
    st.error("❌ Failed to connect to database. Please check your Render database configuration.")
    st.stop()

# Initialize Google Gemini
@st.cache_resource
def setup_langgraph_agent():
    """Setup the LangGraph agent with Google Gemini"""
    
    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )
    
    # Create SQL query tool
    sql_query_tool = QuerySQLDataBaseTool(db=db)
    
    # Enhanced system prompt for tennis database
    system_prompt = """
    You are an expert tennis database analyst with access to a comprehensive tennis database.
    
    DATABASE SCHEMA:
    - matches: Individual match results with winner/loser info, rankings, scores, dates
    - players: Player information and statistics  
    - rankings: Historical ranking data
    - doubles_matches: Doubles match results
    
    KEY COLUMNS IN MATCHES TABLE:
    - winner_name, loser_name: Player names
    - winner_rank, loser_rank: Rankings at time of match
    - tourney_name: Tournament name
    - event_year, event_month, event_date: Match date
    - surface: Court surface (Hard, Clay, Grass, Carpet)
    - round: Match round (F, SF, QF, R16, etc.)
    - set1, set2, set3, set4, set5: Set scores
    - tourney_level: Tournament level (A=ATP Main, G=Grand Slam, W=WTA Main, etc.)
    - tournament_type: Tour type (Main_Tour, ATP_Futures, ATP_Qual_Chall, WTA_Qual_ITF)
    
    QUERY GUIDELINES:
    1. Always use proper SQL syntax for PostgreSQL
    2. Use ILIKE for case-insensitive text searches
    3. Use proper date filtering with event_year, event_month, event_date
    4. For head-to-head queries, use both match directions
    5. Exclude walkover matches (set1 != 'W/O')
    
    RESPONSE FORMAT:
    - Provide clear, accurate answers
    - Include relevant statistics and context
    - For head-to-head queries, show detailed match results
    """
    
    def should_continue(state):
        """Determine if we should continue or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        if last_message.type == "tool":
            return "continue"
        else:
            return "end"
    
    def call_model(state):
        """Call the language model"""
        messages = state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}
    
    def call_tool(state):
        """Call the SQL tool"""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_call = last_message.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        if tool_name == "sql_db_query":
            result = sql_query_tool.run(tool_args["query"])
            return {"messages": [ToolMessage(content=str(result), tool_call_id=tool_call["id"])]}
    
    # Create the graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tool)
    
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")
    
    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Define state
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "The messages in the conversation"]

# Initialize the agent
agent_graph = setup_langgraph_agent()

# Streamlit UI
st.title("🎾 AskTennis - AI Tennis Database Assistant")
st.markdown("Ask questions about tennis matches, players, tournaments, and statistics!")

# Example questions
with st.expander("💡 Example Questions", expanded=False):
    st.markdown("""
    **Player Statistics:**
    - How many matches did Roger Federer win in 2006?
    - Who won the most matches on clay in 2010?
    - What was the score of the Wimbledon final in 2008?
    
    **Head-to-Head Records:**
    - What is the head-to-head record between Serena Williams and Maria Sharapova?
    - Show me all matches between Rafael Nadal and Novak Djokovic
    
    **Tournament Analysis:**
    - How many Grand Slam titles did Serena Williams win?
    - Which players won the most matches at Wimbledon?
    - Compare ATP vs WTA match statistics
    """)

# Create persistent placeholder for dataframe display
dataframe_placeholder = st.empty()

user_question = st.text_input(
    "Ask your tennis question:",
    placeholder="e.g., 'How many tournaments did Serena Williams win on hard court?'"
)

if user_question:
    with st.spinner("The AI is analyzing your question and querying the database..."):
        try:
            # The config dictionary ensures each user gets their own conversation history.
            config = {"configurable": {"thread_id": "user_session"}}
            
            # Invoke the agent
            response = agent_graph.invoke(
                {"messages": [HumanMessage(content=user_question)]},
                config=config
            )
            
            # Parse response
            last_message = response["messages"][-1]
            if isinstance(last_message.content, list) and last_message.content:
                final_answer = last_message.content[0].get("text", "")
            else:
                final_answer = last_message.content
            
            # Handle head-to-head queries with dataframe display
            if 'h2h' in user_question.lower() or 'head to head' in user_question.lower() or 'vs' in user_question.lower():
                # Look for detailed match data in tool messages
                for message in response["messages"]:
                    if hasattr(message, 'type') and message.type == 'tool' and 'sql_db_query' in str(message.name):
                        try:
                            import ast
                            if message.content.startswith('[') and message.content.endswith(']'):
                                data = ast.literal_eval(message.content)
                                if data and len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) > 3:
                                    # Display detailed match data
                                    with dataframe_placeholder.container():
                                        st.markdown("### 📊 Detailed Head-to-Head Matches")
                                        
                                        # Convert to DataFrame
                                        df_data = []
                                        for row in data:
                                            if len(row) >= 4:
                                                set_scores = []
                                                for i in range(7, min(len(row), 12)):
                                                    if i < len(row) and row[i] and str(row[i]).strip() and str(row[i]).strip() != 'None':
                                                        set_scores.append(str(row[i]).strip())
                                                
                                                score_str = ' '.join(set_scores) if set_scores else 'N/A'
                                                
                                                df_data.append({
                                                    'Winner': row[0],
                                                    'Loser': row[1], 
                                                    'Tournament': row[2],
                                                    'Year': row[3],
                                                    'Surface': row[6] if len(row) > 6 else 'N/A',
                                                    'Score': score_str
                                                })
                                        
                                        if df_data:
                                            df = pd.DataFrame(df_data)
                                            st.dataframe(
                                                df, 
                                                use_container_width=True,
                                                column_config={
                                                    "Winner": st.column_config.TextColumn("Winner", width="medium"),
                                                    "Loser": st.column_config.TextColumn("Loser", width="medium"),
                                                    "Tournament": st.column_config.TextColumn("Tournament", width="large"),
                                                    "Year": st.column_config.TextColumn("Year", width="small"),
                                                    "Surface": st.column_config.TextColumn("Surface", width="small"),
                                                    "Score": st.column_config.TextColumn("Score", width="medium")
                                                }
                                            )
                                        else:
                                            st.warning("No detailed match data found in the expected format.")
                                    break
                        except:
                            continue
            else:
                # Clear the dataframe placeholder for non-head-to-head queries
                dataframe_placeholder.empty()
            
            if final_answer and final_answer.strip():
                st.success("Here's what I found:")
                st.markdown(final_answer)
            else:
                st.warning("I processed your request but couldn't generate a clear response.")
                
        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")

# Footer
st.markdown("---")
st.markdown("**Powered by Google Gemini AI and Render PostgreSQL** 🚀")
