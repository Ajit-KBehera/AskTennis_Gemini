"""
Query analysis utilities for AskTennis AI application.
Handles user query pattern analysis and categorization.
Extracted from ml_analytics.py for better modularity.
"""

import re
import numpy as np
from collections import Counter, defaultdict
from typing import Dict, List, Any


class QueryAnalyzer:
    """
    Centralized query analysis class for tennis application queries.
    Handles query pattern analysis, categorization, and coverage detection.
    """
    
    def __init__(self):
        """Initialize the query analyzer."""
        pass
    
    def analyze_query_patterns(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze user query patterns using ML techniques."""
        queries = [log for log in log_data if log.get('type') == 'user_query']
        
        if not queries:
            return {"message": "No user queries found in logs"}
        
        # Basic statistics
        total_queries = len(queries)
        unique_sessions = len(set(log.get('session') for log in queries))
        
        # Query length analysis
        query_lengths = [len(log.get('query', '')) for log in queries]
        avg_query_length = np.mean(query_lengths) if query_lengths else 0
        
        # Common query patterns
        query_texts = [log.get('query', '') for log in queries]
        word_frequencies = Counter()
        for query in query_texts:
            words = re.findall(r'\b\w+\b', query.lower())
            word_frequencies.update(words)
        
        # Query categories (simple classification)
        categories = {
            'player_stats': 0,
            'head_to_head': 0,
            'tournament': 0,
            'ranking': 0,
            'surface': 0,
            'year': 0,
            'other': 0
        }
        
        # Tennis terminology analysis
        terminology_analysis = self._analyze_tennis_terminology(query_texts)
        
        # Enhanced analysis for tournament queries
        tournament_queries = []
        incomplete_coverage_queries = []
        
        for query in query_texts:
            query_lower = query.lower()
            if any(word in query_lower for word in ['win', 'match', 'victory', 'defeat']):
                categories['player_stats'] += 1
            elif any(word in query_lower for word in ['vs', 'against', 'head', 'h2h']):
                categories['head_to_head'] += 1
            elif any(word in query_lower for word in ['tournament', 'grand slam', 'wimbledon', 'us open']):
                categories['tournament'] += 1
            elif any(word in query_lower for word in ['rank', 'ranking', 'position']):
                categories['ranking'] += 1
            elif any(word in query_lower for word in ['clay', 'grass', 'hard', 'surface']):
                categories['surface'] += 1
            elif any(word in query_lower for word in ['2020', '2021', '2022', '2023', '2024', 'year']):
                categories['year'] += 1
            else:
                categories['other'] += 1
            
            # Detect tournament queries that might need both ATP and WTA coverage
            if any(tournament in query_lower for tournament in ['basel', 'rome', 'madrid', 'indian wells', 'miami', 'monte carlo', 'hamburg', 'stuttgart', 'eastbourne', 'newport', 'atlanta', 'washington', 'toronto', 'montreal', 'cincinnati', 'winston salem', 'stockholm', 'antwerp', 'vienna', 'paris']):
                tournament_queries.append(query)
                # Check if query is generic (no gender specification)
                if not any(gender_word in query_lower for gender_word in ['men', 'women', 'male', 'female', 'atp', 'wta']):
                    incomplete_coverage_queries.append(query)
            
            # Detect tournament winner queries that might be missing Final round filter
            if any(word in query_lower for word in ['won', 'winner', 'champion']) and any(tournament in query_lower for tournament in ['wimbledon', 'french open', 'roland garros', 'us open', 'australian open', 'aus open', 'rome', 'basel', 'madrid']):
                # Check if round is explicitly specified
                if not any(round_word in query_lower for round_word in ['final', 'semi', 'quarter', 'round', 'f', 'sf', 'qf']):
                    # This is a tournament winner query without explicit round - should default to Final
                    tournament_queries.append(f"{query} (implicit Final)")
        
        return {
            'total_queries': total_queries,
            'unique_sessions': unique_sessions,
            'avg_query_length': round(avg_query_length, 2),
            'most_common_words': dict(word_frequencies.most_common(10)),
            'query_categories': categories,
            'category_percentages': {k: round(v/total_queries*100, 2) for k, v in categories.items()},
            'tournament_queries': tournament_queries,
            'incomplete_coverage_queries': incomplete_coverage_queries,
            'coverage_issues': self._analyze_coverage_issues(incomplete_coverage_queries),
            'tennis_terminology': terminology_analysis
        }
    
    def _analyze_coverage_issues(self, incomplete_queries: List[str]) -> Dict[str, Any]:
        """Analyze coverage issues in tournament queries."""
        if not incomplete_queries:
            return {"message": "No coverage issues detected"}
        
        # Analyze the specific problem
        basel_queries = [q for q in incomplete_queries if 'basel' in q.lower()]
        rome_queries = [q for q in incomplete_queries if 'rome' in q.lower()]
        
        coverage_analysis = {
            'total_incomplete_queries': len(incomplete_queries),
            'basel_queries': basel_queries,
            'rome_queries': rome_queries,
            'problem_description': "Generic tournament queries missing gender specification",
            'recommendations': [
                "For generic tournament queries, search both ATP and WTA tables",
                "Add gender detection to query understanding",
                "Implement comprehensive tournament coverage",
                "Suggest both men's and women's results when applicable"
            ],
            'sql_improvements': [
                "Use UNION to combine ATP and WTA results",
                "Add tournament_type column to distinguish men's/women's",
                "Implement smart query expansion for generic questions"
            ]
        }
        
        return coverage_analysis
    
    def _analyze_tennis_terminology(self, query_texts: List[str]) -> Dict[str, Any]:
        """Analyze tennis terminology usage in queries."""
        # Tennis terminology patterns
        surface_terms = {
            'clay': ['clay court', 'red clay', 'terre battue', 'dirt', 'slow court'],
            'hard': ['hard court', 'concrete', 'asphalt', 'acrylic', 'deco turf', 'plexicushion', 'fast court'],
            'grass': ['grass court', 'lawn', 'natural grass', 'very fast court', 'quick court'],
            'carpet': ['carpet court', 'synthetic', 'artificial', 'indoor carpet']
        }
        
        tour_terms = {
            'atp': ['atp tour', 'men\'s tour', 'men tour', 'men', 'male'],
            'wta': ['wta tour', 'women\'s tour', 'women tour', 'women', 'female', 'ladies'],
            'challenger': ['challenger tour', 'development tour', 'challenger'],
            'futures': ['futures tour', 'itf futures', 'futures'],
            'itf': ['itf tour', 'junior tour', 'development', 'itf']
        }
        
        hand_terms = {
            'right': ['right-handed', 'righty', 'right hand', 'right handed'],
            'left': ['left-handed', 'lefty', 'left handed', 'southpaw'],
            'ambidextrous': ['ambidextrous', 'both hands', 'switch', 'either']
        }
        
        round_terms = {
            'final': ['final', 'finals', 'championship', 'champion', 'winner'],
            'semi': ['semi-final', 'semi finals', 'semifinal', 'semifinals', 'semi', 'last four', 'last 4'],
            'quarter': ['quarter-final', 'quarter finals', 'quarterfinal', 'quarterfinals', 'quarter', 'quarters', 'last eight', 'last 8'],
            'round16': ['round of 16', 'round 16', 'last 16', 'fourth round', '4th round'],
            'round32': ['round of 32', 'round 32', 'third round', '3rd round'],
            'round64': ['round of 64', 'round 64', 'second round', '2nd round'],
            'round128': ['round of 128', 'round 128', 'first round', '1st round'],
            'qualifying': ['qualifying', 'qualifier', 'qualifying 1', 'qualifying 2', 'qualifying 3'],
            'round_robin': ['round robin', 'group stage', 'group']
        }
        
        # Analyze terminology usage
        terminology_stats = {
            'surface_usage': defaultdict(int),
            'tour_usage': defaultdict(int),
            'hand_usage': defaultdict(int),
            'round_usage': defaultdict(int),
            'colloquial_terms_detected': [],
            'mapping_opportunities': [],
            'terminology_coverage': {}
        }
        
        for query in query_texts:
            query_lower = query.lower()
            
            # Surface terminology detection
            for surface_type, terms in surface_terms.items():
                for term in terms:
                    if term in query_lower:
                        terminology_stats['surface_usage'][surface_type] += 1
                        if term != surface_type:  # Colloquial term detected
                            terminology_stats['colloquial_terms_detected'].append(f"Surface: '{term}' in query: '{query}'")
            
            # Tour terminology detection
            for tour_type, terms in tour_terms.items():
                for term in terms:
                    if term in query_lower:
                        terminology_stats['tour_usage'][tour_type] += 1
                        if term != tour_type:  # Colloquial term detected
                            terminology_stats['colloquial_terms_detected'].append(f"Tour: '{term}' in query: '{query}'")
            
            # Hand terminology detection
            for hand_type, terms in hand_terms.items():
                for term in terms:
                    if term in query_lower:
                        terminology_stats['hand_usage'][hand_type] += 1
                        if term != hand_type:  # Colloquial term detected
                            terminology_stats['colloquial_terms_detected'].append(f"Hand: '{term}' in query: '{query}'")
            
            # Round terminology detection
            for round_type, terms in round_terms.items():
                for term in terms:
                    if term in query_lower:
                        terminology_stats['round_usage'][round_type] += 1
                        if term != round_type:  # Colloquial term detected
                            terminology_stats['colloquial_terms_detected'].append(f"Round: '{term}' in query: '{query}'")
        
        # Calculate terminology coverage
        total_queries = len(query_texts)
        terminology_stats['terminology_coverage'] = {
            'surface_queries': sum(terminology_stats['surface_usage'].values()),
            'tour_queries': sum(terminology_stats['tour_usage'].values()),
            'hand_queries': sum(terminology_stats['hand_usage'].values()),
            'round_queries': sum(terminology_stats['round_usage'].values()),
            'colloquial_terms_found': len(terminology_stats['colloquial_terms_detected']),
            'terminology_usage_percentage': round(
                (sum(terminology_stats['surface_usage'].values()) + 
                 sum(terminology_stats['tour_usage'].values()) + 
                 sum(terminology_stats['hand_usage'].values()) + 
                 sum(terminology_stats['round_usage'].values())) / total_queries * 100, 2
            ) if total_queries > 0 else 0
        }
        
        # Generate mapping opportunities
        terminology_stats['mapping_opportunities'] = self._generate_terminology_recommendations(
            terminology_stats['colloquial_terms_detected'],
            terminology_stats['surface_usage'],
            terminology_stats['tour_usage'],
            terminology_stats['hand_usage'],
            terminology_stats['round_usage']
        )
        
        return terminology_stats
    
    def _generate_terminology_recommendations(self, colloquial_terms: List[str], 
                                           surface_usage: Dict, tour_usage: Dict, 
                                           hand_usage: Dict, round_usage: Dict) -> List[str]:
        """Generate recommendations for tennis terminology improvements."""
        recommendations = []
        
        # Surface terminology recommendations
        if surface_usage.get('clay', 0) > 0:
            recommendations.append("Consider adding clay court surface detection for better query understanding")
        if surface_usage.get('grass', 0) > 0:
            recommendations.append("Grass court queries detected - ensure proper surface mapping")
        
        # Tour terminology recommendations
        if tour_usage.get('atp', 0) > 0 and tour_usage.get('wta', 0) > 0:
            recommendations.append("Both ATP and WTA queries detected - ensure combined tournament coverage")
        if tour_usage.get('challenger', 0) > 0:
            recommendations.append("Challenger tour queries detected - consider development tour coverage")
        
        # Hand terminology recommendations
        if hand_usage.get('left', 0) > 0:
            recommendations.append("Left-handed player queries detected - ensure southpaw terminology support")
        if hand_usage.get('ambidextrous', 0) > 0:
            recommendations.append("Ambidextrous player queries detected - ensure switch-hitter terminology")
        
        # Round terminology recommendations
        if round_usage.get('semi', 0) > 0 or round_usage.get('quarter', 0) > 0:
            recommendations.append("Tournament round queries detected - ensure proper round mapping")
        if round_usage.get('qualifying', 0) > 0:
            recommendations.append("Qualifying round queries detected - ensure Q1/Q2/Q3 mapping")
        
        # Colloquial terms recommendations
        if len(colloquial_terms) > 0:
            recommendations.append(f"Found {len(colloquial_terms)} colloquial tennis terms - ensure mapping tools are working")
            recommendations.append("Consider expanding tennis terminology dictionary")
        
        return recommendations
