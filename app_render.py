import streamlit as st
from sqlalchemy import create_engine
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import pandas as pd
from difflib import get_close_matches
import os

# Modern imports for LangChain & LangGraph
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
# Removed create_react_agent import - using custom agent pattern instead
from langgraph.checkpoint.memory import MemorySaver

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
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return []
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Get all unique winner and loser names
            result = conn.execute("SELECT DISTINCT winner_name FROM matches WHERE winner_name IS NOT NULL")
            winner_names = [row[0] for row in result.fetchall()]
            
            result = conn.execute("SELECT DISTINCT loser_name FROM matches WHERE loser_name IS NOT NULL")
            loser_names = [row[0] for row in result.fetchall()]
            
            # Combine and deduplicate
            all_names = list(set(winner_names + loser_names))
            return all_names
    except Exception as e:
        st.error(f"Error fetching player names: {e}")
        return []

@st.cache_data
def get_all_tournament_names():
    """Get all unique tournament names from the database for fuzzy matching."""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return []
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT DISTINCT tourney_name FROM matches WHERE tourney_name IS NOT NULL")
            tournament_names = [row[0] for row in result.fetchall()]
            return tournament_names
    except Exception as e:
        st.error(f"Error fetching tournament names: {e}")
        return []

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

def validate_head_to_head_count(matches_data, player1, player2):
    """Validate head-to-head counting and return accurate record."""
    if not matches_data or len(matches_data) == 0:
        return "No matches found"
    
    player1_wins = 0
    player2_wins = 0
    excluded_matches = 0
    
    for match in matches_data:
        if len(match) >= 7:  # Ensure we have enough data
            winner = match[0]
            # Check if this is a walkover, default, or retirement
            score_parts = [str(match[i]) for i in range(7, min(len(match), 12)) if match[i]]
            score_str = ' '.join(score_parts).upper()
            
            if 'W/O' in score_str or 'DEF' in score_str or 'RET' in score_str:
                excluded_matches += 1
                continue
            
            # Count wins
            if player1.lower() in winner.lower():
                player1_wins += 1
            elif player2.lower() in winner.lower():
                player2_wins += 1
    
    total_matches = player1_wins + player2_wins
    excluded_note = f" (excluding {excluded_matches} walkover/default/retirement matches)" if excluded_matches > 0 else ""
    
    return f"{player1} leads {player2} {player1_wins}-{player2_wins} in {total_matches} completed matches{excluded_note}"

# --- Database and LLM Setup (Cached for performance) ---

