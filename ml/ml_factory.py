"""
Main ML analytics factory for AskTennis AI application.
Orchestrates all ML analytics components to provide comprehensive insights.
Extracted from ml_analytics.py for better modularity.
"""

from datetime import datetime
from typing import Dict, List, Any
from .parsing.log_parser import LogParser
from .analysis.query_analyzer import QueryAnalyzer
from .analysis.performance_analyzer import PerformanceAnalyzer
from .analysis.error_analyzer import ErrorAnalyzer
from .terminology.terminology_analyzer import TerminologyAnalyzer
from .display.ml_dashboard import MLDashboard


class TennisLogAnalyzer:
    """
    Main ML analytics factory class for tennis application.
    Orchestrates all ML analytics components to provide comprehensive insights.
    """
    
    def __init__(self, logs_dir: str = "logs"):
        """
        Initialize the ML analytics factory.
        
        Args:
            logs_dir: Directory containing log files
        """
        # Initialize all components
        self.log_parser = LogParser(logs_dir)
        self.query_analyzer = QueryAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.error_analyzer = ErrorAnalyzer()
        self.terminology_analyzer = TerminologyAnalyzer()
        self.dashboard = MLDashboard()
    
    def load_log_files(self) -> List[Dict]:
        """Load and parse all log files."""
        return self.log_parser.load_log_files()
    
    def analyze_query_patterns(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze user query patterns using ML techniques."""
        return self.query_analyzer.analyze_query_patterns(log_data)
    
    def analyze_performance(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze performance metrics from logs."""
        return self.performance_analyzer.analyze_performance(log_data)
    
    def analyze_errors(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns and provide insights."""
        return self.error_analyzer.analyze_errors(log_data)
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        log_data = self.load_log_files()
        
        if not log_data:
            return {"error": "No log data found"}
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_log_entries': len(log_data),
            'query_analysis': self.analyze_query_patterns(log_data),
            'performance_analysis': self.analyze_performance(log_data),
            'error_analysis': self.analyze_errors(log_data)
        }
        
        return report
    
    def get_health_score(self) -> Dict[str, int]:
        """Get overall system health scores."""
        log_data = self.load_log_files()
        
        if not log_data:
            return {"overall": 0, "performance": 0, "errors": 0, "terminology": 0}
        
        # Get individual health scores
        performance_data = self.analyze_performance(log_data)
        error_data = self.analyze_errors(log_data)
        query_data = self.analyze_query_patterns(log_data)
        
        performance_score = self.performance_analyzer.get_performance_health_score(performance_data)
        error_score = self.error_analyzer.get_error_health_score(error_data)
        
        # Calculate terminology score from query analysis
        terminology_score = 0
        if 'tennis_terminology' in query_data:
            terminology_score = self.terminology_analyzer.get_terminology_health_score(
                query_data['tennis_terminology']
            )
        
        # Calculate overall score
        overall_score = (performance_score + error_score + terminology_score) // 3
        
        return {
            "overall": overall_score,
            "performance": performance_score,
            "errors": error_score,
            "terminology": terminology_score
        }
    
    def get_system_summary(self) -> str:
        """Get a comprehensive system summary."""
        log_data = self.load_log_files()
        
        if not log_data:
            return "No log data available for analysis"
        
        # Get basic statistics
        stats = self.log_parser.get_log_statistics(log_data)
        
        # Get health scores
        health_scores = self.get_health_score()
        
        summary = f"System Analysis Summary:\n"
        summary += f"- Total log entries: {stats['total_entries']}\n"
        summary += f"- User queries: {stats['user_queries']}\n"
        summary += f"- Database queries: {stats['database_queries']}\n"
        summary += f"- Errors: {stats['errors']}\n"
        summary += f"- Unique sessions: {stats['unique_sessions']}\n"
        summary += f"- Overall health score: {health_scores['overall']}/100\n"
        summary += f"- Performance score: {health_scores['performance']}/100\n"
        summary += f"- Error score: {health_scores['errors']}/100\n"
        summary += f"- Terminology score: {health_scores['terminology']}/100"
        
        return summary


# Main function for backward compatibility
def display_ml_analytics():
    """
    Display ML analytics in Streamlit.
    Maintains backward compatibility with the original ml_analytics.py interface.
    """
    analyzer = TennisLogAnalyzer()
    dashboard = MLDashboard()
    dashboard.display_ml_analytics(analyzer)
