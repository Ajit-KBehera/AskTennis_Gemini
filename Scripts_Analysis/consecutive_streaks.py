#!/usr/bin/env python3
"""
Consecutive Winning Streaks Analysis
Find consecutive winning streaks of 6+ matches where the winner was ranked below their opponent
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

def get_matches_data(db_path="tennis_data.db"):
    """
    Get matches data using the provided SQL query
    """
    conn = sqlite3.connect(db_path)
    
    # SQL query to get ordered matches data
    query = """
    WITH src AS (
      SELECT DISTINCT
        tourney_name,
        round,
        event_year,
        event_month,
        event_date,
        winner_name,
        loser_name,
        winner_rank,
        loser_rank,
        set1
      FROM matches
      WHERE winner_name IS NOT NULL AND loser_name IS NOT NULL
        AND winner_rank IS NOT NULL 
        AND loser_rank IS NOT NULL
        AND set1 != 'W/O'  -- EXCLUDE WALKOVER MATCHES
        AND set1 IS NOT NULL
    ), dated AS (
      SELECT
        *,
        date(event_year || '-' || printf('%02d', event_month) || '-' || printf('%02d', event_date)) AS match_date
      FROM src
      WHERE event_year IS NOT NULL AND event_month IS NOT NULL AND event_date IS NOT NULL
    ), seq AS (
      SELECT
        *,
        CASE WHEN winner_name < loser_name THEN winner_name ELSE loser_name END AS player_a,
        CASE WHEN winner_name < loser_name THEN loser_name ELSE winner_name END AS player_b
      FROM dated
      WHERE match_date IS NOT NULL
    ), ordered AS (
      SELECT
        *,
        ROW_NUMBER() OVER (
          PARTITION BY player_a, player_b
          ORDER BY match_date, tourney_name, round
        ) AS seq_idx
      FROM seq
    )
    SELECT
      player_a,
      player_b,
      winner_name,
      loser_name,
      match_date,
      winner_rank AS winner_rank_int,
      loser_rank AS loser_rank_int,
      tourney_name,
      round,
      seq_idx
    FROM ordered
    ORDER BY player_a, player_b, seq_idx;
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def find_consecutive_streaks_6plus(df):
    """Find consecutive winning streaks of 6+ matches where winner was ranked below loser"""
    streaks = []
    
    for (player_a, player_b), group in df.groupby(["player_a", "player_b"]):
        group = group.sort_values("seq_idx")
        
        # Look for streaks of 6 or more consecutive matches
        i = 0
        while i < len(group) - 5:  # Need at least 6 matches remaining
            # Find the longest consecutive streak starting from position i
            streak_length = 0
            j = i
            
            while j < len(group):
                # Check if this match is part of a consecutive streak
                if j == i or group.iloc[j]["seq_idx"] == group.iloc[j-1]["seq_idx"] + 1:
                    # Check if same player won and was ranked below
                    if (group.iloc[j]["winner_name"] == group.iloc[i]["winner_name"] and
                        group.iloc[j]["winner_rank_int"] > group.iloc[j]["loser_rank_int"]):
                        streak_length += 1
                        j += 1
                    else:
                        break
                else:
                    break
            
            # If we found a streak of 6 or more, record it
            if streak_length >= 6:
                window = group.iloc[i:i+streak_length]
                
                winner = window["winner_name"].iloc[0]
                opponent = window["loser_name"].iloc[0]
                start_date = window["match_date"].iloc[0]
                end_date = window["match_date"].iloc[-1]
                winner_ranks = [int(rank) for rank in window["winner_rank_int"].tolist()]
                loser_ranks = [int(rank) for rank in window["loser_rank_int"].tolist()]
                tournaments = window["tourney_name"].tolist()
                rounds = window["round"].tolist()
                
                
                streaks.append({
                    "winner": winner,
                    "opponent": opponent,
                    "streak_length": streak_length,
                    "start_date": start_date,
                    "end_date": end_date,
                    "winner_ranks": winner_ranks,
                    "loser_ranks": loser_ranks,
                    "tournaments": tournaments,
                    "rounds": rounds
                })
                
                # Move to after this streak
                i = j
            else:
                i += 1
    
    return pd.DataFrame(streaks)

def export_to_csv(dataframe, filename, output_dir="output"):
    """Export DataFrame to CSV file"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    dataframe.to_csv(filepath, index=False)
    return filepath

def main():
    """Main function to demonstrate the consecutive streaks analysis"""
    
    # Get matches data
    matches_df = get_matches_data()
    
    # Find consecutive streaks
    all_streaks = find_consecutive_streaks_6plus(matches_df)
    
    if not all_streaks.empty:
        # Export all streaks to CSV
        export_to_csv(all_streaks, "all_consecutive_streaks.csv")

if __name__ == "__main__":
    main()