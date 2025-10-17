import streamlit as st
import pandas as pd
import sqlite3

# --- Database Connection ---
DB_FILE = "tennis_data.db"
conn = sqlite3.connect(DB_FILE)

# --- Page Configuration ---
st.set_page_config(page_title="AskTennis MVP", layout="wide")
st.title("🎾 AskTennis: AI-Powered Tennis Statistics")
st.markdown("This is the MVP version. Select a pre-defined question from the sidebar to get started.")


# --- Sidebar for User Input ---
st.sidebar.header("Ask a Question")

# The list of questions for our dropdown
question_options = [
    "Select a question...",
    "Who were the top 10 players with the most wins in 2024?",
    "Show the Head-to-Head record between two players.",
    "Find all tournament winners for a specific year."
]

selected_question = st.sidebar.selectbox("Choose a question:", question_options)


# --- Functions to answer questions ---

def get_top_winners_2024():
    """Query for top 10 players by wins in 2024."""
    query = """
    SELECT
        winner_name AS player,
        COUNT(*) AS wins
    FROM
        matches
    WHERE
        strftime('%Y', tourney_date) = '2024'
    GROUP BY
        winner_name
    ORDER BY
        wins DESC
    LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_head_to_head(player1, player2):
    """Query for H2H stats between two players."""
    query = f"""
    SELECT
        tourney_name,
        strftime('%Y-%m-%d', tourney_date) as match_date,
        round,
        winner_name,
        loser_name,
        score
    FROM
        matches
    WHERE
        (winner_name = '{player1}' AND loser_name = '{player2}')
        OR (winner_name = '{player2}' AND loser_name = '{player1}')
    ORDER BY
        tourney_date DESC;
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_tournament_winners(year):
    """Query for all tournament winners in a given year."""
    query = f"""
    SELECT
        tourney_name,
        winner_name as champion
    FROM
        matches
    WHERE
        round = 'F' AND strftime('%Y', tourney_date) = '{year}'
    ORDER BY
        tourney_name;
    """
    df = pd.read_sql_query(query, conn)
    return df

# --- Main App Logic ---

if selected_question == "Who were the top 10 players with the most wins in 2024?":
    st.subheader("Top 10 Players by Wins in 2024")
    results_df = get_top_winners_2024()
    st.dataframe(results_df, use_container_width=True)

elif selected_question == "Show the Head-to-Head record between two players.":
    st.subheader("Head-to-Head Record")
    # Get player names from user input fields
    player1 = st.sidebar.text_input("Enter Player 1 Name", "Carlos Alcaraz")
    player2 = st.sidebar.text_input("Enter Player 2 Name", "Jannik Sinner")
    
    if st.sidebar.button("Get H2H"):
        results_df = get_head_to_head(player1, player2)
        
        # Calculate and display summary stats
        p1_wins = len(results_df[results_df['winner_name'] == player1])
        p2_wins = len(results_df[results_df['winner_name'] == player2])
        
        st.markdown(f"### {player1} vs. {player2}")
        st.markdown(f"**{player1}'s Wins:** `{p1_wins}`")
        st.markdown(f"**{player2}'s Wins:** `{p2_wins}`")

        st.markdown("#### Match History")
        st.dataframe(results_df, use_container_width=True)

elif selected_question == "Find all tournament winners for a specific year.":
    st.subheader("Tournament Winners")
    year = st.sidebar.selectbox("Select Year", options=[2023, 2024, 2025], index=1)
    
    if year:
        results_df = get_tournament_winners(str(year))
        st.dataframe(results_df, use_container_width=True)

# Close the connection at the end of the script
conn.close()