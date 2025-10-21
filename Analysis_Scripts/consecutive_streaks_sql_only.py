#!/usr/bin/env python3
"""
Consecutive Winning Streaks Analysis - SQL Only Version
Find consecutive winning streaks of 6+ matches where the winner was ranked below their opponent
Using pure SQL queries without Python processing
"""

import sqlite3
import pandas as pd
import os

def find_consecutive_streaks_sql_only(db_path="tennis_data.db", min_streak=6):
    """
    Find consecutive winning streaks using pure SQL - no Python processing needed
    """
    conn = sqlite3.connect(db_path)
    
    # Complete SQL query that does everything in the database
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
    ), consecutive_groups AS (
      SELECT
        *,
        seq_idx - ROW_NUMBER() OVER (PARTITION BY player_a, player_b, winner_name ORDER BY seq_idx) AS group_id
      FROM ordered
      WHERE winner_rank > loser_rank  -- Winner ranked below loser (upset)
    ), streak_counts AS (
      SELECT
        player_a,
        player_b,
        winner_name,
        group_id,
        COUNT(*) as streak_length,
        MIN(match_date) as start_date,
        MAX(match_date) as end_date,
        GROUP_CONCAT(winner_rank, ', ') as winner_ranks,
        GROUP_CONCAT(loser_rank, ', ') as loser_ranks,
        GROUP_CONCAT(tourney_name, ', ') as tournaments,
        GROUP_CONCAT(round, ', ') as rounds
      FROM consecutive_groups
      GROUP BY player_a, player_b, winner_name, group_id
      HAVING COUNT(*) >= ?
    )
    SELECT
      winner_name as winner,
      CASE WHEN winner_name = player_a THEN player_b ELSE player_a END as opponent,
      streak_length,
      start_date,
      end_date,
      winner_ranks,
      loser_ranks,
      tournaments,
      rounds
    FROM streak_counts
    ORDER BY streak_length DESC, start_date DESC;
    """
    
    # Execute query
    df = pd.read_sql_query(query, conn, params=[min_streak])
    conn.close()
    
    return df

def export_to_csv(dataframe, filename, output_dir="output"):
    """Export DataFrame to CSV file"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    dataframe.to_csv(filepath, index=False)
    return filepath

def main():
    """Main function using pure SQL approach"""
    
    # Find consecutive streaks using only SQL
    all_streaks = find_consecutive_streaks_sql_only(min_streak=6)
    
    if not all_streaks.empty:
        # Export all streaks to CSV
        export_to_csv(all_streaks, "consecutive_streaks_sql_only.csv")

if __name__ == "__main__":
    main()
