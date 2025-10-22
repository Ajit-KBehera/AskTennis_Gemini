"""
ML Analytics Integration for AskTennis AI application.
Handles ML analytics, coverage detection, and performance analysis.
Extracted from ui_components.py for better modularity.
"""

import streamlit as st
from ml_analytics import TennisLogAnalyzer


class MLIntegration:
    """
    Centralized ML analytics integration class.
    Handles ML analysis, coverage detection, and performance insights.
    """
    
    def __init__(self):
        """Initialize the ML integration."""
        self.analyzer = TennisLogAnalyzer()
    
    def detect_coverage_issue_realtime(self, query: str) -> dict:
        """Detect potential coverage issues in real-time."""
        query_lower = query.lower()
        
        # Combined tournaments that have both ATP and WTA
        combined_tournaments = [
            'rome', 'basel', 'madrid', 'indian wells', 'miami', 'monte carlo', 
            'hamburg', 'stuttgart', 'eastbourne', 'newport', 'atlanta', 
            'washington', 'toronto', 'montreal', 'cincinnati', 'winston salem', 
            'stockholm', 'antwerp', 'vienna', 'paris'
        ]
        
        is_tournament_query = any(tournament in query_lower for tournament in combined_tournaments)
        has_gender_spec = any(gender_word in query_lower for gender_word in ['men', 'women', 'male', 'female', 'atp', 'wta'])
        
        if is_tournament_query and not has_gender_spec:
            tournament_detected = next((t for t in combined_tournaments if t in query_lower), 'unknown')
            return {
                'is_coverage_issue': True,
                'tournament': tournament_detected,
                'query': query,
                'severity': 'high' if tournament_detected in ['rome', 'basel', 'madrid'] else 'medium'
            }
        
        return {'is_coverage_issue': False}
    
    def run_session_ml_analysis(self):
        """Run ML analysis at the start of each session."""
        if 'ml_analysis_done' not in st.session_state:
            st.session_state.ml_analysis_done = True
            
            # Run comprehensive analysis silently in background
            try:
                report = self.analyzer.generate_insights_report()
                
                if 'error' not in report:
                    # Store analysis results in session state silently
                    st.session_state.ml_insights = report
                    
                    # Check for coverage issues and store silently
                    if 'query_analysis' in report and 'coverage_issues' in report['query_analysis']:
                        coverage = report['query_analysis']['coverage_issues']
                        if coverage.get('total_incomplete_queries', 0) > 0:
                            st.session_state.coverage_issues = coverage
                    
                    # Store performance insights silently
                    if 'performance_analysis' in report:
                        st.session_state.performance_insights = report['performance_analysis']
                        
            except Exception as e:
                # Log error silently without showing to user
                pass
    
    def get_coverage_insights(self) -> dict:
        """Get coverage insights from session state."""
        return getattr(st.session_state, 'coverage_issues', {})
    
    def get_performance_insights(self) -> dict:
        """Get performance insights from session state."""
        return getattr(st.session_state, 'performance_insights', {})
    
    def get_ml_insights(self) -> dict:
        """Get ML insights from session state."""
        return getattr(st.session_state, 'ml_insights', {})
    
    def has_coverage_issues(self) -> bool:
        """Check if there are coverage issues detected."""
        coverage = self.get_coverage_insights()
        return coverage.get('total_incomplete_queries', 0) > 0
    
    def get_coverage_summary(self) -> str:
        """Get a summary of coverage issues."""
        coverage = self.get_coverage_insights()
        if not coverage:
            return "No coverage issues detected."
        
        total_issues = coverage.get('total_incomplete_queries', 0)
        if total_issues == 0:
            return "No coverage issues detected."
        
        return f"Detected {total_issues} coverage issues in recent queries."
    
    def get_performance_summary(self) -> str:
        """Get a summary of performance insights."""
        performance = self.get_performance_insights()
        if not performance:
            return "No performance data available."
        
        avg_response_time = performance.get('average_response_time', 0)
        total_queries = performance.get('total_queries', 0)
        
        return f"Processed {total_queries} queries with average response time of {avg_response_time:.2f}s."
