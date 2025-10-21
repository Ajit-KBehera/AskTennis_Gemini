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
def setup_logging():
    """Setup comprehensive logging for AI LLM and database interactions."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Use session state to maintain consistent logging across reruns
    if 'tennis_logger_session_id' not in st.session_state:
        st.session_state.tennis_logger_session_id = str(uuid.uuid4())[:8]
        st.session_state.tennis_logger_initialized = False
    
    session_id = st.session_state.tennis_logger_session_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/asktennis_ai_interaction_{timestamp}_{session_id}.log"
    
    # Only configure logging once per session
    if not st.session_state.tennis_logger_initialized:
        # Clear any existing handlers to avoid duplicates
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8')
                # Removed StreamHandler to prevent terminal printing
            ],
            force=True  # Force reconfiguration
        )
        
        st.session_state.tennis_logger_initialized = True
        st.session_state.tennis_log_file = log_filename
    
    return logging.getLogger(__name__), st.session_state.tennis_log_file

# Initialize logging
logger, log_file = setup_logging()

def log_user_query(query, session_id=None):
    """Log the user's input query."""
    logger.info(f"=== USER QUERY START ===")
    logger.info(f"Query: {query}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    if session_id:
        logger.info(f"Session ID: {session_id}")
    logger.info(f"=== USER QUERY END ===")

def log_llm_interaction(messages, interaction_type="LLM_CALL"):
    """Log LLM interactions and responses."""
    logger.info(f"=== {interaction_type} START ===")
    for i, message in enumerate(messages):
        if isinstance(message, HumanMessage):
            logger.info(f"Human Message {i+1}: {message.content}")
        elif isinstance(message, AIMessage):
            logger.info(f"AI Message {i+1}: {message.content}")
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info(f"Tool Calls: {[tool_call for tool_call in message.tool_calls]}")
        else:
            logger.info(f"Message {i+1} ({type(message).__name__}): {message.content}")
    logger.info(f"=== {interaction_type} END ===")

def log_database_query(sql_query, results, execution_time=None):
    """Log database queries and results."""
    logger.info(f"=== DATABASE QUERY START ===")
    logger.info(f"SQL Query: {sql_query}")
    if execution_time:
        logger.info(f"Execution Time: {execution_time:.3f} seconds")
    logger.info(f"Results Count: {len(results) if results else 0}")
    if results and len(results) > 0:
        logger.info(f"Sample Results: {results[:3]}")  # Log first 3 results
    logger.info(f"=== DATABASE QUERY END ===")

def log_tool_usage(tool_name, tool_input, tool_output, execution_time=None):
    """Log tool usage and results."""
    logger.info(f"=== TOOL USAGE START ===")
    logger.info(f"Tool: {tool_name}")
    logger.info(f"Input: {tool_input}")
    logger.info(f"Output: {tool_output}")
    if execution_time:
        logger.info(f"Execution Time: {execution_time:.3f} seconds")
    logger.info(f"=== TOOL USAGE END ===")

def log_final_response(response, processing_time=None):
    """Log the final response to the user."""
    logger.info(f"=== FINAL RESPONSE START ===")
    logger.info(f"Response: {response}")
    if processing_time:
        logger.info(f"Total Processing Time: {processing_time:.3f} seconds")
    logger.info(f"=== FINAL RESPONSE END ===")

def log_error(error, context=""):
    """Log errors with context."""
    logger.error(f"=== ERROR START ===")
    logger.error(f"Context: {context}")
    logger.error(f"Error: {str(error)}")
    logger.error(f"=== ERROR END ===")

# --- Page Configuration ---
st.set_page_config(page_title="AskTennis AI", layout="wide")
st.title("🎾 AskTennis: The Advanced AI Engine")
st.markdown("#### Powered by Gemini & LangGraph (Stateful Agent)")
st.markdown("This app uses a state-of-the-art AI agent to answer natural language questions about tennis data.")

# --- Define the Agent's State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# --- Helper Functions for Misspelling Handling ---
@st.cache_data
def get_all_player_names():
    """Get all unique player names from the database for fuzzy matching."""
    conn = sqlite3.connect("tennis_data.db")
    cursor = conn.cursor()
    
    # Get all unique winner and loser names
    cursor.execute("SELECT DISTINCT winner_name FROM matches WHERE winner_name IS NOT NULL")
    winner_names = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT loser_name FROM matches WHERE loser_name IS NOT NULL")
    loser_names = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Combine and deduplicate
    all_names = list(set(winner_names + loser_names))
    return all_names

@st.cache_data
def get_all_tournament_names():
    """Get all unique tournament names from the database for fuzzy matching."""
    conn = sqlite3.connect("tennis_data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT tourney_name FROM matches WHERE tourney_name IS NOT NULL")
    tournament_names = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return tournament_names

def suggest_corrections(query_name, name_type="player"):
    """Suggest corrections for misspelled names."""
    if name_type == "player":
        all_names = get_all_player_names()
    else:
        all_names = get_all_tournament_names()
    
    # Find close matches
    close_matches = get_close_matches(query_name, all_names, n=3, cutoff=0.6)
    
    if close_matches:
        return f"Did you mean: {', '.join(close_matches)}?"
    else:
        return f"No similar {name_type} names found. Please check your spelling."


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
        google_api_key = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("Google API key not found! Please create a `.streamlit/secrets.toml` file and add your GOOGLE_API_KEY.")
        st.stop()

    # Setup database connection and tools
    db_engine = create_engine("sqlite:///tennis_data.db")
    db = SQLDatabase(engine=db_engine)
    # --- REFINEMENT 1: Use the official, version-stable model name ---
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=google_api_key, temperature=0)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    
    # --- Custom agent pattern using llm.bind_tools() ---
    # This is the modern approach for tool-calling models like Gemini
    db_schema = db.get_table_info()
    system_prompt = f"""You are a helpful assistant designed to answer questions about tennis matches by querying a SQL database.
    Here is the schema for the `matches` table you can query:
    {db_schema}
    
    ENHANCED DATABASE FEATURES:
    - The database now includes a `players` table with player metadata (handedness, nationality, height, birth date, etc.)
    - The database includes a `rankings` table with historical ranking data (1973-2024, 5.3M+ records)
    - The database includes COMPLETE TOURNAMENT COVERAGE (1877-2024, 1.7M+ matches)
    - The database includes a `doubles_matches` table with doubles match data (2000-2020, 26K+ matches)
    - Use `matches_with_full_info` view for queries that need player details
    - Use `matches_with_rankings` view for queries that need ranking context
    - Use `player_rankings_history` view for ranking analysis
    - Available player fields: winner_hand, winner_ioc, winner_height, winner_dob, loser_hand, loser_ioc, loser_height, loser_dob
    - Available ranking fields: winner_rank_at_time, winner_points_at_time, loser_rank_at_time, loser_points_at_time
    - Era classification: Amateur (1877-1967), Professional (1968-2024)
    - Tournament types: Main_Tour, ATP_Qual_Chall, ATP_Futures, WTA_Qual_ITF
    - Match types: Singles (matches table), Doubles (doubles_matches table)
    - Historical coverage: 147 years of complete tennis history (1877-2024)
    
    CRITICAL INSTRUCTIONS:
    - To answer questions, you MUST use the sql_db_query tool to execute your SQL query and get results.
    - Do NOT use sql_db_query_checker - that only validates queries but doesn't return data.
    - After getting query results with sql_db_query, analyze the results and provide a clear, natural language answer.
    - Always provide a final response to the user, even if the query returns no results.
    - Do not make up information. If the database does not contain the answer, say so.
    
    MISSPELLING HANDLING:
    - If a query returns no results, try fuzzy matching with LIKE patterns and common misspellings.
    - For player names, try variations: partial names, common nicknames, and similar spellings.
    - For tournament names, try partial matches and common abbreviations.
    - If still no results, suggest similar names found in the database.
    - Always be helpful and suggest corrections when possible.
    
    SPECIAL INSTRUCTIONS FOR HEAD-TO-HEAD QUERIES:
    - For head-to-head questions (e.g., "Player A vs Player B h2h"), provide both a summary AND detailed match information.
    - ALWAYS include the surface column in your SQL queries for head-to-head matches.
    - Use this query format: SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, surface, set1, set2, set3, set4, set5 FROM matches WHERE...
    - Include match details like year, tournament, surface, score, and winner.
    - Format the response to show both the overall record and individual match details.
    
    CRITICAL HEAD-TO-HEAD COUNTING RULES:
    - Count ONLY completed matches (exclude W/O, DEF, RET matches from head-to-head records)
    - Double-check your counting: count wins for each player separately
    - Verify your count matches the number of matches displayed in the table
    - If you find W/O, DEF, or RET in the score, exclude that match from the head-to-head record
    - Always state the correct win-loss record in your summary
    - Example: "Player A leads Player B 15-3" (not counting walkovers)
    
    PLAYER METADATA QUERIES:
    - For questions about player characteristics (handedness, nationality, height, age), use the `matches_with_full_info` view
    - Example: "Which left-handed players won the most matches?" - use winner_hand = 'L'
    - Example: "How many matches did Spanish players win?" - use winner_ioc = 'ESP'
    - Example: "Who are the tallest players?" - use winner_height or loser_height columns
    
    RANKINGS QUERIES:
    - For questions about player rankings, use the `player_rankings_history` view
    - For questions about matches with ranking context, use the `matches_with_rankings` view
    - Example: "Who was ranked #1 in 2020?" - use player_rankings_history WHERE rank = 1 AND ranking_date LIKE '2020%'
    - Example: "Which top 10 players won the most matches?" - use matches_with_rankings WHERE winner_rank_at_time <= 10
    - Example: "How many upsets happened in Grand Slams?" - use matches_with_rankings WHERE winner_rank_at_time > loser_rank_at_time
    - Example: "Who had the highest ranking points?" - use player_rankings_history ORDER BY points DESC
    
    HISTORICAL QUERIES:
    - For questions about tennis history, use the COMPLETE historical database (1877-2024)
    - Example: "Who won the first Wimbledon in 1877?" - use matches WHERE tourney_name LIKE '%Wimbledon%' AND event_year = 1877
    - Example: "Who won Wimbledon in 1970?" - use matches WHERE tourney_name LIKE '%Wimbledon%' AND event_year = 1970
    - Example: "How many matches were played in the 1980s?" - use matches WHERE event_year BETWEEN 1980 AND 1989
    - Example: "Which players dominated the 1990s?" - use matches WHERE event_year BETWEEN 1990 AND 1999
    - Example: "Compare amateur vs professional eras" - use era column to filter Amateur vs Professional
    - Example: "Compare tennis evolution across decades" - use decade-based analysis with event_year
    
    TOURNAMENT TYPE QUERIES:
    - For questions about different tournament levels, use the tournament_type column
    - Example: "How many Challenger matches were played?" - use matches WHERE tournament_type = 'ATP_Qual_Chall'
    - Example: "Which players won the most Futures matches?" - use matches WHERE tournament_type = 'ATP_Futures'
    - Example: "Compare main tour vs qualifying results" - use tournament_type to filter Main_Tour vs ATP_Qual_Chall
    - Example: "How many ITF matches were played by women?" - use matches WHERE tournament_type = 'WTA_Qual_ITF'
    - Example: "Which tournament level has the most matches?" - use GROUP BY tournament_type
    
    DOUBLES MATCH QUERIES:
    - For questions about doubles matches, use the `doubles_matches` table
    - Doubles table has 4 players: winner1_name, winner2_name, loser1_name, loser2_name
    - Example: "How many doubles matches were played?" - use SELECT COUNT(*) FROM doubles_matches
    - Example: "Which doubles team won the most matches?" - use GROUP BY winner1_name, winner2_name
    - Example: "Who are the most successful doubles players?" - use winner1_name, winner2_name, loser1_name, loser2_name
    - Example: "Doubles matches by surface" - use SELECT surface, COUNT(*) FROM doubles_matches GROUP BY surface
    - Example: "Recent doubles champions" - use ORDER BY event_year DESC, event_month DESC, event_date DESC
    
    COMPLEX STREAK ANALYSIS (Gaps and Islands):
    - For complex streak questions (e.g., "consecutive upsets"), you must first use a CTE with LAG() to identify "streak breaks" and then a second CTE with SUM() OVER... to create a 'group_id' for each streak.
    - Example Q: "Find consecutive upset streaks of 6+ matches where a lower-ranked player beats a specific higher-ranked player every time."
    - Example SQL Logic:
      WITH ...
      streak_groups AS (
        SELECT
          *,
          -- Flag a 'break' if the winner changes OR it's not an upset
          CASE
            WHEN (winner_rank > loser_rank) = 0 THEN 1 -- Not an upset
            WHEN winner_id != LAG(winner_id) OVER (PARTITION BY player1_id, player2_id ORDER BY match_date) AND LAG(winner_id) OVER (PARTITION BY player1_id, player2_id ORDER BY match_date) IS NOT NULL THEN 1 -- Winner changed
            ELSE 0 -- Continues streak
          END as is_streak_break
        FROM ...
      ),
      streak_islands AS (
        SELECT
          *,
          -- Create the unique group_id for each streak
          SUM(is_streak_break) OVER (PARTITION BY player1_id, player2_id ORDER BY match_date) as group_id
        FROM streak_groups
      )
      SELECT ... FROM streak_islands WHERE is_upset = 1 GROUP BY group_id HAVING COUNT(*) >= 6;
    
    WORKFLOW:
    1. Write a SQL query to answer the user's question
    2. Use sql_db_query tool to execute the query and get results
    3. Analyze the results and provide a clear answer to the user
    
    REMEMBER: Always use sql_db_query (not sql_db_query_checker) to get actual data from the database!
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ]
    )
    
    # Bind tools to the LLM for native tool calling
    llm_with_tools = llm.bind_tools(tools)

    # --- Define the Nodes for the LangGraph ---

    # The 'agent' node uses the LLM with bound tools
    def call_agent(state: AgentState):
        """Calls the LLM to decide the next step."""
        messages = state["messages"]
        # Use the LLM with bound tools to get the response
        response = llm_with_tools.invoke(prompt.format_prompt(messages=messages))
        return {"messages": [response]}

    # Custom tool node with logging
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
                for tool in tools:
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
                                log_database_query(tool_input.get("query", ""), result, execution_time)
                            
                            return {"messages": [AIMessage(content=str(result), tool_calls=[])]}
                        except Exception as e:
                            log_error(e, f"Tool execution failed: {tool_name}")
                            return {"messages": [AIMessage(content=f"Error executing {tool_name}: {str(e)}", tool_calls=[])]}
        
        return {"messages": []}
    
    tool_node = logged_tool_node

    def should_continue(state: AgentState):
        """Decide whether to continue with tools or finish."""
        # The ReAct agent returns an AIMessage with tool_calls if it needs to act.
        if isinstance(state["messages"][-1], AIMessage) and hasattr(state["messages"][-1], 'tool_calls') and state["messages"][-1].tool_calls:
            return "tools"
        return "end"

    # --- Build the LangGraph ---
    graph = StateGraph(AgentState)
    
    graph.add_node("agent", call_agent)
    graph.add_node("tools", tool_node)
    
    graph.set_entry_point("agent")
    
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    
    graph.add_edge("tools", "agent")
    
    memory = MemorySaver()
    runnable_graph = graph.compile(checkpointer=memory)
    
    print("--- LangGraph Agent Compiled Successfully with Gemini ---")
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
    # Log the user query
    log_user_query(user_question, "user_session")
    
    with st.spinner("The AI is analyzing your question and querying the database..."):
        try:
            start_time = datetime.now()
            
            # The config dictionary ensures each user gets their own conversation history.
            config = {"configurable": {"thread_id": "user_session"}}
            
            # Log the initial LLM interaction
            log_llm_interaction([HumanMessage(content=user_question)], "INITIAL_USER_QUERY")
            
            # --- REFINEMENT 3: The stateful graph only needs the new human message. ---
            # It loads the history from memory automatically via the checkpointer.
            response = agent_graph.invoke(
                {"messages": [HumanMessage(content=user_question)]},
                config=config
            )
            
            # Log the complete conversation flow
            log_llm_interaction(response["messages"], "COMPLETE_CONVERSATION_FLOW")
            
            # The final answer is in the content of the last AIMessage.
            # Parse Gemini's structured output format
            last_message = response["messages"][-1]
            logger.info(f"Last message type: {type(last_message)}")
            logger.info(f"Last message content: {last_message.content}")
            logger.info(f"Last message content type: {type(last_message.content)}")
            
            if isinstance(last_message.content, list) and last_message.content:
                # For Gemini, content is a list of dicts. We want the text from the first part.
                final_answer = last_message.content[0].get("text", "")
                if logger is not None:
                    logger.info(f"Extracted from list content: {final_answer}")
            else:
                # Fallback for standard string content
                final_answer = last_message.content
                if logger is not None:
                    logger.info(f"Using string content: {final_answer}")
            
            # If no final answer found, try to extract from tool messages and format properly
            if not final_answer or not final_answer.strip():
                if logger is not None:
                    logger.info("No clear final answer found, attempting to parse database results...")
                # First, try to parse database results from AI messages
                for i, message in enumerate(reversed(response["messages"])):
                    if isinstance(message, AIMessage) and message.content:
                        if logger is not None:
                            logger.info(f"Checking AI message {i}: {message.content}")
                        try:
                            import ast
                            content_str = str(message.content)
                            if logger is not None:
                                logger.info(f"Content string: {content_str}")
                            if content_str.startswith('[') and content_str.endswith(']'):
                                if logger is not None:
                                    logger.info("Found list-like content, attempting to parse...")
                                data = ast.literal_eval(content_str)
                                if logger is not None:
                                    logger.info(f"Parsed data: {data}")
                                if data and len(data) > 0:
                                    # Format the result properly based on the query type
                                    if len(data) == 1 and len(data[0]) == 1:
                                        # Single result (like winner name)
                                        result = data[0][0]
                                        final_answer = f"The answer is: {result}"
                                        if logger is not None:
                                            logger.info(f"✅ Formatted single result: {final_answer}")
                                    elif len(data) == 1 and len(data[0]) > 1:
                                        # Multiple columns, single row
                                        final_answer = f"Result: {', '.join(map(str, data[0]))}"
                                        if logger is not None:
                                            logger.info(f"✅ Formatted multi-column result: {final_answer}")
                                    else:
                                        # Multiple rows
                                        final_answer = f"Found {len(data)} result(s): {', '.join([str(row[0]) for row in data[:5]])}"
                                        if logger is not None:
                                            logger.info(f"✅ Formatted multi-row result: {final_answer}")
                                    break
                        except Exception as e:
                            if logger is not None:
                                logger.info(f"Failed to parse message {i}: {e}")
                            continue
                
                # If still no answer, try tool messages
                if not final_answer or not final_answer.strip():
                    for message in reversed(response["messages"]):
                        if hasattr(message, 'type') and message.type == 'tool' and 'sql_db_query' in str(message.name):
                            try:
                                import ast
                                if message.content.startswith('[') and message.content.endswith(']'):
                                    data = ast.literal_eval(message.content)
                                    if data and len(data) > 0:
                                        # Format the result properly based on the query type
                                        if len(data) == 1 and len(data[0]) == 1:
                                            # Single result (like winner name)
                                            result = data[0][0]
                                            final_answer = f"The answer is: {result}"
                                        elif len(data) == 1 and len(data[0]) > 1:
                                            # Multiple columns, single row
                                            final_answer = f"Result: {', '.join(map(str, data[0]))}"
                                        else:
                                            # Multiple rows
                                            final_answer = f"Found {len(data)} result(s): {', '.join([str(row[0]) for row in data[:5]])}"
                                        break
                            except:
                                continue
            

            # Calculate total processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if final_answer and final_answer.strip():
                # Log successful response
                log_final_response(final_answer, processing_time)
                st.success("Here's what I found:")
                st.markdown(final_answer)
            else:
                # Log warning case
                log_final_response("No clear response generated", processing_time)
                st.warning("I processed your request but couldn't generate a clear response. Please check the conversation flow below for details.")
                
                # Check if this might be a misspelling issue
                if "no results" in str(final_answer).lower() or "not found" in str(final_answer).lower():
                    st.info("💡 **Tip**: If you didn't find what you're looking for, try checking the spelling of player or tournament names. The system is case-sensitive and requires exact matches.")


        except Exception as e:
            # Log error
            log_error(e, f"Processing user query: {user_question}")
            st.error(f"An error occurred while processing your request: {e}")

