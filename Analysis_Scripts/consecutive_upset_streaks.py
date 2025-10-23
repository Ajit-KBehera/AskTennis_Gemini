#!/usr/bin/env python3
"""
Consecutive Upset Streaks Analysis
Find consecutive winning streaks of 6+ matches where the winner was ranked below their opponent
Using the sophisticated SQL query with proper data cleaning and normalization
"""

import sqlite3
import pandas as pd
import os

def find_consecutive_upset_streaks(db_path="tennis_data_new.db", min_streak=6):
    """
    Find consecutive upset streaks using the sophisticated SQL query
    """
    conn = sqlite3.connect(db_path)
    
    # The complete SQL query for consecutive upset streaks using gap detection logic
    query = """
    WITH
      -- Step 1 & 2: Clean data, create dates, and order chronologically
      cleaned_matches AS (
        SELECT
          DATE(
            event_year || '-' || printf('%02d', event_month) || '-' || printf('%02d', event_date)
          ) AS match_date,
          tourney_name,
          round,
          winner_id,
          winner_name,
          winner_rank,
          loser_id,
          loser_name,
          loser_rank
        FROM matches
        WHERE
          set1 IS NOT NULL
          AND set1 != 'W/O'
          AND winner_rank IS NOT NULL
          AND loser_rank IS NOT NULL
          AND winner_rank > 0
          AND loser_rank > 0
      ),
      
      -- Step 3: Normalize player pairs to group all matches between the same two people
      normalized_pairs AS (
        SELECT
          m.*,
          CASE
            WHEN winner_id < loser_id THEN winner_id ELSE loser_id
          END AS player1_id,
          CASE
            WHEN winner_id < loser_id THEN winner_name ELSE loser_name
          END AS player1_name,
          CASE
            WHEN winner_id < loser_id THEN loser_id ELSE winner_id
          END AS player2_id,
          CASE
            WHEN winner_id < loser_id THEN loser_name ELSE winner_name
          END AS player2_name
        FROM cleaned_matches AS m
      ),
      
      -- Step 4: Flag matches for upset status and identify "gaps" in a streak
      streak_groups AS (
        SELECT
          *,
          CASE
            WHEN winner_rank > loser_rank THEN 1 ELSE 0
          END AS is_upset,
          
          -- We define a "streak break" (a "gap") as any match that fails our criteria.
          -- A break = 1, a continuation = 0.
          -- A streak is broken if:
          -- 1. The match was NOT an upset (is_upset = 0).
          -- 2. The winner changed from the previous match *between these two players*.
          CASE
            WHEN (winner_rank > loser_rank) = 0 THEN 1 -- Not an upset, so this is a "break"
            WHEN winner_id != LAG(winner_id) OVER (
              PARTITION BY
                player1_id,
                player2_id
              ORDER BY
                match_date
            )
            AND LAG(winner_id) OVER (
              PARTITION BY
                player1_id,
                player2_id
              ORDER BY
                match_date
            ) IS NOT NULL THEN 1 -- It's an upset, but the winner changed, so this is a "break"
            ELSE 0 -- This match continues the streak (same winner, is an upset)
          END AS is_streak_break
        FROM normalized_pairs
      ),
      
      -- Step 5: Assign a unique group_id to each consecutive "island"
      streak_islands AS (
        SELECT
          *,
          -- A cumulative SUM of the "break" flags. This value will be
          -- constant for all consecutive matches in a single streak.
          SUM(is_streak_break) OVER (
            PARTITION BY
              player1_id,
              player2_id
            ORDER BY
              match_date
          ) AS group_id
        FROM streak_groups
      ),
      
      -- Step 6 & 7: Count matches in each streak, but only for the upset groups
      streak_counts AS (
        SELECT
          group_id,
          winner_id,
          MAX(winner_name) AS streak_winner_name, -- Get the name of the winner
          
          -- Identify the opponent in this pair
          CASE
            WHEN winner_id = player1_id THEN player2_id ELSE player1_id
          END AS opponent_id,
          CASE
            WHEN winner_id = player1_id THEN MAX(player2_name) ELSE MAX(player1_name)
          END AS opponent_name,
          
          COUNT(*) AS consecutive_upset_streak,
          MIN(match_date) AS streak_start_date,
          MAX(match_date) AS streak_end_date,
          
          -- Step 8: Include tournament names and match details
          GROUP_CONCAT(
            tourney_name || ' (' || round || ' | Rank: ' || CAST(
              ROUND(winner_rank) AS INTEGER
            ) || ' > ' || CAST(
              ROUND(loser_rank) AS INTEGER
            ) || ')',
            '; '
          ) AS match_details
          
        FROM streak_islands
        WHERE
          is_upset = 1 -- This is key: we only count the rows that *are* upsets
        GROUP BY
          player1_id,
          player2_id,
          group_id,
          winner_id
      )
    -- Final Step: Filter for streaks of 6+ and return all details
    SELECT
      streak_winner_name,
      opponent_name,
      consecutive_upset_streak,
      streak_start_date,
      streak_end_date,
      match_details
    FROM streak_counts
    WHERE
      consecutive_upset_streak >= ?
    ORDER BY
      consecutive_upset_streak DESC,
      streak_start_date DESC;
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
    """Main function to execute the consecutive upset streaks analysis"""
    
    # Find consecutive upset streaks using the sophisticated SQL query
    all_streaks = find_consecutive_upset_streaks(min_streak=6)
    
    if not all_streaks.empty:
        # Export all streaks to CSV
        export_to_csv(all_streaks, "consecutive_upset_streaks.csv")
    else:
        print("No consecutive upset streaks of 6+ matches found")

if __name__ == "__main__":
    main()
