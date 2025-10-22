"""
Log parsing utilities for AskTennis AI application.
Handles log file loading, parsing, and data extraction.
Extracted from ml_analytics.py for better modularity.
"""

import os
import re
from typing import Dict, List
import streamlit as st


class LogParser:
    """
    Centralized log parsing class for tennis application logs.
    Handles file loading, content parsing, and data extraction.
    """
    
    def __init__(self, logs_dir: str = "logs"):
        """
        Initialize the log parser.
        
        Args:
            logs_dir: Directory containing log files
        """
        self.logs_dir = logs_dir
    
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
    
    def get_log_statistics(self, log_data: List[Dict]) -> Dict[str, int]:
        """Get basic statistics about the log data."""
        if not log_data:
            return {"total_entries": 0}
        
        stats = {
            "total_entries": len(log_data),
            "user_queries": len([log for log in log_data if log.get('type') == 'user_query']),
            "database_queries": len([log for log in log_data if log.get('type') == 'database_query']),
            "errors": len([log for log in log_data if log.get('type') == 'error']),
            "unique_sessions": len(set(log.get('session') for log in log_data if log.get('session')))
        }
        
        return stats
