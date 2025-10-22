"""
Terminology analysis utilities for AskTennis AI application.
Handles tennis terminology analysis and mapping recommendations.
Extracted from ml_analytics.py for better modularity.
"""

from collections import defaultdict
from typing import Dict, List, Any


class TerminologyAnalyzer:
    """
    Centralized terminology analysis class for tennis application.
    Handles tennis terminology analysis and mapping recommendations.
    """
    
    def __init__(self):
        """Initialize the terminology analyzer."""
        pass
    
    def analyze_tennis_terminology(self, query_texts: List[str]) -> Dict[str, Any]:
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
    
    def get_terminology_summary(self, terminology_data: Dict[str, Any]) -> str:
        """Get a summary of terminology analysis."""
        coverage = terminology_data.get('terminology_coverage', {})
        
        surface_queries = coverage.get('surface_queries', 0)
        tour_queries = coverage.get('tour_queries', 0)
        hand_queries = coverage.get('hand_queries', 0)
        round_queries = coverage.get('round_queries', 0)
        usage_percentage = coverage.get('terminology_usage_percentage', 0)
        
        summary = f"Terminology usage: {usage_percentage}% of queries use tennis terminology"
        summary += f" (Surface: {surface_queries}, Tour: {tour_queries}, Hand: {hand_queries}, Round: {round_queries})"
        
        return summary
    
    def get_terminology_health_score(self, terminology_data: Dict[str, Any]) -> int:
        """Calculate a terminology health score (0-100)."""
        coverage = terminology_data.get('terminology_coverage', {})
        usage_percentage = coverage.get('terminology_usage_percentage', 0)
        colloquial_terms = len(terminology_data.get('colloquial_terms_detected', []))
        
        # Base score from terminology usage
        score = min(100, usage_percentage)
        
        # Bonus for high terminology usage
        if usage_percentage > 50:
            score += 10
        elif usage_percentage > 30:
            score += 5
        
        # Deduct for too many colloquial terms (indicates mapping issues)
        if colloquial_terms > 20:
            score -= 15
        elif colloquial_terms > 10:
            score -= 10
        elif colloquial_terms > 5:
            score -= 5
        
        return max(0, min(100, score))
