"""
LangGraph agent setup and configuration for AskTennis AI application.
Handles agent state, LLM setup, tool configuration, and graph compilation.
"""

import streamlit as st
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime
from logging_config import log_tool_usage, log_database_query, log_error


# --- Define the Agent's State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


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
    
    # Add custom tournament mapping tool for combined events
    from langchain_core.tools import tool

    @tool
    def get_combined_tournament_names(tournament: str) -> str:
        """
        Get the correct tournament names for combined events that have both ATP and WTA.
        Returns a JSON string with ATP and WTA tournament names.
        
        Args:
            tournament: The tournament name to look up (e.g., 'rome', 'basel', 'madrid')
            
        Returns:
            JSON string with ATP and WTA tournament names
        """
        tournament_mappings = {
            "rome": {"atp": "Rome Masters", "wta": "Rome"},
            "basel": {"atp": "Basel", "wta": "Basel"},
            "madrid": {"atp": "Madrid Masters", "wta": "Madrid"},
            "indian wells": {"atp": "Indian Wells Masters", "wta": "Indian Wells"},
            "miami": {"atp": "Miami Masters", "wta": "Miami"},
            "monte carlo": {"atp": "Monte Carlo Masters", "wta": "Monte Carlo"},
            "hamburg": {"atp": "Hamburg", "wta": "Hamburg"},
            "stuttgart": {"atp": "Stuttgart", "wta": "Stuttgart"},
            "eastbourne": {"atp": "Eastbourne", "wta": "Eastbourne"},
            "newport": {"atp": "Newport", "wta": "Newport"},
            "atlanta": {"atp": "Atlanta", "wta": "Atlanta"},
            "washington": {"atp": "Washington", "wta": "Washington"},
            "toronto": {"atp": "Toronto Masters", "wta": "Toronto"},
            "montreal": {"atp": "Montreal Masters", "wta": "Montreal"},
            "cincinnati": {"atp": "Cincinnati Masters", "wta": "Cincinnati"},
            "winston salem": {"atp": "Winston Salem", "wta": "Winston Salem"},
            "stockholm": {"atp": "Stockholm", "wta": "Stockholm"},
            "antwerp": {"atp": "Antwerp", "wta": "Antwerp"},
            "vienna": {"atp": "Vienna", "wta": "Vienna"},
            "paris": {"atp": "Paris Masters", "wta": "Paris"}
        }
        
        tournament_lower = tournament.lower()
        if tournament_lower in tournament_mappings:
            return str(tournament_mappings[tournament_lower])
        else:
            return str({"atp": tournament, "wta": tournament})

    # Add the custom tool to the tools list
    tools.append(get_combined_tournament_names)
    
    # --- Custom agent pattern using llm.bind_tools() ---
    # This is the modern approach for tool-calling models like Gemini
    db_schema = db.get_table_info()
    system_prompt = f"""You are a helpful assistant designed to answer questions about tennis matches by querying a SQL database.
    Here is the schema for the `matches` table you can query:
    {db_schema}
    
    CRITICAL: COMBINED TOURNAMENTS (ATP + WTA)
    - For combined tournaments like Rome, Basel, Madrid, etc., you MUST search BOTH ATP and WTA tournaments
    - Use the get_combined_tournament_names tool to get the correct tournament names
    - Rome: ATP = "Rome Masters", WTA = "Rome"
    - Basel: ATP = "Basel", WTA = "Basel" 
    - Madrid: ATP = "Madrid Masters", WTA = "Madrid"
    - For generic tournament queries (without ATP/WTA specification), search BOTH tournaments using UNION
    - ALWAYS include round filter when user asks for specific rounds (Final, Semi-Final, etc.)
    - Example: "Who won Rome Final 2022" should return BOTH Iga Swiatek (WTA) and Novak Djokovic (ATP)
    - Example query: SELECT winner_name FROM matches WHERE tourney_name = 'Rome Masters' AND event_year = 2022 AND round = 'F' UNION SELECT winner_name FROM matches WHERE tourney_name = 'Rome' AND event_year = 2022 AND round = 'F'
    
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
