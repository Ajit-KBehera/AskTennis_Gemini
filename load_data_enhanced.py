import pandas as pd
import sqlite3
import glob
import os

# --- Configuration ---
DATA_DIRS = ["data/tennis_atp", "data/tennis_wta"]
YEARS = list(range(1968, 2026))  # Complete historical coverage: 1968-2024
DB_FILE = "tennis_data.db"

def load_players_data():
    """
    Loads player information from ATP and WTA player files.
    """
    print("--- Loading Player Information ---")
    
    # Load ATP players
    atp_players_path = "data/tennis_atp/atp_players.csv"
    if os.path.exists(atp_players_path):
        print(f"Reading {atp_players_path}...")
        atp_players = pd.read_csv(atp_players_path)
        atp_players['tour'] = 'ATP'
        print(f"ATP players loaded: {len(atp_players)}")
    else:
        print(f"Warning: {atp_players_path} not found")
        atp_players = pd.DataFrame()
    
    # Load WTA players
    wta_players_path = "data/tennis_wta/wta_players.csv"
    if os.path.exists(wta_players_path):
        print(f"Reading {wta_players_path}...")
        wta_players = pd.read_csv(wta_players_path)
        wta_players['tour'] = 'WTA'
        print(f"WTA players loaded: {len(wta_players)}")
    else:
        print(f"Warning: {wta_players_path} not found")
        wta_players = pd.DataFrame()
    
    # Combine ATP and WTA players
    if not atp_players.empty and not wta_players.empty:
        all_players = pd.concat([atp_players, wta_players], ignore_index=True)
    elif not atp_players.empty:
        all_players = atp_players
    elif not wta_players.empty:
        all_players = wta_players
    else:
        print("No player data found!")
        return pd.DataFrame()
    
    # Clean and standardize player data
    all_players['dob'] = pd.to_datetime(all_players['dob'], format='%Y%m%d', errors='coerce')
    all_players['height'] = pd.to_numeric(all_players['height'], errors='coerce')
    
    # Create full name for easier searching
    all_players['full_name'] = all_players['name_first'] + ' ' + all_players['name_last']
    
    print(f"Total players loaded: {len(all_players)}")
    return all_players

def load_rankings_data():
    """
    Loads rankings data from ATP and WTA ranking files.
    """
    print("--- Loading Rankings Data ---")
    
    # Define ranking file patterns
    ranking_files = [
        "data/tennis_atp/atp_rankings_70s.csv",
        "data/tennis_atp/atp_rankings_80s.csv", 
        "data/tennis_atp/atp_rankings_90s.csv",
        "data/tennis_atp/atp_rankings_00s.csv",
        "data/tennis_atp/atp_rankings_10s.csv",
        "data/tennis_atp/atp_rankings_20s.csv",
        "data/tennis_atp/atp_rankings_current.csv",
        "data/tennis_wta/wta_rankings_80s.csv",
        "data/tennis_wta/wta_rankings_90s.csv", 
        "data/tennis_wta/wta_rankings_00s.csv",
        "data/tennis_wta/wta_rankings_10s.csv",
        "data/tennis_wta/wta_rankings_20s.csv",
        "data/tennis_wta/wta_rankings_current.csv"
    ]
    
    all_rankings = []
    
    for file_path in ranking_files:
        if os.path.exists(file_path):
            print(f"Reading {file_path}...")
            try:
                df = pd.read_csv(file_path)
                
                # Determine tour based on file path
                if 'atp' in file_path:
                    df['tour'] = 'ATP'
                elif 'wta' in file_path:
                    df['tour'] = 'WTA'
                else:
                    df['tour'] = 'Unknown'
                
                # Standardize column names
                if 'tours' in df.columns:
                    df = df.rename(columns={'tours': 'tournaments'})
                else:
                    df['tournaments'] = None
                
                all_rankings.append(df)
                print(f"  Loaded {len(df)} ranking records")
                
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
        else:
            print(f"  File not found: {file_path}")
    
    if not all_rankings:
        print("No rankings data found!")
        return pd.DataFrame()
    
    # Combine all rankings data
    rankings_df = pd.concat(all_rankings, ignore_index=True)
    
    # Clean and standardize rankings data
    rankings_df['ranking_date'] = pd.to_datetime(rankings_df['ranking_date'], format='%Y%m%d', errors='coerce')
    rankings_df['rank'] = pd.to_numeric(rankings_df['rank'], errors='coerce')
    rankings_df['points'] = pd.to_numeric(rankings_df['points'], errors='coerce')
    rankings_df['player'] = pd.to_numeric(rankings_df['player'], errors='coerce')
    
    # Remove invalid data
    rankings_df = rankings_df.dropna(subset=['ranking_date', 'rank', 'player'])
    
    print(f"Total rankings loaded: {len(rankings_df)}")
    print(f"Date range: {rankings_df['ranking_date'].min()} to {rankings_df['ranking_date'].max()}")
    
    return rankings_df

