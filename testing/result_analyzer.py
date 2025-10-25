"""
Result analyzer for automated testing framework.
Handles basic result analysis and reporting.
"""

from typing import Dict, Any, List
from datetime import datetime


class ResultAnalyzer:
    """
    Analyzes test results and provides basic metrics.
    Simplified to focus on execution metrics without accuracy calculation.
    """
    
    def __init__(self):
        """Initialize the result analyzer."""
        pass
    
    def analyze_test_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze test results and generate basic metrics.
        
        Args:
            results: List of test result dictionaries
            
        Returns:
            Dictionary containing analysis results
        """
        if not results:
            return {
                'basic_metrics': {
                    'total_tests': 0,
                    'completed_tests': 0,
                    'error_tests': 0
                },
                'performance_metrics': {
                    'average_execution_time': 0.0,
                    'total_execution_time': 0.0
                },
                'category_breakdown': {},
                'difficulty_breakdown': {}
            }
        
        # Basic metrics
        total_tests = len(results)
        completed_tests = sum(1 for r in results if not r.get('error_message'))
        error_tests = sum(1 for r in results if r.get('error_message'))
        
        # Performance metrics
        execution_times = [r.get('execution_time', 0.0) for r in results]
        avg_execution_time = sum(execution_times) / total_tests if total_tests > 0 else 0.0
        total_execution_time = sum(execution_times)
        
        # Category breakdown
        categories = {}
        for result in results:
            category = result.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        # Difficulty breakdown
        difficulties = {}
        for result in results:
            difficulty = result.get('difficulty', 'unknown')
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        return {
            'basic_metrics': {
                'total_tests': total_tests,
                'completed_tests': completed_tests,
                'error_tests': error_tests
            },
            'performance_metrics': {
                'average_execution_time': avg_execution_time,
                'total_execution_time': total_execution_time
            },
            'category_breakdown': categories,
            'difficulty_breakdown': difficulties
        }
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a text summary report of test results.
        
        Args:
            results: List of test result dictionaries
            
        Returns:
            String summary report
        """
        analysis = self.analyze_test_results(results)
        
        report = f"""
Test Execution Summary
=====================
Total Tests: {analysis['basic_metrics']['total_tests']}
Completed: {analysis['basic_metrics']['completed_tests']}
Errors: {analysis['basic_metrics']['error_tests']}

Performance
===========
Average Execution Time: {analysis['performance_metrics']['average_execution_time']:.2f}s
Total Execution Time: {analysis['performance_metrics']['total_execution_time']:.2f}s

Category Breakdown
=================
"""
        
        for category, count in analysis['category_breakdown'].items():
            report += f"{category}: {count}\n"
        
        report += "\nDifficulty Breakdown\n===================\n"
        for difficulty, count in analysis['difficulty_breakdown'].items():
            report += f"{difficulty}: {count}\n"
        
        return report.strip()