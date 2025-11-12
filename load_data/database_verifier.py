"""
Database verification functions for tennis data.

This module contains functions that verify the integrity and completeness
of the created database, including data counts, distributions, and sample queries.
"""

import sqlite3

# Import configuration
from .config import DB_FILE

def verify_enhancement():
    """
    Verifies that the player, rankings, and historical data integration worked correctly.
    """
    print("\n--- Verifying Complete Historical Integration ---")
    conn = sqlite3.connect(DB_FILE)
    
    # Check player count (separate ATP and WTA tables)
    atp_player_count = 0
    wta_player_count = 0
    try:
        atp_player_count = conn.execute("SELECT COUNT(*) FROM atp_players").fetchone()[0]
        print(f"ATP players in database: {atp_player_count}")
    except:
        print("No ATP players table found")
    
    try:
        wta_player_count = conn.execute("SELECT COUNT(*) FROM wta_players").fetchone()[0]
        print(f"WTA players in database: {wta_player_count}")
    except:
        print("No WTA players table found")
    
    player_count = atp_player_count + wta_player_count
    print(f"Total players in database: {player_count}")
    
    # Check rankings count (ATP and WTA separately)
    atp_rankings_count = 0
    wta_rankings_count = 0
    try:
        atp_rankings_count = conn.execute("SELECT COUNT(*) FROM atp_rankings").fetchone()[0]
        print(f"ATP rankings in database: {atp_rankings_count}")
    except:
        print("No ATP rankings table found")
    
    try:
        wta_rankings_count = conn.execute("SELECT COUNT(*) FROM wta_rankings").fetchone()[0]
        print(f"WTA rankings in database: {wta_rankings_count}")
    except:
        print("No WTA rankings table found")
    
    rankings_count = atp_rankings_count + wta_rankings_count
    
    # Check matches with player info (skip if views don't exist)
    matches_with_winner_info = 0
    matches_with_loser_info = 0
    try:
        matches_with_winner_info = conn.execute("""
            SELECT COUNT(*) FROM matches_with_full_info 
            WHERE winner_first_name IS NOT NULL
        """).fetchone()[0]
        
        matches_with_loser_info = conn.execute("""
            SELECT COUNT(*) FROM matches_with_full_info 
            WHERE loser_first_name IS NOT NULL
        """).fetchone()[0]
    except:
        # Views don't exist, check directly from matches and players tables
        # Use tour-specific players tables based on matches.tour column
        matches_with_winner_info = conn.execute("""
            SELECT COUNT(*) FROM matches m
            LEFT JOIN atp_players ap ON m.winner_id = ap.player_id AND m.tour = 'ATP'
            LEFT JOIN wta_players wp ON m.winner_id = wp.player_id AND m.tour = 'WTA'
            WHERE (ap.name_first IS NOT NULL OR wp.name_first IS NOT NULL)
        """).fetchone()[0]
        
        matches_with_loser_info = conn.execute("""
            SELECT COUNT(*) FROM matches m
            LEFT JOIN atp_players ap ON m.loser_id = ap.player_id AND m.tour = 'ATP'
            LEFT JOIN wta_players wp ON m.loser_id = wp.player_id AND m.tour = 'WTA'
            WHERE (ap.name_first IS NOT NULL OR wp.name_first IS NOT NULL)
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
    
    # Check rankings integration (skip if views don't exist)
    if rankings_count > 0:
        try:
            matches_with_rankings = conn.execute("""
                SELECT COUNT(*) FROM matches_with_rankings 
                WHERE winner_current_rank IS NOT NULL
            """).fetchone()[0]
            print(f"Matches with rankings data: {matches_with_rankings}/{total_matches} ({matches_with_rankings/total_matches*100:.1f}%)")
        except:
            # View doesn't exist, skip this check
            print("Rankings view not available (skipping rankings integration check)")
    
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
    try:
        # Try using view first
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
    except:
        # View doesn't exist, use direct table joins with tour-specific players tables
        sample_query = """
            SELECT m.winner_name, 
                   COALESCE(aw.hand, ww.hand) as winner_hand, 
                   COALESCE(aw.ioc, ww.ioc) as winner_ioc, 
                   COALESCE(aw.height, ww.height) as winner_height,
                   m.loser_name, 
                   COALESCE(al.hand, wl.hand) as loser_hand, 
                   COALESCE(al.ioc, wl.ioc) as loser_ioc, 
                   COALESCE(al.height, wl.height) as loser_height,
                   m.tourney_name, m.event_year, m.event_month, m.event_date, m.surface,
                   m.set1, m.set2, m.set3, m.set4, m.set5
            FROM matches m
            LEFT JOIN atp_players aw ON m.winner_id = aw.player_id AND m.tour = 'ATP'
            LEFT JOIN wta_players ww ON m.winner_id = ww.player_id AND m.tour = 'WTA'
            LEFT JOIN atp_players al ON m.loser_id = al.player_id AND m.tour = 'ATP'
            LEFT JOIN wta_players wl ON m.loser_id = wl.player_id AND m.tour = 'WTA'
            WHERE m.winner_name LIKE '%Federer%' OR m.loser_name LIKE '%Federer%'
            ORDER BY m.event_year DESC, m.event_month DESC, m.event_date DESC
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
        
        # ATP rankings sample
        if atp_rankings_count > 0:
            try:
                atp_rankings_query = """
                    SELECT p.name_first, p.name_last, r.rank, r.points, r.ranking_date
                    FROM atp_rankings r
                    JOIN atp_players p ON r.player = p.player_id
                    WHERE r.rank <= 5
                    ORDER BY r.ranking_date DESC, r.rank ASC
                    LIMIT 5
                """
                atp_results = conn.execute(atp_rankings_query).fetchall()
                if atp_results:
                    print("Top 5 ATP rankings sample:")
                    for row in atp_results:
                        print(f"  #{row[2]} {row[0]} {row[1]} - {row[3]} points ({row[4]})")
            except Exception as e:
                print(f"ATP rankings query error: {e}")
        
        # WTA rankings sample
        if wta_rankings_count > 0:
            try:
                wta_rankings_query = """
                    SELECT p.name_first, p.name_last, r.rank, r.points, r.ranking_date
                    FROM wta_rankings r
                    JOIN wta_players p ON r.player = p.player_id
                    WHERE r.rank <= 5
                    ORDER BY r.ranking_date DESC, r.rank ASC
                    LIMIT 5
                """
                wta_results = conn.execute(wta_rankings_query).fetchall()
                if wta_results:
                    print("Top 5 WTA rankings sample:")
                    for row in wta_results:
                        print(f"  #{row[2]} {row[0]} {row[1]} - {row[3]} points ({row[4]})")
            except Exception as e:
                print(f"WTA rankings query error: {e}")
    
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
    # Try tournament_type first, then fallback to tourney_level and round patterns
    qualifying_query = """
        SELECT winner_name, loser_name, tourney_name, event_year, event_month, event_date, 
               COALESCE(tournament_type, 'N/A') as tournament_type, tourney_level, round
        FROM matches 
        WHERE (tournament_type IN ('ATP_Qualifying', 'ATP_Challenger', 'ATP_Challenger_Qualifying', 
                                   'WTA_Qualifying', 'WTA_ITF'))
           OR (tour = 'ATP' AND tourney_level = 'C')
           OR (tour = 'ATP' AND round LIKE 'Q%' AND round != 'QF')
           OR (tour = 'WTA' AND round LIKE 'Q%' AND round != 'QF')
           OR (tour = 'WTA' AND tourney_level LIKE 'ITF_%')
        ORDER BY event_year DESC, event_month DESC, event_date DESC
        LIMIT 5
    """
    
    try:
        qualifying_results = conn.execute(qualifying_query).fetchall()
        if qualifying_results:
            print("Sample Qualifying/Challenger/ITF matches:")
            for row in qualifying_results:
                print(f"  {row[0]} vs {row[1]} - {row[2]} ({row[3]}-{row[4]:02d}-{row[5]:02d}) - Type: {row[6]}, Level: {row[7]}, Round: {row[8]}")
        else:
            print("No qualifying/challenger results found")
            # Check if tournament_type column exists and has any values
            try:
                type_check = conn.execute("SELECT COUNT(*) FROM matches WHERE tournament_type IS NOT NULL AND tournament_type != ''").fetchone()[0]
                if type_check == 0:
                    print("  Note: tournament_type column appears to be empty. Checking tourney_level and round patterns...")
                    # Try a simpler query using just tourney_level and round
                    simple_query = """
                        SELECT winner_name, loser_name, tourney_name, event_year, tourney_level, round
                        FROM matches 
                        WHERE (tour = 'ATP' AND tourney_level = 'C')
                           OR (round LIKE 'Q%' AND round != 'QF')
                        ORDER BY event_year DESC
                        LIMIT 3
                    """
                    simple_results = conn.execute(simple_query).fetchall()
                    if simple_results:
                        print("  Found matches using tourney_level/round patterns:")
                        for row in simple_results:
                            print(f"    {row[0]} vs {row[1]} - {row[2]} ({row[3]}) - Level: {row[4]}, Round: {row[5]}")
            except:
                pass
    except Exception as e:
        print(f"Qualifying/challenger query error: {e}")
    
    conn.close()