def load_matches_data():
    """
    Loads match data from ATP and WTA files.
    """
    print("--- Loading Match Data ---")
    master_df_list = []
    
    # Loop through each data directory (ATP and WTA)
    for data_dir in DATA_DIRS:
        print(f"\n--- Processing directory: {data_dir} ---")
        all_files = glob.glob(os.path.join(data_dir, "*_matches_*.csv"))
        
        df_list = []
        for year in YEARS:
            # Construct the expected file path pattern for each year
            file_pattern = os.path.join(data_dir, f"*_matches_{year}.csv")
            matching_files = glob.glob(file_pattern)
            
            if matching_files:
                file_path = matching_files[0] # Use the first match found
                print(f"Reading {file_path}...")
                df = pd.read_csv(file_path, low_memory=False)
                df_list.append(df)
            else:
                # This is not an error, just means data for that year/tour doesn't exist
                pass

        if df_list:
            # Combine all dataframes for the current tour (ATP or WTA)
            tour_df = pd.concat(df_list, ignore_index=True)
            master_df_list.append(tour_df)

    if not master_df_list:
        print("No data found in any directory. Exiting.")
        return pd.DataFrame()

    # Combine the ATP and WTA dataframes into one master dataframe
    matches_df = pd.concat(master_df_list, ignore_index=True)
    
    # Convert tourney_date to datetime objects for proper sorting/filtering
    matches_df['tourney_date'] = pd.to_datetime(matches_df['tourney_date'], format='%Y%m%d')

    print(f"\nTotal matches loaded (ATP & WTA): {len(matches_df)}")
    return matches_df

