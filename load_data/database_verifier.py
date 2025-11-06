"""
Database verification functions for tennis data.

This module contains functions that verify the integrity and completeness
of the created database, including data counts, distributions, and sample queries.
"""

import sqlite3

# Import configuration
from load_data.config import DB_FILE

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
    date_range = conn.execute("SELECT MIN(event_year), MAX(event_year) FROM matches").fetchone()
    print(f"Historical coverage: {date_range[0]} to {date_range[1]}")
    
    # Check era distribution
    era_counts = conn.execute("""
        SELECT era, COUNT(*) as matches 
        FROM matches 
        GROUP BY era 
        ORDER BY era
    """).fetchall()
    
    print("Matches by era:")
    for era, count in era_counts:
        print(f"  {era}: {count:,} matches")
    
    # Show era distribution with percentages
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    print(f"\nEra distribution percentages:")
    for era, count in era_counts:
        percentage = (count / total_matches) * 100
        print(f"  {era}: {count:,} matches ({percentage:.1f}%)")
    
    # Check tournament type distribution
    tournament_type_counts = conn.execute("""
        SELECT tournament_type, COUNT(*) as matches 
        FROM matches 
        GROUP BY tournament_type 
        ORDER BY matches DESC
    """).fetchall()
    
    print("Matches by tournament type:")
    for tournament_type, count in tournament_type_counts:
        print(f"  {tournament_type}: {count:,} matches")
    
    # Check standardized tourney level distribution
    tourney_level_counts = conn.execute("""
        SELECT tourney_level, COUNT(*) as matches 
        FROM matches 
        GROUP BY tourney_level 
        ORDER BY matches DESC
    """).fetchall()
    
    print("Matches by standardized tourney level:")
    for tourney_level, count in tourney_level_counts:
        print(f"  {tourney_level}: {count:,} matches")
    
    # Check matches by decade (expanded for complete history)
    decade_counts = conn.execute("""
        SELECT 
            CASE 
                WHEN event_year < 1880 THEN '1870s'
                WHEN event_year < 1890 THEN '1880s'
                WHEN event_year < 1900 THEN '1890s'
                WHEN event_year < 1910 THEN '1900s'
                WHEN event_year < 1920 THEN '1910s'
                WHEN event_year < 1930 THEN '1920s'
                WHEN event_year < 1940 THEN '1930s'
                WHEN event_year < 1950 THEN '1940s'
                WHEN event_year < 1960 THEN '1950s'
                WHEN event_year < 1970 THEN '1960s'
                WHEN event_year < 1980 THEN '1970s'
                WHEN event_year < 1990 THEN '1980s'
                WHEN event_year < 2000 THEN '1990s'
                WHEN event_year < 2010 THEN '2000s'
                WHEN event_year < 2020 THEN '2010s'
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
    
    # Check surface data quality
    missing_surface = conn.execute("""
        SELECT COUNT(*) FROM matches 
        WHERE surface IS NULL OR surface = '' OR surface = 'Unknown'
    """).fetchone()[0]
    
    print(f"Missing surface data: {missing_surface:,} matches")
    if missing_surface == 0:
        print("✅ All surface data is complete!")
    else:
        print(f"⚠️  {missing_surface:,} matches still have missing surface data")
    
    # Surface distribution
    surface_counts = conn.execute("""
        SELECT surface, COUNT(*) as matches 
        FROM matches 
        GROUP BY surface 
        ORDER BY matches DESC
    """).fetchall()
    
    print("Surface distribution:")
    for surface, count in surface_counts:
        print(f"  {surface}: {count:,} matches")
    
    # Check doubles data
    try:
        doubles_count = conn.execute("SELECT COUNT(*) FROM doubles_matches").fetchone()[0]
        print(f"Doubles matches: {doubles_count:,} matches")
        
        if doubles_count > 0:
            # Sample doubles query
            doubles_sample = conn.execute("""
                SELECT winner1_name, winner2_name, loser1_name, loser2_name, 
                       tourney_name, event_year, event_month, event_date, surface
                FROM doubles_matches 
                ORDER BY event_year DESC, event_month DESC, event_date DESC 
                LIMIT 3
            """).fetchall()
            
            print("Sample doubles matches:")
            for row in doubles_sample:
                print(f"  {row[0]} & {row[1]} vs {row[2]} & {row[3]} - {row[4]} ({row[5]}-{row[6]:02d}-{row[7]:02d}) - {row[8]}")
    except:
        print("No doubles matches found")
    
    
    # Sample query to test functionality
    print("\n--- Sample Player Query Test ---")
    sample_query = """
        SELECT winner_name, winner_hand, winner_ioc, winner_height,
               loser_name, loser_hand, loser_ioc, loser_height,
               tourney_name, event_year, event_month, event_date, surface,
               set1, set2, set3, set4, set5
        FROM matches_with_full_info 
        WHERE winner_name LIKE '%Federer%' OR loser_name LIKE '%Federer%'
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 3
    """
    
    results = conn.execute(sample_query).fetchall()
    if results:
        print("Sample query results (Federer matches):")
        for row in results:
            print(f"  {row[0]} ({row[1]}, {row[2]}, {row[3]}cm) vs {row[4]} ({row[5]}, {row[6]}, {row[7]}cm)")
            print(f"    {row[8]} - {row[9]}-{row[10]:02d}-{row[11]:02d} - {row[12]}")
            print(f"    Score: {row[13]} | {row[14]} | {row[15]} | {row[16]} | {row[17]}")
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
        SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, surface
        FROM matches 
        WHERE event_year = 1970
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 5
    """
    
    try:
        historical_results = conn.execute(historical_query).fetchall()
        if historical_results:
            print("Sample 1970 matches:")
            for row in historical_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}-{row[4]:02d}-{row[5]:02d}) - {row[6]}")
        else:
            print("No historical results found")
    except Exception as e:
        print(f"Historical query error: {e}")
    
    # Sample amateur era query
    print("\n--- Sample Amateur Era Query Test ---")
    amateur_query = """
        SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, surface, era
        FROM matches 
        WHERE event_year = 1877
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 5
    """
    
    try:
        amateur_results = conn.execute(amateur_query).fetchall()
        if amateur_results:
            print("Sample 1877 matches (First Wimbledon):")
            for row in amateur_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}-{row[4]:02d}-{row[5]:02d}) - {row[6]} - {row[7]}")
        else:
            print("No amateur era results found")
    except Exception as e:
        print(f"Amateur era query error: {e}")
    
    # Sample qualifying/challenger query
    print("\n--- Sample Qualifying/Challenger Query Test ---")
    qualifying_query = """
        SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, tournament_type, tourney_level
        FROM matches 
        WHERE tournament_type IN ('ATP_Qualifying', 'ATP_Challenger', 'ATP_Challenger_Qualifying')
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 5
    """
    
    try:
        qualifying_results = conn.execute(qualifying_query).fetchall()
        if qualifying_results:
            print("Sample ATP Qualifying/Challenger matches:")
            for row in qualifying_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}-{row[4]:02d}-{row[5]:02d}) - {row[6]} - {row[7]}")
        else:
            print("No qualifying/challenger results found")
    except Exception as e:
        print(f"Qualifying/challenger query error: {e}")
    
    conn.close()

