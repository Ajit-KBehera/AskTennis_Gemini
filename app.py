import streamlit as st
from sqlalchemy import create_engine
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import pandas as pd

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
    - The database includes a `mixed_doubles_matches` table with mixed doubles data (2018-2024, 500+ matches)
    - Use `matches_with_full_info` view for queries that need player details
    - Use `matches_with_rankings` view for queries that need ranking context
    - Use `player_rankings_history` view for ranking analysis
    - Available player fields: winner_hand, winner_ioc, winner_height, winner_dob, loser_hand, loser_ioc, loser_height, loser_dob
    - Available ranking fields: winner_rank_at_time, winner_points_at_time, loser_rank_at_time, loser_points_at_time
    - Era classification: Amateur (1877-1967), Professional (1968-2024)
    - Tournament types: Main_Tour, ATP_Qual_Chall, ATP_Futures, WTA_Qual_ITF
    - Match types: Singles (matches table), Doubles (doubles_matches table), Mixed Doubles (mixed_doubles_matches table)
    - Historical coverage: 147 years of complete tennis history (1877-2024)
    
    CRITICAL INSTRUCTIONS:
    - To answer questions, you MUST use the sql_db_query tool to execute your SQL query and get results.
    - Do NOT use sql_db_query_checker - that only validates queries but doesn't return data.
    - After getting query results with sql_db_query, analyze the results and provide a clear, natural language answer.
    - Always provide a final response to the user, even if the query returns no results.
    - Do not make up information. If the database does not contain the answer, say so.
    
    SPECIAL INSTRUCTIONS FOR HEAD-TO-HEAD QUERIES:
    - For head-to-head questions (e.g., "Player A vs Player B h2h"), provide both a summary AND detailed match information.
    - ALWAYS include the surface column in your SQL queries for head-to-head matches.
    - Use this query format: SELECT winner_name, loser_name, tourney_name, tourney_date, score, surface FROM matches WHERE...
    - Include match details like year, tournament, surface, score, and winner.
    - Format the response to show both the overall record and individual match details.
    
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
    - Example: "Who won the first Wimbledon in 1877?" - use matches WHERE tourney_name LIKE '%Wimbledon%' AND strftime('%Y', tourney_date) = '1877'
    - Example: "Who won Wimbledon in 1970?" - use matches WHERE tourney_name LIKE '%Wimbledon%' AND strftime('%Y', tourney_date) = '1970'
    - Example: "How many matches were played in the 1980s?" - use matches WHERE strftime('%Y', tourney_date) BETWEEN '1980' AND '1989'
    - Example: "Which players dominated the 1990s?" - use matches WHERE strftime('%Y', tourney_date) BETWEEN '1990' AND '1999'
    - Example: "Compare amateur vs professional eras" - use era column to filter Amateur vs Professional
    - Example: "Compare tennis evolution across decades" - use decade-based analysis with strftime functions
    
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
    - Example: "Recent doubles champions" - use ORDER BY tourney_date DESC
    
    MIXED DOUBLES MATCH QUERIES:
    - For questions about mixed doubles matches, use the `mixed_doubles_matches` table
    - Mixed doubles table has 4 players: player1, partner1, player2, partner2
    - Mixed doubles are only played at Grand Slams (Australian Open, French Open, Wimbledon, US Open)
    - Example: "How many mixed doubles matches were played?" - use SELECT COUNT(*) FROM mixed_doubles_matches
    - Example: "Which mixed doubles team won the most matches?" - use GROUP BY player1, partner1
    - Example: "Mixed doubles champions at Wimbledon" - use WHERE tourney_name = 'Wimbledon'
    - Example: "Recent mixed doubles champions" - use ORDER BY year DESC
    - Example: "Mixed doubles by tournament" - use GROUP BY tourney_name
    - Example: "Mixed doubles by surface" - use GROUP BY surface
    - Example: "Who won mixed doubles at US Open 2024?" - use WHERE tourney_name = 'US Open' AND year = 2024
    
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
                                    st.markdown("### 📊 Detailed Head-to-Head Matches")
                                    
                                    
                                    # Convert to DataFrame for better display
                                    df_data = []
                                    for row in data:
                                        if len(row) >= 4:  # Ensure we have enough columns
                                            # Map columns based on the ACTUAL database query result:
                                            # Index 0: winner_name, Index 1: loser_name, Index 2: tourney_name, Index 3: tourney_date, Index 4: score, Index 5: surface
                                            df_data.append({
                                                'Winner': row[0],
                                                'Loser': row[1], 
                                                'Tournament': row[2],
                                                'Date': row[3] if len(row) > 3 else 'N/A',
                                                'Score': row[4] if len(row) > 4 else 'N/A',
                                                'Surface': row[5] if len(row) > 5 else 'N/A'
                                            })
                                    
                                    if df_data:
                                        df = pd.DataFrame(df_data)
                                        st.dataframe(df, use_container_width=True)
                                    else:
                                        st.warning("No detailed match data found in the expected format.")
                                    break
                        except:
                            continue

            if final_answer and final_answer.strip():
                st.success("Here's what I found:")
                st.markdown(final_answer)
            else:
                st.warning("I processed your request but couldn't generate a clear response. Please check the conversation flow below for details.")

            # Optional: Show the full conversation history for debugging
            with st.expander("🧠 Show Full Conversation Flow", expanded=False):
                st.json(response['messages'])

        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")

