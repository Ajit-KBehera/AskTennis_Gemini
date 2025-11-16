-- SQL Query: Players with Most Points in Year-End Rankings (ATP)
-- This query finds players with the highest ranking points in year-end rankings
-- Year-end rankings are typically published in the last week of December (days 25-31)

-- Query 1: Top players by year-end ranking points (all-time)
-- Filters for last week of December (days 25-31) to capture year-end rankings
SELECT 
    player_name,
    strftime('%Y', ranking_date) AS year,
    rank,
    points,
    ranking_date
FROM atp_rankings
WHERE strftime('%m', ranking_date) = '12'
    AND CAST(strftime('%d', ranking_date) AS INTEGER) BETWEEN 25 AND 31
    AND points IS NOT NULL
ORDER BY points DESC
LIMIT 50;

-- Query 2: Top year-end ranking points by year (highest points each year)
-- Filters for last week of December (days 25-31) to capture year-end rankings
SELECT 
    year,
    player_name,
    rank,
    points,
    ranking_date
FROM (
    SELECT 
        player_name,
        strftime('%Y', ranking_date) AS year,
        rank,
        points,
        ranking_date,
        ROW_NUMBER() OVER (PARTITION BY strftime('%Y', ranking_date) ORDER BY points DESC, ranking_date DESC) AS rn
    FROM atp_rankings
    WHERE strftime('%m', ranking_date) = '12'
        AND CAST(strftime('%d', ranking_date) AS INTEGER) BETWEEN 25 AND 31
        AND points IS NOT NULL
)
WHERE rn = 1
ORDER BY year DESC;

-- Query 3: Players with most year-end ranking points (aggregated across all years)
-- Filters for last week of December (days 25-31) to capture year-end rankings
WITH player_stats AS (
    SELECT 
        player_name,
        COUNT(*) AS years_in_top_rankings,
        MAX(points) AS highest_year_end_points,
        MIN(rank) AS best_year_end_rank,
        AVG(points) AS avg_year_end_points
    FROM atp_rankings
    WHERE strftime('%m', ranking_date) = '12'
        AND CAST(strftime('%d', ranking_date) AS INTEGER) BETWEEN 25 AND 31
        AND points IS NOT NULL
    GROUP BY player_name
    HAVING COUNT(*) >= 1
),
year_of_max_points AS (
    SELECT 
        ps.player_name,
        ps.years_in_top_rankings,
        ps.highest_year_end_points,
        ps.best_year_end_rank,
        ps.avg_year_end_points,
        strftime('%Y', r.ranking_date) AS year_of_highest_points,
        ROW_NUMBER() OVER (PARTITION BY ps.player_name ORDER BY r.ranking_date DESC) AS rn
    FROM player_stats ps
    JOIN atp_rankings r ON r.player_name = ps.player_name
        AND r.points = ps.highest_year_end_points
        AND strftime('%m', r.ranking_date) = '12'
        AND CAST(strftime('%d', r.ranking_date) AS INTEGER) BETWEEN 25 AND 31
        AND r.points IS NOT NULL
)
SELECT 
    player_name,
    years_in_top_rankings,
    highest_year_end_points,
    year_of_highest_points,
    best_year_end_rank,
    avg_year_end_points
FROM year_of_max_points
WHERE rn = 1
ORDER BY highest_year_end_points DESC
LIMIT 30;

