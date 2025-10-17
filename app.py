import streamlit as st
import pandas as pd
import sqlite3
import spacy
import plotly.express as px  # --- NEW: Import Plotly ---

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error("SpaCy model not found. Please run 'python -m spacy download en_core_web_sm'")
    st.stop()

# --- Database Connection ---
DB_FILE = "tennis_data.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)

# --- Player Name Lookup Functions (No changes here) ---
@st.cache_data
def create_player_lookup():
    query = "SELECT DISTINCT winner_name FROM matches UNION SELECT DISTINCT loser_name FROM matches"
    df = pd.read_sql_query(query, conn)
    names = df['winner_name'].dropna().unique()
    lookup = {}
    for name in names:
        lookup[name] = name
        parts = name.split()
        if len(parts) > 1:
            last_name = parts[-1]
            if last_name not in lookup:
                 lookup[last_name] = name
    return lookup

PLAYER_LOOKUP = create_player_lookup()
PLAYER_SEARCH_LIST = sorted(PLAYER_LOOKUP.keys(), key=len, reverse=True)


# --- Page Configuration ---
st.set_page_config(page_title="AskTennis Viz", layout="wide")
st.title("🎾 AskTennis: AI-Powered Tennis Statistics")
st.markdown("Phase 3: Beautiful Visualizations. Ask a question below!")


# --- NLP Parsing Function (No changes here) ---
def parse_question(question):
    intent = "unknown"
    entities = {"players": [], "year": None}
    
    if "most wins" in question or "top winners" in question:
        intent = "top_winners"
    elif "head-to-head" in question.lower() or "vs" in question.lower() or "versus" in question.lower():
        intent = "h2h"
    elif "tournament winners" in question or "won which tournaments" in question:
        intent = "tournament_winners"

    question_title_case = question.title()
    found_canonical_names = set()
    for search_name in PLAYER_SEARCH_LIST:
        if search_name in question_title_case:
            canonical_name = PLAYER_LOOKUP[search_name]
            found_canonical_names.add(canonical_name)
            question_title_case = question_title_case.replace(search_name, "")
    entities["players"] = list(found_canonical_names)

    doc = nlp(question)
    for ent in doc.ents:
        if ent.label_ == "DATE" and ent.text.isdigit() and len(ent.text) == 4:
            entities["year"] = ent.text
            
    return intent, entities


# --- Functions to answer questions (No changes here) ---
def get_top_winners(year="2024"):
    query = f"""
    SELECT winner_name AS player, COUNT(*) AS wins
    FROM matches WHERE strftime('%Y', tourney_date) = '{year}'
    GROUP BY winner_name ORDER BY wins DESC LIMIT 10;
    """
    return pd.read_sql_query(query, conn)

def get_head_to_head(player1, player2):
    query = """
    SELECT tourney_name, strftime('%Y-%m-%d', tourney_date) as match_date, round,
           winner_name, loser_name, score
    FROM matches WHERE (winner_name = ? AND loser_name = ?) OR (winner_name = ? AND loser_name = ?)
    ORDER BY tourney_date DESC;
    """
    return pd.read_sql_query(query, conn, params=(player1, player2, player2, player1))

def get_tournament_winners(year):
    query = f"""
    SELECT tourney_name, winner_name as champion FROM matches
    WHERE round = 'F' AND strftime('%Y', tourney_date) = '{year}'
    ORDER BY tourney_name;
    """
    return pd.read_sql_query(query, conn)


# --- Main App UI & Logic ---
user_question = st.text_input(
    "Ask your tennis question:",
    placeholder="e.g., 'Who had the most wins in 2023?' or 'Nadal vs Djokovic h2h'"
)

if user_question:
    intent, entities = parse_question(user_question)
    
    st.write(f"🔍 **Intent:** `{intent}`")
    st.write(f"**Entities:** `{entities}`")
    
    if intent == "top_winners":
        year = entities.get("year", "2024") # Default to current year if not specified
        st.subheader(f"Top 10 Players by Wins in {year}")
        results_df = get_top_winners(year)
        
        # --- VISUALIZATION ---
        fig = px.bar(results_df, 
                     x='player', 
                     y='wins',
                     title=f"Most Match Wins ({year})",
                     labels={'player': 'Player', 'wins': 'Number of Wins'},
                     template="streamlit")
        st.plotly_chart(fig, use_container_width=True)
        # --- END VISUALIZATION ---
        
        st.dataframe(results_df, use_container_width=True)

    elif intent == "h2h":
        if len(entities["players"]) >= 2:
            player1 = entities["players"][0]
            player2 = entities["players"][1]
            st.subheader(f"Head-to-Head: {player1} vs. {player2}")
            results_df = get_head_to_head(player1, player2)
            
            if not results_df.empty:
                p1_wins = len(results_df[results_df['winner_name'] == player1])
                p2_wins = len(results_df[results_df['winner_name'] == player2])
                
                # --- VISUALIZATION ---
                chart_data = pd.DataFrame({
                    'Player': [player1, player2],
                    'Wins': [p1_wins, p2_wins]
                })
                fig = px.bar(chart_data, 
                             x='Player', 
                             y='Wins', 
                             title=f'Head-to-Head Wins: {player1} vs {player2}',
                             color='Player', # Assign different colors to each player
                             text_auto=True, # Display the win count on the bars
                             template="streamlit")
                st.plotly_chart(fig, use_container_width=True)
                # --- END VISUALIZATION ---
                
                st.markdown("#### Match History")
                st.dataframe(results_df, use_container_width=True)
            else:
                st.info(f"No match history found between {player1} and {player2} in the dataset.")
        else:
            st.warning(f"I found these players: `{entities['players']}`. Please specify two distinct player names for a head-to-head comparison.")

    elif intent == "tournament_winners":
        year = entities.get("year")
        if year:
            st.subheader(f"Tournament Winners in {year}")
            results_df = get_tournament_winners(year)
            # A table is best for this data, so no chart is needed.
            st.dataframe(results_df, use_container_width=True)
        else:
            st.warning("Please specify a year to find tournament winners.")
            
    else:
        st.error("Sorry, I didn't understand that question. Please try rephrasing.")