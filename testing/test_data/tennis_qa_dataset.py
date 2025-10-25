"""
Comprehensive tennis Q&A dataset for automated testing.
Contains 100 carefully curated tennis questions with expected answers.
"""

from typing import List, Dict, Any
from .test_categories import TestCategory


# 100 Tennis Q&A Test Cases
TENNIS_QA_DATASET: List[Dict[str, Any]] = [
    # TOURNAMENT WINNERS (20 questions)
    {
        "id": 1,
        "question": "Who won Wimbledon in 2022?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2022 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Wimbledon", "2022", "winner"]
    },
    {
        "id": 2,
        "question": "Who won the French Open in 2021?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Roland Garros' AND event_year = 2021 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["French Open", "2021", "winner"]
    },
    {
        "id": 3,
        "question": "Who won the US Open in 2020?",
        "expected_answer": "Dominic Thiem",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'US Open' AND event_year = 2020 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["US Open", "2020", "winner"]
    },
    {
        "id": 4,
        "question": "Who won the Australian Open in 2023?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Australian Open' AND event_year = 2023 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Australian Open", "2023", "winner"]
    },
    {
        "id": 5,
        "question": "Who won Wimbledon in 2019?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2019 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Wimbledon", "2019", "winner"]
    },
    {
        "id": 6,
        "question": "Who won the French Open in 2020?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Roland Garros' AND event_year = 2020 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["French Open", "2020", "winner"]
    },
    {
        "id": 7,
        "question": "Who won the US Open in 2019?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'US Open' AND event_year = 2019 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["US Open", "2019", "winner"]
    },
    {
        "id": 8,
        "question": "Who won the Australian Open in 2022?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Australian Open' AND event_year = 2022 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Australian Open", "2022", "winner"]
    },
    {
        "id": 9,
        "question": "Who won Wimbledon in 2018?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2018 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Wimbledon", "2018", "winner"]
    },
    {
        "id": 10,
        "question": "Who won the French Open in 2019?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Roland Garros' AND event_year = 2019 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["French Open", "2019", "winner"]
    },
    {
        "id": 11,
        "question": "Who won the US Open in 2018?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'US Open' AND event_year = 2018 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["US Open", "2018", "winner"]
    },
    {
        "id": 12,
        "question": "Who won the Australian Open in 2021?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Australian Open' AND event_year = 2021 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Australian Open", "2021", "winner"]
    },
    {
        "id": 13,
        "question": "Who won Wimbledon in 2017?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2017 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Wimbledon", "2017", "winner"]
    },
    {
        "id": 14,
        "question": "Who won the French Open in 2018?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Roland Garros' AND event_year = 2018 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["French Open", "2018", "winner"]
    },
    {
        "id": 15,
        "question": "Who won the US Open in 2017?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'US Open' AND event_year = 2017 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["US Open", "2017", "winner"]
    },
    {
        "id": 16,
        "question": "Who won the Australian Open in 2020?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Australian Open' AND event_year = 2020 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Australian Open", "2020", "winner"]
    },
    {
        "id": 17,
        "question": "Who won Wimbledon in 2016?",
        "expected_answer": "Andy Murray",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2016 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Wimbledon", "2016", "winner"]
    },
    {
        "id": 18,
        "question": "Who won the French Open in 2017?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Roland Garros' AND event_year = 2017 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["French Open", "2017", "winner"]
    },
    {
        "id": 19,
        "question": "Who won the US Open in 2016?",
        "expected_answer": "Stan Wawrinka",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'US Open' AND event_year = 2016 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["US Open", "2016", "winner"]
    },
    {
        "id": 20,
        "question": "Who won the Australian Open in 2019?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Australian Open' AND event_year = 2019 AND round = 'F'",
        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ["Australian Open", "2019", "winner"]
    },

    # HEAD-TO-HEAD RECORDS (15 questions)
    {
        "id": 21,
        "question": "What is the head-to-head record between Roger Federer and Rafael Nadal?",
        "expected_answer": "Nadal leads 24-16",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Roger Federer' AND loser_name = 'Rafael Nadal') OR (winner_name = 'Rafael Nadal' AND loser_name = 'Roger Federer')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Federer", "Nadal", "head-to-head", "record"]
    },
    {
        "id": 22,
        "question": "How many times has Novak Djokovic beaten Andy Murray?",
        "expected_answer": "25",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE winner_name = 'Novak Djokovic' AND loser_name = 'Andy Murray'",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Djokovic", "Murray", "beaten", "times"]
    },
    {
        "id": 23,
        "question": "What is the head-to-head record between Serena Williams and Venus Williams?",
        "expected_answer": "Serena leads 19-12",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Serena Williams' AND loser_name = 'Venus Williams') OR (winner_name = 'Venus Williams' AND loser_name = 'Serena Williams')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Serena Williams", "Venus Williams", "head-to-head"]
    },
    {
        "id": 24,
        "question": "How many times has Rafael Nadal beaten Roger Federer?",
        "expected_answer": "24",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE winner_name = 'Rafael Nadal' AND loser_name = 'Roger Federer'",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Nadal", "Federer", "beaten", "times"]
    },
    {
        "id": 25,
        "question": "What is the head-to-head record between Novak Djokovic and Roger Federer?",
        "expected_answer": "Djokovic leads 27-23",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Novak Djokovic' AND loser_name = 'Roger Federer') OR (winner_name = 'Roger Federer' AND loser_name = 'Novak Djokovic')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Djokovic", "Federer", "head-to-head"]
    },
    {
        "id": 26,
        "question": "How many times has Andy Murray beaten Novak Djokovic?",
        "expected_answer": "11",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE winner_name = 'Andy Murray' AND loser_name = 'Novak Djokovic'",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Murray", "Djokovic", "beaten", "times"]
    },
    {
        "id": 27,
        "question": "What is the head-to-head record between Rafael Nadal and Novak Djokovic?",
        "expected_answer": "Djokovic leads 30-29",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Rafael Nadal' AND loser_name = 'Novak Djokovic') OR (winner_name = 'Novak Djokovic' AND loser_name = 'Rafael Nadal')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Nadal", "Djokovic", "head-to-head"]
    },
    {
        "id": 28,
        "question": "How many times has Roger Federer beaten Rafael Nadal?",
        "expected_answer": "16",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE winner_name = 'Roger Federer' AND loser_name = 'Rafael Nadal'",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Federer", "Nadal", "beaten", "times"]
    },
    {
        "id": 29,
        "question": "What is the head-to-head record between Andy Murray and Roger Federer?",
        "expected_answer": "Federer leads 14-11",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Andy Murray' AND loser_name = 'Roger Federer') OR (winner_name = 'Roger Federer' AND loser_name = 'Andy Murray')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Murray", "Federer", "head-to-head"]
    },
    {
        "id": 30,
        "question": "How many times has Novak Djokovic beaten Rafael Nadal?",
        "expected_answer": "30",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE winner_name = 'Novak Djokovic' AND loser_name = 'Rafael Nadal'",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Djokovic", "Nadal", "beaten", "times"]
    },
    {
        "id": 31,
        "question": "What is the head-to-head record between Andy Murray and Rafael Nadal?",
        "expected_answer": "Nadal leads 17-7",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Andy Murray' AND loser_name = 'Rafael Nadal') OR (winner_name = 'Rafael Nadal' AND loser_name = 'Andy Murray')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Murray", "Nadal", "head-to-head"]
    },
    {
        "id": 32,
        "question": "How many times has Rafael Nadal beaten Andy Murray?",
        "expected_answer": "17",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE winner_name = 'Rafael Nadal' AND loser_name = 'Andy Murray'",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Nadal", "Murray", "beaten", "times"]
    },
    {
        "id": 33,
        "question": "What is the head-to-head record between Novak Djokovic and Andy Murray?",
        "expected_answer": "Djokovic leads 25-11",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Novak Djokovic' AND loser_name = 'Andy Murray') OR (winner_name = 'Andy Murray' AND loser_name = 'Novak Djokovic')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Djokovic", "Murray", "head-to-head"]
    },
    {
        "id": 34,
        "question": "How many times has Roger Federer beaten Novak Djokovic?",
        "expected_answer": "23",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE winner_name = 'Roger Federer' AND loser_name = 'Novak Djokovic'",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Federer", "Djokovic", "beaten", "times"]
    },
    {
        "id": 35,
        "question": "What is the head-to-head record between Roger Federer and Andy Murray?",
        "expected_answer": "Federer leads 14-11",
        "expected_sql": "SELECT COUNT(*) FROM matches WHERE (winner_name = 'Roger Federer' AND loser_name = 'Andy Murray') OR (winner_name = 'Andy Murray' AND loser_name = 'Roger Federer')",
        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ["Federer", "Murray", "head-to-head"]
    },

    # SURFACE PERFORMANCE (15 questions)
    {
        "id": 36,
        "question": "Who has the best record on clay courts?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Clay' GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["clay", "courts", "best", "record"]
    },
    {
        "id": 37,
        "question": "Which players perform best on grass courts?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Grass' GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["grass", "courts", "perform", "best"]
    },
    {
        "id": 38,
        "question": "What is Rafael Nadal's win percentage on clay?",
        "expected_answer": "91.3%",
        "expected_sql": "SELECT (COUNT(CASE WHEN winner_name = 'Rafael Nadal' THEN 1 END) * 100.0 / COUNT(*)) as win_percentage FROM matches WHERE surface = 'Clay' AND (winner_name = 'Rafael Nadal' OR loser_name = 'Rafael Nadal')",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ["Nadal", "clay", "win", "percentage"]
    },
    {
        "id": 39,
        "question": "Who has the most wins on hard courts?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Hard' GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["hard", "courts", "most", "wins"]
    },
    {
        "id": 40,
        "question": "Which surface does Novak Djokovic perform best on?",
        "expected_answer": "Hard courts",
        "expected_sql": "SELECT surface, (COUNT(CASE WHEN winner_name = 'Novak Djokovic' THEN 1 END) * 100.0 / COUNT(*)) as win_percentage FROM matches WHERE (winner_name = 'Novak Djokovic' OR loser_name = 'Novak Djokovic') GROUP BY surface ORDER BY win_percentage DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ["Djokovic", "surface", "perform", "best"]
    },
    {
        "id": 41,
        "question": "What is Roger Federer's win percentage on grass?",
        "expected_answer": "87.1%",
        "expected_sql": "SELECT (COUNT(CASE WHEN winner_name = 'Roger Federer' THEN 1 END) * 100.0 / COUNT(*)) as win_percentage FROM matches WHERE surface = 'Grass' AND (winner_name = 'Roger Federer' OR loser_name = 'Roger Federer')",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ["Federer", "grass", "win", "percentage"]
    },
    {
        "id": 42,
        "question": "Who has the best record on indoor courts?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Carpet' OR tourney_name LIKE '%Indoor%' GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["indoor", "courts", "best", "record"]
    },
    {
        "id": 43,
        "question": "Which players have the most wins on clay in 2020?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Clay' AND event_year = 2020 GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["clay", "2020", "most", "wins"]
    },
    {
        "id": 44,
        "question": "What is Andy Murray's win percentage on grass?",
        "expected_answer": "78.4%",
        "expected_sql": "SELECT (COUNT(CASE WHEN winner_name = 'Andy Murray' THEN 1 END) * 100.0 / COUNT(*)) as win_percentage FROM matches WHERE surface = 'Grass' AND (winner_name = 'Andy Murray' OR loser_name = 'Andy Murray')",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ["Murray", "grass", "win", "percentage"]
    },
    {
        "id": 45,
        "question": "Who has the most wins on hard courts in 2021?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Hard' AND event_year = 2021 GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["hard", "courts", "2021", "most", "wins"]
    },
    {
        "id": 46,
        "question": "Which surface produces the most upsets?",
        "expected_answer": "Grass courts",
        "expected_sql": "SELECT surface, COUNT(*) as upsets FROM matches WHERE winner_rank > loser_rank GROUP BY surface ORDER BY upsets DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ["surface", "upsets", "most"]
    },
    {
        "id": 47,
        "question": "What is Novak Djokovic's win percentage on hard courts?",
        "expected_answer": "84.2%",
        "expected_sql": "SELECT (COUNT(CASE WHEN winner_name = 'Novak Djokovic' THEN 1 END) * 100.0 / COUNT(*)) as win_percentage FROM matches WHERE surface = 'Hard' AND (winner_name = 'Novak Djokovic' OR loser_name = 'Novak Djokovic')",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ["Djokovic", "hard", "courts", "win", "percentage"]
    },
    {
        "id": 48,
        "question": "Who has the most wins on grass courts in 2019?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Grass' AND event_year = 2019 GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["grass", "courts", "2019", "most", "wins"]
    },
    {
        "id": 49,
        "question": "Which players have the best record on carpet courts?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as wins FROM matches WHERE surface = 'Carpet' GROUP BY winner_name ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ["carpet", "courts", "best", "record"]
    },
    {
        "id": 50,
        "question": "What is Rafael Nadal's win percentage on hard courts?",
        "expected_answer": "77.8%",
        "expected_sql": "SELECT (COUNT(CASE WHEN winner_name = 'Rafael Nadal' THEN 1 END) * 100.0 / COUNT(*)) as win_percentage FROM matches WHERE surface = 'Hard' AND (winner_name = 'Rafael Nadal' OR loser_name = 'Rafael Nadal')",
        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ["Nadal", "hard", "courts", "win", "percentage"]
    },

    # STATISTICAL ANALYSIS (15 questions)
    {
        "id": 51,
        "question": "Who has the most Grand Slam titles?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name, COUNT(*) as titles FROM matches WHERE tourney_level = 'G' AND round = 'F' GROUP BY winner_name ORDER BY titles DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "easy",
        "keywords": ["Grand Slam", "titles", "most"]
    },
    {
        "id": 52,
        "question": "Which player has the highest ranking?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name, MIN(winner_rank) as best_ranking FROM matches WHERE winner_rank IS NOT NULL GROUP BY winner_name ORDER BY best_ranking LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ["player", "highest", "ranking"]
    },
    {
        "id": 53,
        "question": "What is the average age of top 10 players?",
        "expected_answer": "28.5",
        "expected_sql": "SELECT AVG(winner_age) as avg_age FROM matches WHERE winner_rank <= 10 AND winner_age IS NOT NULL",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ["average", "age", "top 10", "players"]
    },
    {
        "id": 54,
        "question": "Who has the most ATP titles?",
        "expected_answer": "Jimmy Connors",
        "expected_sql": "SELECT winner_name, COUNT(*) as titles FROM matches WHERE tour = 'ATP' AND round = 'F' GROUP BY winner_name ORDER BY titles DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ["ATP", "titles", "most"]
    },
    {
        "id": 55,
        "question": "Which player has the most aces in 2023?",
        "expected_answer": "Ilya Ivashka",
        "expected_sql": "SELECT winner_name, SUM(w_ace) as total_aces FROM matches WHERE event_year = 2023 AND w_ace IS NOT NULL GROUP BY winner_name ORDER BY total_aces DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ["player", "aces", "2023", "most"]
    },
    {
        "id": 56,
        "question": "What is the longest match duration in minutes?",
        "expected_answer": "665",
        "expected_sql": "SELECT MAX(minutes) as longest_match FROM matches WHERE minutes IS NOT NULL",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ["longest", "match", "duration", "minutes"]
    },
    {
        "id": 57,
        "question": "Who has the most consecutive weeks at number 1?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as weeks_at_1 FROM matches WHERE winner_rank = 1 GROUP BY winner_name ORDER BY weeks_at_1 DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ["consecutive", "weeks", "number 1"]
    },
    {
        "id": 58,
        "question": "Which player has the most double faults in 2022?",
        "expected_answer": "Alexander Zverev",
        "expected_sql": "SELECT winner_name, SUM(w_df) as total_df FROM matches WHERE event_year = 2022 AND w_df IS NOT NULL GROUP BY winner_name ORDER BY total_df DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ["player", "double faults", "2022", "most"]
    },
    {
        "id": 59,
        "question": "What is the average match duration in Grand Slams?",
        "expected_answer": "142.3",
        "expected_sql": "SELECT AVG(minutes) as avg_duration FROM matches WHERE tourney_level = 'G' AND minutes IS NOT NULL",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ["average", "match", "duration", "Grand Slams"]
    },
    {
        "id": 60,
        "question": "Who has the most wins in a single year?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, event_year, COUNT(*) as wins FROM matches GROUP BY winner_name, event_year ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ["wins", "single year", "most"]
    },
    {
        "id": 61,
        "question": "Which player has the highest first serve percentage?",
        "expected_answer": "John Isner",
        "expected_sql": "SELECT winner_name, AVG((w_1stIn * 100.0 / w_svpt)) as first_serve_pct FROM matches WHERE w_1stIn IS NOT NULL AND w_svpt IS NOT NULL AND w_svpt > 0 GROUP BY winner_name ORDER BY first_serve_pct DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ["player", "first serve", "percentage", "highest"]
    },
    {
        "id": 62,
        "question": "What is the most common score in tennis matches?",
        "expected_answer": "6-4, 6-4",
        "expected_sql": "SELECT set1, set2, COUNT(*) as frequency FROM matches WHERE set1 IS NOT NULL AND set2 IS NOT NULL GROUP BY set1, set2 ORDER BY frequency DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ["common", "score", "tennis", "matches"]
    },
    {
        "id": 63,
        "question": "Who has the most bagels (6-0 sets) in their career?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as bagels FROM matches WHERE (set1 = '6-0' OR set2 = '6-0' OR set3 = '6-0' OR set4 = '6-0' OR set5 = '6-0') GROUP BY winner_name ORDER BY bagels DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ["bagels", "6-0", "sets", "career", "most"]
    },
    {
        "id": 64,
        "question": "Which player has the most tiebreaks won?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as tiebreaks FROM matches WHERE score LIKE '%7-6%' GROUP BY winner_name ORDER BY tiebreaks DESC LIMIT 1",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ["player", "tiebreaks", "won", "most"]
    },
    {
        "id": 65,
        "question": "What is the average height of top 100 players?",
        "expected_answer": "185.2",
        "expected_sql": "SELECT AVG(winner_ht) as avg_height FROM matches WHERE winner_rank <= 100 AND winner_ht IS NOT NULL",
        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ["average", "height", "top 100", "players"]
    },

    # HISTORICAL RECORDS (10 questions)
    {
        "id": 66,
        "question": "Who was the youngest Wimbledon champion?",
        "expected_answer": "Boris Becker",
        "expected_sql": "SELECT winner_name, MIN(winner_age) as youngest_age FROM matches WHERE tourney_name = 'Wimbledon' AND round = 'F' AND winner_age IS NOT NULL GROUP BY winner_name ORDER BY youngest_age LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ["youngest", "Wimbledon", "champion"]
    },
    {
        "id": 67,
        "question": "Which player has the longest winning streak?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as streak FROM matches WHERE winner_name = 'Roger Federer' GROUP BY winner_name ORDER BY streak DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ["player", "longest", "winning", "streak"]
    },
    {
        "id": 68,
        "question": "Who won the most matches in a single year?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, event_year, COUNT(*) as wins FROM matches GROUP BY winner_name, event_year ORDER BY wins DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ["matches", "single year", "most"]
    },
    {
        "id": 69,
        "question": "Which player has the most consecutive Grand Slam finals?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as consecutive_finals FROM matches WHERE tourney_level = 'G' AND round = 'F' GROUP BY winner_name ORDER BY consecutive_finals DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ["player", "consecutive", "Grand Slam", "finals"]
    },
    {
        "id": 70,
        "question": "Who was the oldest player to win a Grand Slam?",
        "expected_answer": "Ken Rosewall",
        "expected_sql": "SELECT winner_name, MAX(winner_age) as oldest_age FROM matches WHERE tourney_level = 'G' AND round = 'F' AND winner_age IS NOT NULL GROUP BY winner_name ORDER BY oldest_age DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ["oldest", "player", "Grand Slam"]
    },
    {
        "id": 71,
        "question": "Which player has the most career wins?",
        "expected_answer": "Jimmy Connors",
        "expected_sql": "SELECT winner_name, COUNT(*) as career_wins FROM matches GROUP BY winner_name ORDER BY career_wins DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "easy",
        "keywords": ["player", "career", "wins", "most"]
    },
    {
        "id": 72,
        "question": "Who has the most consecutive weeks at number 1?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as weeks_at_1 FROM matches WHERE winner_rank = 1 GROUP BY winner_name ORDER BY weeks_at_1 DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ["consecutive", "weeks", "number 1"]
    },
    {
        "id": 73,
        "question": "Which player has the most 5-set match wins?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as five_set_wins FROM matches WHERE best_of = 5 AND winner_name IS NOT NULL GROUP BY winner_name ORDER BY five_set_wins DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ["player", "5-set", "match", "wins", "most"]
    },
    {
        "id": 74,
        "question": "Who has the most wins against top 10 players?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, COUNT(*) as top10_wins FROM matches WHERE loser_rank <= 10 AND loser_rank IS NOT NULL GROUP BY winner_name ORDER BY top10_wins DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ["wins", "top 10", "players", "most"]
    },
    {
        "id": 75,
        "question": "Which player has the most tournament wins in a single year?",
        "expected_answer": "Roger Federer",
        "expected_sql": "SELECT winner_name, event_year, COUNT(DISTINCT tourney_id) as tournaments_won FROM matches WHERE round = 'F' GROUP BY winner_name, event_year ORDER BY tournaments_won DESC LIMIT 1",
        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ["player", "tournament", "wins", "single year", "most"]
    },

    # PLAYER RANKINGS (10 questions)
    {
        "id": 76,
        "question": "Who was ranked number 1 in 2020?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE winner_rank = 1 AND event_year = 2020 LIMIT 1",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ["ranked", "number 1", "2020"]
    },
    {
        "id": 77,
        "question": "Which players were in the top 10 in 2019?",
        "expected_answer": "Novak Djokovic, Rafael Nadal, Roger Federer, Daniil Medvedev, Dominic Thiem, Stefanos Tsitsipas, Alexander Zverev, Matteo Berrettini, Roberto Bautista Agut, Gael Monfils",
        "expected_sql": "SELECT DISTINCT winner_name FROM matches WHERE winner_rank <= 10 AND event_year = 2019 ORDER BY winner_rank",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ["players", "top 10", "2019"]
    },
    {
        "id": 78,
        "question": "What was Roger Federer's highest ranking?",
        "expected_answer": "1",
        "expected_sql": "SELECT MIN(winner_rank) as highest_ranking FROM matches WHERE winner_name = 'Roger Federer' AND winner_rank IS NOT NULL",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ["Federer", "highest", "ranking"]
    },
    {
        "id": 79,
        "question": "Who was ranked number 1 in 2018?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE winner_rank = 1 AND event_year = 2018 LIMIT 1",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ["ranked", "number 1", "2018"]
    },
    {
        "id": 80,
        "question": "Which player has spent the most weeks at number 1?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name, COUNT(*) as weeks_at_1 FROM matches WHERE winner_rank = 1 GROUP BY winner_name ORDER BY weeks_at_1 DESC LIMIT 1",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "hard",
        "keywords": ["player", "weeks", "number 1", "most"]
    },
    {
        "id": 81,
        "question": "Who was ranked number 1 in 2017?",
        "expected_answer": "Rafael Nadal",
        "expected_sql": "SELECT winner_name FROM matches WHERE winner_rank = 1 AND event_year = 2017 LIMIT 1",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ["ranked", "number 1", "2017"]
    },
    {
        "id": 82,
        "question": "What was Rafael Nadal's highest ranking?",
        "expected_answer": "1",
        "expected_sql": "SELECT MIN(winner_rank) as highest_ranking FROM matches WHERE winner_name = 'Rafael Nadal' AND winner_rank IS NOT NULL",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ["Nadal", "highest", "ranking"]
    },
    {
        "id": 83,
        "question": "Who was ranked number 1 in 2016?",
        "expected_answer": "Andy Murray",
        "expected_sql": "SELECT winner_name FROM matches WHERE winner_rank = 1 AND event_year = 2016 LIMIT 1",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ["ranked", "number 1", "2016"]
    },
    {
        "id": 84,
        "question": "Which players were in the top 5 in 2020?",
        "expected_answer": "Novak Djokovic, Rafael Nadal, Dominic Thiem, Roger Federer, Daniil Medvedev",
        "expected_sql": "SELECT DISTINCT winner_name FROM matches WHERE winner_rank <= 5 AND event_year = 2020 ORDER BY winner_rank",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ["players", "top 5", "2020"]
    },
    {
        "id": 85,
        "question": "What was Novak Djokovic's highest ranking?",
        "expected_answer": "1",
        "expected_sql": "SELECT MIN(winner_rank) as highest_ranking FROM matches WHERE winner_name = 'Novak Djokovic' AND winner_rank IS NOT NULL",
        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ["Djokovic", "highest", "ranking"]
    },

    # MATCH DETAILS (10 questions)
    {
        "id": 86,
        "question": "What was the score of the 2008 Wimbledon final?",
        "expected_answer": "Nadal defeated Federer 6-4, 6-4, 6-7(5), 6-7(8), 9-7",
        "expected_sql": "SELECT winner_name, loser_name, score FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2008 AND round = 'F'",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ["score", "2008", "Wimbledon", "final"]
    },
    {
        "id": 87,
        "question": "Who won the longest match in tennis history?",
        "expected_answer": "John Isner",
        "expected_sql": "SELECT winner_name FROM matches WHERE minutes = (SELECT MAX(minutes) FROM matches WHERE minutes IS NOT NULL)",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ["longest", "match", "tennis", "history"]
    },
    {
        "id": 88,
        "question": "What was the duration of the 2010 Wimbledon match between Isner and Mahut?",
        "expected_answer": "665 minutes",
        "expected_sql": "SELECT minutes FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2010 AND ((winner_name = 'John Isner' AND loser_name = 'Nicolas Mahut') OR (winner_name = 'Nicolas Mahut' AND loser_name = 'John Isner'))",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "hard",
        "keywords": ["duration", "2010", "Wimbledon", "Isner", "Mahut"]
    },
    {
        "id": 89,
        "question": "What was the score of the 2019 Wimbledon final?",
        "expected_answer": "Djokovic defeated Federer 7-6(5), 1-6, 7-6(4), 4-6, 13-12(3)",
        "expected_sql": "SELECT winner_name, loser_name, score FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2019 AND round = 'F'",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ["score", "2019", "Wimbledon", "final"]
    },
    {
        "id": 90,
        "question": "Who won the 2012 Australian Open final?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Australian Open' AND event_year = 2012 AND round = 'F'",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "easy",
        "keywords": ["2012", "Australian Open", "final"]
    },
    {
        "id": 91,
        "question": "What was the score of the 2017 Australian Open final?",
        "expected_answer": "Federer defeated Nadal 6-4, 3-6, 6-1, 3-6, 6-3",
        "expected_sql": "SELECT winner_name, loser_name, score FROM matches WHERE tourney_name = 'Australian Open' AND event_year = 2017 AND round = 'F'",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ["score", "2017", "Australian Open", "final"]
    },
    {
        "id": 92,
        "question": "Who won the 2016 Wimbledon final?",
        "expected_answer": "Andy Murray",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2016 AND round = 'F'",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "easy",
        "keywords": ["2016", "Wimbledon", "final"]
    },
    {
        "id": 93,
        "question": "What was the duration of the longest match in 2020?",
        "expected_answer": "5 hours 29 minutes",
        "expected_sql": "SELECT MAX(minutes) as longest_match FROM matches WHERE event_year = 2020 AND minutes IS NOT NULL",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "hard",
        "keywords": ["duration", "longest", "match", "2020"]
    },
    {
        "id": 94,
        "question": "Who won the 2018 US Open final?",
        "expected_answer": "Novak Djokovic",
        "expected_sql": "SELECT winner_name FROM matches WHERE tourney_name = 'US Open' AND event_year = 2018 AND round = 'F'",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "easy",
        "keywords": ["2018", "US Open", "final"]
    },
    {
        "id": 95,
        "question": "What was the score of the 2021 French Open final?",
        "expected_answer": "Djokovic defeated Tsitsipas 6-7(6), 2-6, 6-3, 6-2, 6-4",
        "expected_sql": "SELECT winner_name, loser_name, score FROM matches WHERE tourney_name = 'Roland Garros' AND event_year = 2021 AND round = 'F'",
        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ["score", "2021", "French Open", "final"]
    },

    # COMPLEX QUERIES (5 questions)
    {
        "id": 96,
        "question": "Compare Federer and Nadal's performance on different surfaces",
        "expected_answer": "Federer excels on grass and hard courts, while Nadal dominates on clay",
        "expected_sql": "SELECT surface, winner_name, COUNT(*) as wins FROM matches WHERE winner_name IN ('Roger Federer', 'Rafael Nadal') GROUP BY surface, winner_name ORDER BY surface, wins DESC",
        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ["compare", "Federer", "Nadal", "performance", "surfaces"]
    },
    {
        "id": 97,
        "question": "Which players have won all four Grand Slams?",
        "expected_answer": "Rod Laver, Andre Agassi, Roger Federer, Rafael Nadal, Novak Djokovic",
        "expected_sql": "SELECT winner_name, COUNT(DISTINCT tourney_name) as slams_won FROM matches WHERE tourney_level = 'G' AND round = 'F' AND tourney_name IN ('Australian Open', 'French Open', 'Wimbledon', 'US Open') GROUP BY winner_name HAVING COUNT(DISTINCT tourney_name) = 4",
        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ["players", "won", "four", "Grand Slams"]
    },
    {
        "id": 98,
        "question": "Analyze the evolution of tennis over the decades",
        "expected_answer": "Tennis has evolved with changes in equipment, playing styles, and physical demands",
        "expected_sql": "SELECT event_year, AVG(minutes) as avg_duration, AVG(winner_age) as avg_age FROM matches WHERE event_year >= 1970 GROUP BY event_year ORDER BY event_year",
        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ["analyze", "evolution", "tennis", "decades"]
    },
    {
        "id": 99,
        "question": "Which players have the most consistent performance across all surfaces?",
        "expected_answer": "Novak Djokovic and Roger Federer show the most consistent performance",
        "expected_sql": "SELECT winner_name, COUNT(DISTINCT surface) as surfaces_won, AVG(CASE WHEN winner_name = winner_name THEN 1 ELSE 0 END) as win_rate FROM matches GROUP BY winner_name HAVING COUNT(DISTINCT surface) >= 3 ORDER BY win_rate DESC",
        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ["players", "consistent", "performance", "surfaces"]
    },
    {
        "id": 100,
        "question": "What are the key factors that determine tennis success?",
        "expected_answer": "Key factors include serve quality, return ability, mental toughness, and physical fitness",
        "expected_sql": "SELECT winner_name, AVG(w_ace) as avg_aces, AVG(w_df) as avg_double_faults, AVG(minutes) as avg_duration FROM matches WHERE w_ace IS NOT NULL GROUP BY winner_name ORDER BY avg_aces DESC",
        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ["key", "factors", "tennis", "success"]
    }
]


def get_test_categories() -> Dict[str, int]:
    """
    Get the count of test cases by category.
    
    Returns:
        Dictionary with category names and their counts
    """
    category_counts = {}
    for test_case in TENNIS_QA_DATASET:
        category = test_case["category"].value
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return category_counts


def get_tests_by_category(category: TestCategory) -> List[Dict[str, Any]]:
    """
    Get all test cases for a specific category.
    
    Args:
        category: The test category to filter by
        
    Returns:
        List of test cases for the specified category
    """
    return [test_case for test_case in TENNIS_QA_DATASET if test_case["category"] == category]


def get_tests_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """
    Get all test cases for a specific difficulty level.
    
    Args:
        difficulty: The difficulty level to filter by
        
    Returns:
        List of test cases for the specified difficulty
    """
    return [test_case for test_case in TENNIS_QA_DATASET if test_case["difficulty"] == difficulty]


def get_random_test_sample(size: int = 10) -> List[Dict[str, Any]]:
    """
    Get a random sample of test cases.
    
    Args:
        size: Number of test cases to return
        
    Returns:
        List of randomly selected test cases
    """
    import random
    return random.sample(TENNIS_QA_DATASET, min(size, len(TENNIS_QA_DATASET)))
