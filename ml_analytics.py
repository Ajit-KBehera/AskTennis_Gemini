"""
ML Analytics module for AskTennis AI application.
Analyzes log files to provide insights, optimize performance, and improve user experience.
"""

import os
import re
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import streamlit as st


class TennisLogAnalyzer:
    """ML-powered analyzer for tennis application logs."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self.query_patterns = []
        self.performance_metrics = []
        self.error_patterns = []
        self.user_behavior = defaultdict(list)
        
    def load_log_files(self) -> List[Dict]:
        """Load and parse all log files."""
        log_data = []
        
        if not os.path.exists(self.logs_dir):
            st.warning(f"Logs directory '{self.logs_dir}' not found.")
            return log_data
            
        for filename in os.listdir(self.logs_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(self.logs_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        parsed_logs = self._parse_log_content(content, filename)
                        log_data.extend(parsed_logs)
                except Exception as e:
                    st.error(f"Error reading {filename}: {e}")
                    
        return log_data
    
    def _parse_log_content(self, content: str, filename: str) -> List[Dict]:
        """Parse log content and extract structured data."""
        logs = []
        lines = content.split('\n')
        
        current_query = None
        current_session = None
        db_query = None
        tool_query = None
        error = None
        
        for line in lines:
            if not line.strip():
                continue
                
            # Extract timestamp
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            timestamp = timestamp_match.group(1) if timestamp_match else None
            
            # Extract log level
            level_match = re.search(r'- (INFO|ERROR|WARNING|DEBUG) -', line)
            level = level_match.group(1) if level_match else 'INFO'
            
            # Extract session ID
            session_match = re.search(r'Session ID: ([a-f0-9]+)', line)
            if session_match:
                current_session = session_match.group(1)
            
            # Extract user queries
            if 'USER QUERY START' in line:
                current_query = {'type': 'user_query', 'session': current_session, 'timestamp': timestamp}
            elif 'Query:' in line and current_query:
                query_text = line.split('Query: ')[1] if 'Query: ' in line else ''
                current_query['query'] = query_text
                current_query['filename'] = filename
                logs.append(current_query.copy())
                current_query = None
            elif 'Query:' in line and not current_query:
                # Handle case where we find a query without the start marker
                query_text = line.split('Query: ')[1] if 'Query: ' in line else ''
                if query_text.strip():
                    logs.append({
                        'type': 'user_query',
                        'session': current_session,
                        'timestamp': timestamp,
                        'query': query_text,
                        'filename': filename
                    })
            
            # Extract database queries
            elif 'DATABASE QUERY START' in line:
                db_query = {'type': 'database_query', 'session': current_session, 'timestamp': timestamp}
            elif 'SQL Query:' in line and db_query:
                sql_text = line.split('SQL Query: ')[1] if 'SQL Query: ' in line else ''
                db_query['sql'] = sql_text
            elif 'Execution Time:' in line and db_query:
                time_match = re.search(r'Execution Time: ([\d.]+) seconds', line)
                if time_match:
                    db_query['execution_time'] = float(time_match.group(1))
            elif 'Results Count:' in line and db_query:
                count_match = re.search(r'Results Count: (\d+)', line)
                if count_match:
                    db_query['result_count'] = int(count_match.group(1))
            elif 'DATABASE QUERY END' in line and db_query:
                db_query['filename'] = filename
                logs.append(db_query.copy())
                db_query = None
            
            # Also extract from tool usage
            elif 'Tool: sql_db_query' in line:
                tool_query = {'type': 'database_query', 'session': current_session, 'timestamp': timestamp}
            elif 'Input:' in line and tool_query:
                input_text = line.split('Input: ')[1] if 'Input: ' in line else ''
                tool_query['input'] = input_text
            elif 'Execution Time:' in line and tool_query:
                time_match = re.search(r'Execution Time: ([\d.]+) seconds', line)
                if time_match:
                    tool_query['execution_time'] = float(time_match.group(1))
            elif 'TOOL USAGE END' in line and tool_query:
                tool_query['filename'] = filename
                logs.append(tool_query.copy())
                tool_query = None
            
            # Extract errors
            elif 'ERROR START' in line:
                error = {'type': 'error', 'session': current_session, 'timestamp': timestamp}
            elif 'Context:' in line and error:
                context = line.split('Context: ')[1] if 'Context: ' in line else ''
                error['context'] = context
            elif 'Error:' in line and error:
                error_text = line.split('Error: ')[1] if 'Error: ' in line else ''
                error['error_message'] = error_text
            elif 'ERROR END' in line and error:
                error['filename'] = filename
                logs.append(error.copy())
                error = None
        
        return logs
    
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
        
        return {
            'total_queries': total_queries,
            'unique_sessions': unique_sessions,
            'avg_query_length': round(avg_query_length, 2),
            'most_common_words': dict(word_frequencies.most_common(10)),
            'query_categories': categories,
            'category_percentages': {k: round(v/total_queries*100, 2) for k, v in categories.items()}
        }
    
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


def display_ml_analytics():
    """Display ML analytics in Streamlit."""
    st.subheader("🤖 ML Analytics Dashboard")
    
    analyzer = TennisLogAnalyzer()
    
    if st.button("🔍 Analyze Log Files"):
        with st.spinner("Analyzing log files..."):
            report = analyzer.generate_insights_report()
            
            if 'error' in report:
                st.error(report['error'])
                return
            
            # Display insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Log Entries", report['total_log_entries'])
                
                if 'query_analysis' in report and 'total_queries' in report['query_analysis']:
                    st.metric("Total User Queries", report['query_analysis']['total_queries'])
                    st.metric("Unique Sessions", report['query_analysis']['unique_sessions'])
            
            with col2:
                if 'performance_analysis' in report and 'avg_execution_time' in report['performance_analysis']:
                    st.metric("Avg Query Time", f"{report['performance_analysis']['avg_execution_time']}s")
                    st.metric("Total DB Queries", report['performance_analysis']['total_db_queries'])
            
            # Query patterns
            if 'query_analysis' in report:
                st.subheader("📊 Query Patterns")
                query_analysis = report['query_analysis']
                
                if 'query_categories' in query_analysis:
                    st.write("**Query Categories:**")
                    for category, count in query_analysis['query_categories'].items():
                        st.write(f"- {category.replace('_', ' ').title()}: {count}")
                
                if 'most_common_words' in query_analysis:
                    st.write("**Most Common Words:**")
                    for word, count in list(query_analysis['most_common_words'].items())[:5]:
                        st.write(f"- {word}: {count}")
            
            # Performance insights
            if 'performance_analysis' in report:
                st.subheader("⚡ Performance Insights")
                perf_analysis = report['performance_analysis']
                
                if 'performance_distribution' in perf_analysis:
                    dist = perf_analysis['performance_distribution']
                    st.write(f"**Query Performance:**")
                    st.write(f"- Fast queries (<1s): {dist.get('fast_queries', 0)}")
                    st.write(f"- Medium queries (1-5s): {dist.get('medium_queries', 0)}")
                    st.write(f"- Slow queries (>5s): {dist.get('slow_queries', 0)}")
                
                if 'performance_recommendations' in perf_analysis:
                    st.write("**Recommendations:**")
                    for rec in perf_analysis['performance_recommendations']:
                        st.write(f"- {rec}")
            
            # Error analysis
            if 'error_analysis' in report:
                st.subheader("🚨 Error Analysis")
                error_analysis = report['error_analysis']
                
                if 'total_errors' in error_analysis:
                    st.metric("Total Errors", error_analysis['total_errors'])
                
                if 'error_recommendations' in error_analysis:
                    st.write("**Error Prevention:**")
                    for rec in error_analysis['error_recommendations']:
                        st.write(f"- {rec}")


if __name__ == "__main__":
    # Test the analyzer
    analyzer = TennisLogAnalyzer()
    report = analyzer.generate_insights_report()
    print(json.dumps(report, indent=2))