@st.cache_resource
def setup_langgraph_agent():
    """
    Sets up the database, LLM, tools, and compiles the LangGraph ReAct agent.
    This is cached to avoid re-initializing on every interaction.
    """
    print("--- Initializing LangGraph Agent with Gemini ---")

    # Check for the API key in environment variables (Render deployment)
    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            st.error("Google API key not found! Please set the GOOGLE_API_KEY environment variable in Render.")
            st.stop()
    except Exception as e:
        st.error(f"Error accessing Google API key: {e}")
        st.stop()

    # Setup database connection and tools for Render PostgreSQL
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            st.error("DATABASE_URL not found! Please set the DATABASE_URL environment variable in Render.")
            st.stop()
        
        # Handle postgres:// to postgresql:// conversion
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        db_engine = create_engine(database_url)
        db = SQLDatabase(engine=db_engine)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()
    
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

    # The 'tools' node is the pre-built ToolNode.
    tool_node = ToolNode(tools)

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
    # Create placeholders for dynamic content
    dataframe_placeholder = st.empty()
    
    with st.spinner("The AI is analyzing your question and querying the database..."):
        try:
            # The config dictionary ensures each user gets their own conversation history.
            config = {"configurable": {"thread_id": "user_session"}}
            
            # --- REFINEMENT 3: The stateful graph only needs the new human message. ---
            # It loads the history from memory automatically via the checkpointer.
            response = agent_graph.invoke(
                {"messages": [HumanMessage(content=user_question)]},
                config=config
            )
            
            # The final answer is in the content of the last AIMessage.
            # Parse Gemini's structured output format
            last_message = response["messages"][-1]
            if isinstance(last_message.content, list) and last_message.content:
                # For Gemini, content is a list of dicts. We want the text from the first part.
                final_answer = last_message.content[0].get("text", "")
            else:
                # Fallback for standard string content
                final_answer = last_message.content
            
            # If no final answer found, try to extract from tool messages
            if not final_answer or not final_answer.strip():
                for message in reversed(response["messages"]):
                    if hasattr(message, 'type') and message.type == 'tool' and 'sql_db_query' in str(message.name):
                        try:
                            import ast
                            if message.content.startswith('[') and message.content.endswith(']'):
                                data = ast.literal_eval(message.content)
                                if data and len(data) > 0:
                                    if isinstance(data[0], (list, tuple)) and len(data[0]) > 0:
                                        count = data[0][0]
                                        final_answer = f"Based on the database query, I found {count} result(s)."
                                    else:
                                        final_answer = f"Based on the database query, I found {len(data)} result(s)."
                                    break
                        except:
                            continue
            
            # Check if this is a head-to-head query and display detailed results
            if 'h2h' in user_question.lower() or 'head to head' in user_question.lower() or 'vs' in user_question.lower():
                # Look for detailed match data in tool messages
                for message in response["messages"]:
                    if hasattr(message, 'type') and message.type == 'tool' and 'sql_db_query' in str(message.name):
                        try:
                            import ast
                            if message.content.startswith('[') and message.content.endswith(']'):
                                data = ast.literal_eval(message.content)
                                if data and len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) > 3:
                                    # This looks like detailed match data (winner, loser, score, etc.)
                                    with dataframe_placeholder.container():
                                        st.markdown("### 📊 Detailed Head-to-Head Matches")
                                        
                                        # Convert to DataFrame for better display
                                        df_data = []
                                        for row in data:
                                            if len(row) >= 4:  # Ensure we have enough columns
                                                # Map columns based on the ACTUAL database query result:
                                                # Index 0: winner_name, Index 1: loser_name, Index 2: tourney_name, Index 3: event_year, Index 4: event_month, Index 5: event_date, Index 6: surface, Index 7: set1, Index 8: set2, etc.
                                                # Format the score properly by combining only the set scores
                                                set_scores = []
                                                for i in range(7, min(len(row), 12)):  # Start from set1 (index 7) to set5 (index 11)
                                                    if i < len(row) and row[i] and str(row[i]).strip() and str(row[i]).strip() != 'None':
                                                        set_scores.append(str(row[i]).strip())
                                                
                                                score_str = ' '.join(set_scores) if set_scores else 'N/A'
                                                
                                                df_data.append({
                                                    'Winner': row[0],
                                                    'Loser': row[1], 
                                                    'Tournament': row[2],
                                                    'Year': row[3] if len(row) > 3 else 'N/A',
                                                    'Surface': row[6] if len(row) > 6 else 'N/A',
                                                    'Score': score_str
                                                })
                                        
                                        if df_data:
                                            df = pd.DataFrame(df_data)
                                            
                                            # Add accurate head-to-head summary
                                            if len(data) > 0:
                                                # Extract player names from the first match
                                                first_match = data[0]
                                                if len(first_match) >= 2:
                                                    player1 = first_match[0]  # winner
                                                    player2 = first_match[1]  # loser
                                                    
                                                    # Validate and display accurate count
                                                    accurate_record = validate_head_to_head_count(data, player1, player2)
                                                    st.markdown(f"**Head-to-Head Record:** {accurate_record}")
                                            
                                            # Format the dataframe with consistent left alignment
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
                st.warning("I processed your request but couldn't generate a clear response. Please check the conversation flow below for details.")
                
                # Check if this might be a misspelling issue
                if "no results" in str(final_answer).lower() or "not found" in str(final_answer).lower():
                    st.info("💡 **Tip**: If you didn't find what you're looking for, try checking the spelling of player or tournament names. The system is case-sensitive and requires exact matches.")

            # Optional: Show the full conversation history for debugging
            # with st.expander("🧠 Show Full Conversation Flow", expanded=False):
            #     st.json(response['messages'])

        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")