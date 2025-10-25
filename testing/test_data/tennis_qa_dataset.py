"""
Updated tennis Q&A dataset with verified working SQL queries.
All SQL queries have been tested against tennis_data.db.
"""

from typing import List, Dict, Any
from .test_categories import TestCategory


# Updated Tennis Q&A Test Cases with Working SQL
TENNIS_QA_DATASET: List[Dict[str, Any]] = [
    {
        "id": 1,
        "question": "Who won Wimbledon in 2022?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Wimbledon', '2022', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 2,
        "question": "Who won the French Open in 2021?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['French Open', '2021', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 3,
        "question": "Who won the US Open in 2020?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['US Open', '2020', 'winner'],
        "sql_verified": True}{
        "id": 4,
        "question": "Who won the Australian Open in 2023?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Australian Open', '2023', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 5,
        "question": "Who won Wimbledon in 2019?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Wimbledon', '2019', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 6,
        "question": "Who won the French Open in 2020?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['French Open', '2020', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 7,
        "question": "Who won the US Open in 2019?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['US Open', '2019', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 8,
        "question": "Who won the Australian Open in 2022?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Australian Open', '2022', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 9,
        "question": "Who won Wimbledon in 2018?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Wimbledon', '2018', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 10,
        "question": "Who won the French Open in 2019?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['French Open', '2019', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 11,
        "question": "Who won the US Open in 2018?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['US Open', '2018', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 12,
        "question": "Who won the Australian Open in 2021?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Australian Open', '2021', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 13,
        "question": "Who won Wimbledon in 2017?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Wimbledon', '2017', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 14,
        "question": "Who won the French Open in 2018?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['French Open', '2018', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 15,
        "question": "Who won the US Open in 2017?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['US Open', '2017', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 16,
        "question": "Who won the Australian Open in 2020?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Australian Open', '2020', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 17,
        "question": "Who won Wimbledon in 2016?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Wimbledon', '2016', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 18,
        "question": "Who won the French Open in 2017?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['French Open', '2017', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 19,
        "question": "Who won the US Open in 2016?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['US Open', '2016', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 20,
        "question": "Who won the Australian Open in 2019?",        "category": TestCategory.TOURNAMENT_WINNER,
        "difficulty": "easy",
        "keywords": ['Australian Open', '2019', 'winner'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 21,
        "question": "What is the head-to-head record between Roger Federer and Rafael Nadal?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Federer', 'Nadal', 'head-to-head', 'record'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 22,
        "question": "How many times has Novak Djokovic beaten Andy Murray?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Djokovic', 'Murray', 'beaten', 'times'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 23,
        "question": "What is the head-to-head record between Serena Williams and Venus Williams?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Serena Williams', 'Venus Williams', 'head-to-head'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 24,
        "question": "How many times has Rafael Nadal beaten Roger Federer?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Nadal', 'Federer', 'beaten', 'times'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 25,
        "question": "What is the head-to-head record between Novak Djokovic and Roger Federer?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Djokovic', 'Federer', 'head-to-head'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 26,
        "question": "How many times has Andy Murray beaten Novak Djokovic?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Murray', 'Djokovic', 'beaten', 'times'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 27,
        "question": "What is the head-to-head record between Rafael Nadal and Novak Djokovic?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Nadal', 'Djokovic', 'head-to-head'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 28,
        "question": "How many times has Roger Federer beaten Rafael Nadal?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Federer', 'Nadal', 'beaten', 'times'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 29,
        "question": "What is the head-to-head record between Andy Murray and Roger Federer?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Murray', 'Federer', 'head-to-head'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 30,
        "question": "How many times has Novak Djokovic beaten Rafael Nadal?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Djokovic', 'Nadal', 'beaten', 'times'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 31,
        "question": "What is the head-to-head record between Andy Murray and Rafael Nadal?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Murray', 'Nadal', 'head-to-head'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 32,
        "question": "How many times has Rafael Nadal beaten Andy Murray?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Nadal', 'Murray', 'beaten', 'times'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 33,
        "question": "What is the head-to-head record between Novak Djokovic and Andy Murray?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Djokovic', 'Murray', 'head-to-head'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 34,
        "question": "How many times has Roger Federer beaten Novak Djokovic?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Federer', 'Djokovic', 'beaten', 'times'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 35,
        "question": "What is the head-to-head record between Roger Federer and Andy Murray?",        "category": TestCategory.HEAD_TO_HEAD,
        "difficulty": "medium",
        "keywords": ['Federer', 'Murray', 'head-to-head'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 36,
        "question": "Who has the best record on clay courts?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['clay', 'courts', 'best', 'record'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 37,
        "question": "Which players perform best on grass courts?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['grass', 'courts', 'perform', 'best'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 38,
        "question": "What is Rafael Nadal's win percentage on clay?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ['Nadal', 'clay', 'win', 'percentage'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 39,
        "question": "Who has the most wins on hard courts?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['hard', 'courts', 'most', 'wins'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 40,
        "question": "Which surface does Novak Djokovic perform best on?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ['Djokovic', 'surface', 'perform', 'best'],
        "sql_verified": True,
        "sql_results_count": 4}{
        "id": 41,
        "question": "What is Roger Federer's win percentage on grass?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ['Federer', 'grass', 'win', 'percentage'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 42,
        "question": "Who has the best record on indoor courts?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['indoor', 'courts', 'best', 'record'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 43,
        "question": "Which players have the most wins on clay in 2020?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['clay', '2020', 'most', 'wins'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 44,
        "question": "What is Andy Murray's win percentage on grass?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ['Murray', 'grass', 'win', 'percentage'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 45,
        "question": "Who has the most wins on hard courts in 2021?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['hard', 'courts', '2021', 'most', 'wins'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 46,
        "question": "Which surface produces the most upsets?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ['surface', 'upsets', 'most'],
        "sql_verified": True,
        "sql_results_count": 4}{
        "id": 47,
        "question": "What is Novak Djokovic's win percentage on hard courts?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ['Djokovic', 'hard', 'courts', 'win', 'percentage'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 48,
        "question": "Who has the most wins on grass courts in 2019?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['grass', 'courts', '2019', 'most', 'wins'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 49,
        "question": "Which players have the best record on carpet courts?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "medium",
        "keywords": ['carpet', 'courts', 'best', 'record'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 50,
        "question": "What is Rafael Nadal's win percentage on hard courts?",        "category": TestCategory.SURFACE_PERFORMANCE,
        "difficulty": "hard",
        "keywords": ['Nadal', 'hard', 'courts', 'win', 'percentage'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 51,
        "question": "Who has the most Grand Slam titles?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "easy",
        "keywords": ['Grand Slam', 'titles', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 52,
        "question": "Which player has the highest ranking?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ['player', 'highest', 'ranking'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 53,
        "question": "What is the average age of top 10 players?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ['average', 'age', 'top 10', 'players'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 54,
        "question": "Who has the most ATP titles?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ['ATP', 'titles', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 55,
        "question": "Which player has the most aces in 2023?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ['player', 'aces', '2023', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 56,
        "question": "What is the longest match duration in minutes?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ['longest', 'match', 'duration', 'minutes'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 57,
        "question": "Who has the most matches at number 1 ranking?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ['matches', 'number 1', 'ranking'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 58,
        "question": "Which player has the most double faults in 2022?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ['player', 'double faults', '2022', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 59,
        "question": "What is the average match duration in Grand Slams?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ['average', 'match', 'duration', 'Grand Slams'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 60,
        "question": "Who has the most wins in a single year?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "medium",
        "keywords": ['wins', 'single year', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 61,
        "question": "Which player has the highest first serve percentage?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ['player', 'first serve', 'percentage', 'highest'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 62,
        "question": "What is the most common score in tennis matches?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ['common', 'score', 'tennis', 'matches'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 63,
        "question": "Who has the most bagels (6-0 sets) in their career?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ['bagels', '6-0', 'sets', 'career', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 64,
        "question": "Which player has the most tiebreaks won?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ['player', 'tiebreaks', 'won', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 65,
        "question": "What is the average height of top 100 players?",        "category": TestCategory.STATISTICAL_ANALYSIS,
        "difficulty": "hard",
        "keywords": ['average', 'height', 'top 100', 'players'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 66,
        "question": "Who was the youngest Wimbledon champion?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ['youngest', 'Wimbledon', 'champion'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 67,
        "question": "Which player has the longest winning streak?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ['player', 'longest', 'winning', 'streak'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 68,
        "question": "Who won the most matches in a single year?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ['matches', 'single year', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 69,
        "question": "Which player has the most consecutive Grand Slam finals?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ['player', 'consecutive', 'Grand Slam', 'finals'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 70,
        "question": "Who was the oldest player to win a Grand Slam?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ['oldest', 'player', 'Grand Slam'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 71,
        "question": "Which player has the most career wins?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "easy",
        "keywords": ['player', 'career', 'wins', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 72,
        "question": "Who has the most consecutive weeks at number 1?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ['consecutive', 'weeks', 'number 1'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 73,
        "question": "Which player has the most 5-set match wins?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "medium",
        "keywords": ['player', '5-set', 'match', 'wins', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 74,
        "question": "Who has the most wins against top 10 players?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ['wins', 'top 10', 'players', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 75,
        "question": "Which player has the most tournament wins in a single year?",        "category": TestCategory.HISTORICAL_RECORDS,
        "difficulty": "hard",
        "keywords": ['player', 'tournament', 'wins', 'single year', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 76,
        "question": "Who was ranked number 1 in 2020?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ['ranked', 'number 1', '2020'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 77,
        "question": "Which players were in the top 10 in 2019?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ['players', 'top 10', '2019'],
        "sql_verified": True,
        "sql_results_count": 10}{
        "id": 78,
        "question": "What was Roger Federer's highest ranking?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ['Federer', 'highest', 'ranking'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 79,
        "question": "Who was ranked number 1 in 2018?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ['ranked', 'number 1', '2018'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 80,
        "question": "Which player has spent the most weeks at number 1?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "hard",
        "keywords": ['player', 'weeks', 'number 1', 'most'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 81,
        "question": "Who was ranked number 1 in 2017?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ['ranked', 'number 1', '2017'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 82,
        "question": "What was Rafael Nadal's highest ranking?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ['Nadal', 'highest', 'ranking'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 83,
        "question": "Who was ranked number 1 in 2016?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "easy",
        "keywords": ['ranked', 'number 1', '2016'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 84,
        "question": "Which players were in the top 5 in 2020?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ['players', 'top 5', '2020'],
        "sql_verified": True,
        "sql_results_count": 5}{
        "id": 85,
        "question": "What was Novak Djokovic's highest ranking?",        "category": TestCategory.PLAYER_RANKINGS,
        "difficulty": "medium",
        "keywords": ['Djokovic', 'highest', 'ranking'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 86,
        "question": "What was the score of the 2008 Wimbledon final?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ['score', '2008', 'Wimbledon', 'final'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 87,
        "question": "Who won the longest match in tennis history?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ['longest', 'match', 'tennis', 'history'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 88,
        "question": "What was the duration of the 2010 Wimbledon match between Isner and Mahut?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "hard",
        "keywords": ['duration', '2010', 'Wimbledon', 'Isner', 'Mahut'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 89,
        "question": "What was the score of the 2019 Wimbledon final?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ['score', '2019', 'Wimbledon', 'final'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 90,
        "question": "Who won the 2012 Australian Open final?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "easy",
        "keywords": ['2012', 'Australian Open', 'final'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 91,
        "question": "What was the score of the 2017 Australian Open final?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ['score', '2017', 'Australian Open', 'final'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 92,
        "question": "Who won the 2016 Wimbledon final?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "easy",
        "keywords": ['2016', 'Wimbledon', 'final'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 93,
        "question": "What was the duration of the longest match in 2020?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "hard",
        "keywords": ['duration', 'longest', 'match', '2020'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 94,
        "question": "Who won the 2018 US Open final?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "easy",
        "keywords": ['2018', 'US Open', 'final'],
        "sql_verified": True,
        "sql_results_count": 2}{
        "id": 95,
        "question": "What was the score of the 2021 French Open final?",        "category": TestCategory.MATCH_DETAILS,
        "difficulty": "medium",
        "keywords": ['score', '2021', 'French Open', 'final'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 96,
        "question": "Compare Federer and Nadal's performance on different surfaces",        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ['compare', 'Federer', 'Nadal', 'performance', 'surfaces'],
        "sql_verified": True,
        "sql_results_count": 4}{
        "id": 97,
        "question": "Which players have won all four Grand Slams?",        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ['players', 'won', 'four', 'Grand Slams'],
        "sql_verified": True,
        "sql_results_count": 3}{
        "id": 98,
        "question": "Analyze the evolution of tennis over the decades",        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ['analyze', 'evolution', 'tennis', 'decades'],
        "sql_verified": True,
        "sql_results_count": 3}{
        "id": 99,
        "question": "Which players have the most consistent performance across all surfaces?",        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ['players', 'consistent', 'performance', 'surfaces'],
        "sql_verified": True,
        "sql_results_count": 1}{
        "id": 100,
        "question": "What are the key factors that determine tennis success?",        "category": TestCategory.COMPLEX_QUERIES,
        "difficulty": "hard",
        "keywords": ['key', 'factors', 'tennis', 'success'],
        "sql_verified": True,
        "sql_results_count": 10}
]


def get_test_categories():
    """
    Get all unique test categories from the dataset.
    
    Returns:
        List of unique test categories
    """
    categories = set()
    for test_case in TENNIS_QA_DATASET:
        if 'category' in test_case:
            categories.add(test_case['category'])
    return list(categories)
