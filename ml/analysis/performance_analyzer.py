"""
Performance analysis utilities for AskTennis AI application.
Handles database performance metrics and optimization recommendations.
Extracted from ml_analytics.py for better modularity.
"""

import numpy as np
from collections import Counter
from typing import Dict, List, Any


class PerformanceAnalyzer:
    """
    Centralized performance analysis class for tennis application.
    Handles database performance metrics and optimization recommendations.
    """
    
    def __init__(self):
        """Initialize the performance analyzer."""
        pass
    
    def analyze_performance(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze performance metrics from logs."""
        db_queries = [log for log in log_data if log.get('type') == 'database_query']
        
        if not db_queries:
            return {"message": "No database queries found in logs"}
        
        # Execution time analysis
        execution_times = [log.get('execution_time', 0) for log in db_queries if log.get('execution_time')]
        
        if execution_times:
            avg_execution_time = np.mean(execution_times)
            max_execution_time = np.max(execution_times)
            min_execution_time = np.min(execution_times)
            
            # Performance categories
            fast_queries = len([t for t in execution_times if t < 1.0])
            medium_queries = len([t for t in execution_times if 1.0 <= t < 5.0])
            slow_queries = len([t for t in execution_times if t >= 5.0])
        else:
            avg_execution_time = max_execution_time = min_execution_time = 0
            fast_queries = medium_queries = slow_queries = 0
        
        # Result count analysis
        result_counts = [log.get('result_count', 0) for log in db_queries if log.get('result_count')]
        avg_results = np.mean(result_counts) if result_counts else 0
        
        # SQL pattern analysis
        sql_queries = [log.get('sql', '') for log in db_queries]
        common_operations = Counter()
        for sql in sql_queries:
            if 'SELECT' in sql.upper():
                common_operations['SELECT'] += 1
            if 'WHERE' in sql.upper():
                common_operations['WHERE'] += 1
            if 'JOIN' in sql.upper():
                common_operations['JOIN'] += 1
            if 'GROUP BY' in sql.upper():
                common_operations['GROUP BY'] += 1
            if 'ORDER BY' in sql.upper():
                common_operations['ORDER BY'] += 1
        
        return {
            'total_db_queries': len(db_queries),
            'avg_execution_time': round(avg_execution_time, 3),
            'max_execution_time': round(max_execution_time, 3),
            'min_execution_time': round(min_execution_time, 3),
            'avg_results_per_query': round(avg_results, 2),
            'performance_distribution': {
                'fast_queries': fast_queries,
                'medium_queries': medium_queries,
                'slow_queries': slow_queries
            },
            'common_sql_operations': dict(common_operations),
            'performance_recommendations': self._generate_performance_recommendations(
                avg_execution_time, slow_queries, common_operations
            )
        }
    
    def _generate_performance_recommendations(self, avg_time: float, slow_queries: int, operations: Dict) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        if avg_time > 2.0:
            recommendations.append("Consider adding database indexes for frequently queried columns")
        
        if slow_queries > 0:
            recommendations.append("Investigate slow queries - consider query optimization")
        
        if operations.get('JOIN', 0) > 5:
            recommendations.append("Multiple JOINs detected - consider denormalization or view optimization")
        
        if operations.get('GROUP BY', 0) > 3:
            recommendations.append("Frequent GROUP BY operations - consider pre-computed aggregations")
        
        return recommendations
    
    def get_performance_summary(self, performance_data: Dict[str, Any]) -> str:
        """Get a summary of performance metrics."""
        if 'message' in performance_data:
            return performance_data['message']
        
        avg_time = performance_data.get('avg_execution_time', 0)
        total_queries = performance_data.get('total_db_queries', 0)
        slow_queries = performance_data.get('performance_distribution', {}).get('slow_queries', 0)
        
        summary = f"Processed {total_queries} database queries with average execution time of {avg_time:.2f}s"
        
        if slow_queries > 0:
            summary += f" ({slow_queries} slow queries detected)"
        
        return summary
    
    def get_performance_health_score(self, performance_data: Dict[str, Any]) -> int:
        """Calculate a performance health score (0-100)."""
        if 'message' in performance_data:
            return 0
        
        score = 100
        
        # Deduct points for slow queries
        slow_queries = performance_data.get('performance_distribution', {}).get('slow_queries', 0)
        total_queries = performance_data.get('total_db_queries', 1)
        slow_percentage = (slow_queries / total_queries) * 100
        
        if slow_percentage > 20:
            score -= 30
        elif slow_percentage > 10:
            score -= 20
        elif slow_percentage > 5:
            score -= 10
        
        # Deduct points for high average execution time
        avg_time = performance_data.get('avg_execution_time', 0)
        if avg_time > 5.0:
            score -= 25
        elif avg_time > 3.0:
            score -= 15
        elif avg_time > 2.0:
            score -= 10
        
        return max(0, score)