def create_database_with_players():
    """
    Creates the enhanced database with complete historical matches (1968-2024), 
    player information, and rankings.
    """
    print("=== Enhanced Data Loading with Complete Historical Coverage (1968-2024) ===")
    
    # Load player data
    players_df = load_players_data()
    
    # Load rankings data
    rankings_df = load_rankings_data()
    
    # Load match data
    matches_df = load_matches_data()
    
    if players_df.empty or matches_df.empty:
        print("Error: Could not load required data. Exiting.")
        return
    
    # --- Create SQLite Database ---
    print("\n--- Creating Enhanced Database ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Write matches data
    print("Writing matches data...")
    matches_df.to_sql('matches', conn, if_exists='replace', index=False)
    
    # Write players data
    print("Writing players data...")
    players_df.to_sql('players', conn, if_exists='replace', index=False)
    
    # Write rankings data
    if not rankings_df.empty:
        print("Writing rankings data...")
        rankings_df.to_sql('rankings', conn, if_exists='replace', index=False)
    else:
        print("No rankings data to write.")
    
    # Create indexes for better performance
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_winner_id ON matches(winner_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_loser_id ON matches(loser_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(tourney_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_players_id ON players(player_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_players_name ON players(full_name)")
    
    # Rankings indexes
    if not rankings_df.empty:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_player ON rankings(player)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(ranking_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_rank ON rankings(rank)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_tour ON rankings(tour)")
    
    # Create a view for easy player-match joins
    print("Creating player-match views...")
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
    
    # Create rankings-enhanced views
    if not rankings_df.empty:
        print("Creating rankings-enhanced views...")
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
                AND DATE(m.tourney_date) = DATE(r1.ranking_date)
            LEFT JOIN rankings r2 ON m.loser_id = r2.player 
                AND DATE(m.tourney_date) = DATE(r2.ranking_date)
        """)
        
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
    
    conn.close()
    
    print(f"\n✅ Successfully created enhanced database '{DB_FILE}' with:")
    print(f"   - {len(matches_df)} matches (Complete historical coverage: 1968-2024)")
    print(f"   - {len(players_df)} players")
    if not rankings_df.empty:
        print(f"   - {len(rankings_df)} ranking records")
    print(f"   - Player metadata integration")
    print(f"   - Rankings data integration")
    print(f"   - Performance indexes")
    print(f"   - Enhanced views with rankings")
    print(f"   - Complete historical tennis database")

def verify_enhancement():
    """
    Verifies that the player, rankings, and historical data integration worked correctly.
    """
    print("\n--- Verifying Complete Historical Integration ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Check player count
    player_count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    print(f"Players in database: {player_count}")
    
    # Check rankings count
    try:
        rankings_count = conn.execute("SELECT COUNT(*) FROM rankings").fetchone()[0]
        print(f"Rankings in database: {rankings_count}")
    except:
        print("No rankings table found")
        rankings_count = 0
    
    # Check matches with player info
    matches_with_winner_info = conn.execute("""
        SELECT COUNT(*) FROM matches_with_full_info 
        WHERE winner_first_name IS NOT NULL
    """).fetchone()[0]
    
    matches_with_loser_info = conn.execute("""
        SELECT COUNT(*) FROM matches_with_full_info 
        WHERE loser_first_name IS NOT NULL
    """).fetchone()[0]
    
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    
    # Check historical coverage
    date_range = conn.execute("SELECT MIN(tourney_date), MAX(tourney_date) FROM matches").fetchone()
    print(f"Historical coverage: {date_range[0]} to {date_range[1]}")
    
    # Check matches by decade
    decade_counts = conn.execute("""
        SELECT 
            CASE 
                WHEN strftime('%Y', tourney_date) < '1970' THEN '1960s'
                WHEN strftime('%Y', tourney_date) < '1980' THEN '1970s'
                WHEN strftime('%Y', tourney_date) < '1990' THEN '1980s'
                WHEN strftime('%Y', tourney_date) < '2000' THEN '1990s'
                WHEN strftime('%Y', tourney_date) < '2010' THEN '2000s'
                WHEN strftime('%Y', tourney_date) < '2020' THEN '2010s'
                ELSE '2020s'
            END as decade,
            COUNT(*) as matches
        FROM matches 
        GROUP BY decade 
        ORDER BY decade
    """).fetchall()
    
    print("Matches by decade:")
    for decade, count in decade_counts:
        print(f"  {decade}: {count:,} matches")
    
    print(f"Matches with winner info: {matches_with_winner_info}/{total_matches} ({matches_with_winner_info/total_matches*100:.1f}%)")
    print(f"Matches with loser info: {matches_with_loser_info}/{total_matches} ({matches_with_loser_info/total_matches*100:.1f}%)")
    
    # Check rankings integration
    if rankings_count > 0:
        try:
            matches_with_rankings = conn.execute("""
                SELECT COUNT(*) FROM matches_with_rankings 
                WHERE winner_rank_at_time IS NOT NULL
            """).fetchone()[0]
            print(f"Matches with rankings data: {matches_with_rankings}/{total_matches} ({matches_with_rankings/total_matches*100:.1f}%)")
        except:
            print("Rankings view not available")
    
    # Sample query to test functionality
    print("\n--- Sample Player Query Test ---")
    sample_query = """
        SELECT winner_name, winner_hand, winner_ioc, winner_height,
               loser_name, loser_hand, loser_ioc, loser_height,
               tourney_name, tourney_date, surface
        FROM matches_with_full_info 
        WHERE winner_name LIKE '%Federer%' OR loser_name LIKE '%Federer%'
        ORDER BY tourney_date DESC
        LIMIT 3
    """
    
    results = conn.execute(sample_query).fetchall()
    if results:
        print("Sample query results (Federer matches):")
        for row in results:
            print(f"  {row[0]} ({row[1]}, {row[2]}, {row[3]}cm) vs {row[4]} ({row[5]}, {row[6]}, {row[7]}cm)")
            print(f"    {row[8]} - {row[9]} - {row[10]}")
    else:
        print("No sample results found")
    
    # Sample rankings query
    if rankings_count > 0:
        print("\n--- Sample Rankings Query Test ---")
        rankings_query = """
            SELECT name_first, name_last, rank, points, ranking_date, tour
            FROM player_rankings_history 
            WHERE rank <= 5
            ORDER BY ranking_date DESC, rank ASC
            LIMIT 10
        """
        
        try:
            rankings_results = conn.execute(rankings_query).fetchall()
            if rankings_results:
                print("Top 5 rankings sample:")
                for row in rankings_results:
                    print(f"  #{row[2]} {row[0]} {row[1]} - {row[3]} points ({row[4]}) - {row[5]}")
            else:
                print("No rankings results found")
        except Exception as e:
            print(f"Rankings query error: {e}")
    
    # Sample historical query
    print("\n--- Sample Historical Query Test ---")
    historical_query = """
        SELECT winner_name, loser_name, tourney_name, tourney_date, surface
        FROM matches 
        WHERE strftime('%Y', tourney_date) = '1970'
        ORDER BY tourney_date DESC
        LIMIT 5
    """
    
    try:
        historical_results = conn.execute(historical_query).fetchall()
        if historical_results:
            print("Sample 1970 matches:")
            for row in historical_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}) - {row[4]}")
        else:
            print("No historical results found")
    except Exception as e:
        print(f"Historical query error: {e}")
    
    conn.close()

if __name__ == '__main__':
    create_database_with_players()
    verify_enhancement()
