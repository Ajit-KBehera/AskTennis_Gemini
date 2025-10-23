"""
Database utilities and helper functions for AskTennis AI application.
Handles database connections, caching, and fuzzy matching for player/tournament names.
"""

import sqlite3
import streamlit as st
from difflib import get_close_matches


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
    conn = sqlite3.connect("tennis_data_new.db")
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
