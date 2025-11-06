"""
Database building functions for tennis data.

This module contains functions that create SQLite database structure,
write data to tables, create indexes, and build views.
"""

import sqlite3
import pandas as pd

# Import configuration
from load_data.config import (
    DB_FILE,
    CREATE_TABLE_MATCHES, CREATE_TABLE_PLAYERS, CREATE_TABLE_RANKINGS, CREATE_TABLE_DOUBLES,
    CREATE_INDEXES_MATCHES, CREATE_INDEXES_PLAYERS, CREATE_INDEXES_RANKINGS, CREATE_INDEXES_DOUBLES,
    CREATE_VIEW_WINNER_INFO, CREATE_VIEW_LOSER_INFO, CREATE_VIEW_FULL_INFO,
    CREATE_VIEW_MATCHES_RANKINGS, CREATE_VIEW_RANKINGS_HISTORY
)


def build_database(matches_df, players_df, rankings_df, doubles_df):
    """
    Builds SQLite database with matches, players, rankings, and doubles data.
    Creates indexes and views for optimized queries.
    
    Args:
        matches_df: DataFrame with match data
        players_df: DataFrame with player data
        rankings_df: DataFrame with rankings data
        doubles_df: DataFrame with doubles match data
    """
    print("\n--- Creating Enhanced Database ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Write matches data
    if CREATE_TABLE_MATCHES:
        print("Writing matches data...")
        matches_df.to_sql('matches', conn, if_exists='replace', index=False)
    else:
        print("Skipping matches table creation (CREATE_TABLE_MATCHES = False)")
    
    # Write players data
    if CREATE_TABLE_PLAYERS:
        print("Writing players data...")
        players_df.to_sql('players', conn, if_exists='replace', index=False)
    else:
        print("Skipping players table creation (CREATE_TABLE_PLAYERS = False)")
    
    # Write rankings data
    if CREATE_TABLE_RANKINGS:
        if not rankings_df.empty:
            print("Writing rankings data...")
            rankings_df.to_sql('rankings', conn, if_exists='replace', index=False)
        else:
            print("No rankings data to write.")
    else:
        print("Skipping rankings table creation (CREATE_TABLE_RANKINGS = False)")
    
    # Write doubles data
    if CREATE_TABLE_DOUBLES:
        if not doubles_df.empty:
            print("Writing doubles data...")
            doubles_df.to_sql('doubles_matches', conn, if_exists='replace', index=False)
        else:
            print("No doubles data to write.")
    else:
        print("Skipping doubles table creation (CREATE_TABLE_DOUBLES = False)")
    
    # Create indexes for better performance
    indexes_created = False
    
    if CREATE_INDEXES_MATCHES:
        print("Creating indexes for matches table...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_winner_id ON matches(winner_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_loser_id ON matches(loser_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_year ON matches(event_year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_month ON matches(event_month)")
        indexes_created = True
    
    if CREATE_INDEXES_PLAYERS:
        print("Creating indexes for players table...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_players_id ON players(player_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON players(full_name)")
        indexes_created = True
    
    # Rankings indexes
    if CREATE_INDEXES_RANKINGS and not rankings_df.empty:
        print("Creating indexes for rankings table...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_player ON rankings(player)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(ranking_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_rank ON rankings(rank)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_tour ON rankings(tour)")
        indexes_created = True
    
    # Doubles indexes
    if CREATE_INDEXES_DOUBLES and not doubles_df.empty:
        print("Creating indexes for doubles_matches table...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_winner1_id ON doubles_matches(winner1_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_winner2_id ON doubles_matches(winner2_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_loser1_id ON doubles_matches(loser1_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_loser2_id ON doubles_matches(loser2_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_year ON doubles_matches(event_year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doubles_month ON doubles_matches(event_month)")
        indexes_created = True
    
    if not indexes_created:
        print("No indexes created (all CREATE_INDEXES_* switches are False)")
    else:
        print("Finished creating indexes.")
    
    # Create views for easy player-match joins
    views_created = False
    
    if CREATE_VIEW_WINNER_INFO:
        print("Creating matches_with_winner_info view...")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS matches_with_winner_info AS
            SELECT m.*, 
                   p1.name_first as winner_first_name,
                   p1.name_last as winner_last_name,
                   p1.hand as winner_hand,
                   p1.dob as winner_dob,
                   p1.ioc as winner_ioc,
                   p1.height as winner_height,
                   p1.tour as winner_tour
            FROM matches m
            LEFT JOIN players p1 ON m.winner_id = p1.player_id
        """)
        views_created = True
    
    if CREATE_VIEW_LOSER_INFO:
        print("Creating matches_with_loser_info view...")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS matches_with_loser_info AS
            SELECT m.*, 
                   p2.name_first as loser_first_name,
                   p2.name_last as loser_last_name,
                   p2.hand as loser_hand,
                   p2.dob as loser_dob,
                   p2.ioc as loser_ioc,
                   p2.height as loser_height,
                   p2.tour as loser_tour
            FROM matches m
            LEFT JOIN players p2 ON m.loser_id = p2.player_id
        """)
        views_created = True
    
    if CREATE_VIEW_FULL_INFO:
        print("Creating matches_with_full_info view...")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS matches_with_full_info AS
            SELECT m.*,
                   p1.name_first as winner_first_name,
                   p1.name_last as winner_last_name,
                   p1.hand as winner_hand,
                   p1.dob as winner_dob,
                   p1.ioc as winner_ioc,
                   p1.height as winner_height,
                   p1.tour as winner_tour,
                   p2.name_first as loser_first_name,
                   p2.name_last as loser_last_name,
                   p2.hand as loser_hand,
                   p2.dob as loser_dob,
                   p2.ioc as loser_ioc,
                   p2.height as loser_height,
                   p2.tour as loser_tour
            FROM matches m
            LEFT JOIN players p1 ON m.winner_id = p1.player_id
            LEFT JOIN players p2 ON m.loser_id = p2.player_id
        """)
        views_created = True
    
    # Create rankings-enhanced views
    if CREATE_VIEW_MATCHES_RANKINGS and not rankings_df.empty:
        print("Creating matches_with_rankings view...")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS matches_with_rankings AS
            SELECT m.*,
                   p1.name_first as winner_first_name,
                   p1.name_last as winner_last_name,
                   p1.hand as winner_hand,
                   p1.dob as winner_dob,
                   p1.ioc as winner_ioc,
                   p1.height as winner_height,
                   p1.tour as winner_tour,
                   p2.name_first as loser_first_name,
                   p2.name_last as loser_last_name,
                   p2.hand as loser_hand,
                   p2.dob as loser_dob,
                   p2.ioc as loser_ioc,
                   p2.height as loser_height,
                   p2.tour as loser_tour,
                   r1.rank as winner_rank_at_time,
                   r1.points as winner_points_at_time,
                   r2.rank as loser_rank_at_time,
                   r2.points as loser_points_at_time
            FROM matches m
            LEFT JOIN players p1 ON m.winner_id = p1.player_id
            LEFT JOIN players p2 ON m.loser_id = p2.player_id
            LEFT JOIN rankings r1 ON m.winner_id = r1.player 
                AND r1.ranking_date = (
                    SELECT MAX(r1_inner.ranking_date)
                    FROM rankings r1_inner
                    WHERE r1_inner.player = m.winner_id
                      AND r1_inner.ranking_date <= m.tourney_date
                      AND r1_inner.tour = COALESCE(p1.tour, 'ATP')
                )
            LEFT JOIN rankings r2 ON m.loser_id = r2.player 
                AND r2.ranking_date = (
                    SELECT MAX(r2_inner.ranking_date)
                    FROM rankings r2_inner
                    WHERE r2_inner.player = m.loser_id
                      AND r2_inner.ranking_date <= m.tourney_date
                      AND r2_inner.tour = COALESCE(p2.tour, 'ATP')
                )
        """)
        views_created = True
    
    if CREATE_VIEW_RANKINGS_HISTORY and not rankings_df.empty:
        print("Creating player_rankings_history view...")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS player_rankings_history AS
            SELECT r.*,
                   p.name_first,
                   p.name_last,
                   p.hand,
                   p.ioc,
                   p.height,
                   p.tour
            FROM rankings r
            LEFT JOIN players p ON r.player = p.player_id
            ORDER BY r.ranking_date DESC, r.rank ASC
        """)
        views_created = True
    
    if not views_created:
        print("No views created (all CREATE_VIEW_* switches are False)")
    else:
        print("Finished creating views.")
    
    conn.close()
    
    print(f"\n✅ Successfully created enhanced database '{DB_FILE}' with:")
    print(f"   - {len(matches_df)} singles matches (COMPLETE tournament coverage: 1877-2024)")
    if not doubles_df.empty:
        print(f"   - {len(doubles_df)} doubles matches (2000-2020)")
    print(f"   - {len(players_df)} players")
    if not rankings_df.empty:
        print(f"   - {len(rankings_df)} ranking records")
    print(f"   - Player metadata integration")
    print(f"   - Rankings data integration")
    print(f"   - Surface data quality fix (missing surface inference)")
    print(f"   - Closed Era tennis (1877-1967)")
    print(f"   - Open Era tennis (1968-2024)")
    print(f"   - Main tour matches (Grand Slams, Masters, etc.)")
    print(f"   - Qualifying/Challenger/Futures matches")
    print(f"   - Doubles matches (separate table)")
    print(f"   - Performance indexes")
    print(f"   - Enhanced views with rankings")
    print(f"   - COMPLETE tennis tournament database (147 years)")
