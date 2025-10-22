"""
Error analysis utilities for AskTennis AI application.
Handles error pattern detection and prevention recommendations.
Extracted from ml_analytics.py for better modularity.
"""

from collections import Counter, defaultdict
from typing import Dict, List, Any


class ErrorAnalyzer:
    """
    Centralized error analysis class for tennis application.
    Handles error pattern detection and prevention recommendations.
    """
    
    def __init__(self):
        """Initialize the error analyzer."""
        pass
    
    def analyze_errors(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns and provide insights."""
        errors = [log for log in log_data if log.get('type') == 'error']
        
        if not errors:
            return {"message": "No errors found in logs - great!"}
        
        # Error categorization
        error_contexts = [log.get('context', '') for log in errors]
        error_messages = [log.get('error_message', '') for log in errors]
        
        # Common error patterns
        context_patterns = Counter()
        for context in error_contexts:
            if context:
                context_patterns[context] += 1
        
        # Error frequency by session
        session_errors = defaultdict(int)
        for error in errors:
            session = error.get('session', 'unknown')
            session_errors[session] += 1
        
        return {
            'total_errors': len(errors),
            'unique_error_contexts': len(set(error_contexts)),
            'most_common_error_contexts': dict(context_patterns.most_common(5)),
            'sessions_with_errors': len(session_errors),
            'error_prone_sessions': dict(sorted(session_errors.items(), key=lambda x: x[1], reverse=True)[:5]),
            'error_recommendations': self._generate_error_recommendations(context_patterns)
        }
    
    def _generate_error_recommendations(self, context_patterns: Counter) -> List[str]:
        """Generate error prevention recommendations."""
        recommendations = []
        
        if 'Tool execution failed' in str(context_patterns):
            recommendations.append("Improve tool error handling and validation")
        
        if 'Database connection' in str(context_patterns):
            recommendations.append("Implement connection pooling and retry logic")
        
        if 'API' in str(context_patterns):
            recommendations.append("Add API rate limiting and error handling")
        
        return recommendations
    
    def get_error_summary(self, error_data: Dict[str, Any]) -> str:
        """Get a summary of error metrics."""
        if 'message' in error_data:
            return error_data['message']
        
        total_errors = error_data.get('total_errors', 0)
        sessions_with_errors = error_data.get('sessions_with_errors', 0)
        
        if total_errors == 0:
            return "No errors detected - excellent system health!"
        
        return f"Detected {total_errors} errors across {sessions_with_errors} sessions"
    
    def get_error_health_score(self, error_data: Dict[str, Any]) -> int:
        """Calculate an error health score (0-100)."""
        if 'message' in error_data:
            return 100  # No errors = perfect score
        
        total_errors = error_data.get('total_errors', 0)
        sessions_with_errors = error_data.get('sessions_with_errors', 0)
        
        if total_errors == 0:
            return 100
        
        # Calculate score based on error frequency
        score = 100
        
        # Deduct points for high error count
        if total_errors > 50:
            score -= 40
        elif total_errors > 20:
            score -= 25
        elif total_errors > 10:
            score -= 15
        elif total_errors > 5:
            score -= 10
        
        # Deduct points for many sessions with errors
        if sessions_with_errors > 10:
            score -= 20
        elif sessions_with_errors > 5:
            score -= 15
        elif sessions_with_errors > 2:
            score -= 10
        
        return max(0, score)
