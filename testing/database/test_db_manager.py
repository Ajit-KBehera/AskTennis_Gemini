"""
Test database manager for automated testing framework.
Handles SQLite database operations for test results and sessions.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class TestDatabaseManager:
    """
    Manages test database operations for automated testing.
    Handles test sessions, results storage, and querying.
    """
    
    def __init__(self, db_path: str = "testing/test_results.db"):
        """
        Initialize the test database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.ensure_database_directory()
        self.initialize_database()
    
    def ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create test_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    start_time DATETIME,
                    end_time DATETIME,
                    total_tests INTEGER DEFAULT 0,
                    passed_tests INTEGER DEFAULT 0,
                    failed_tests INTEGER DEFAULT 0,
                    average_accuracy REAL DEFAULT 0.0,
                    average_execution_time REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'running',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create test_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    test_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    generated_sql TEXT,
                    ai_answer TEXT,
                    expected_answer TEXT,
                    accuracy_score REAL DEFAULT 0.0,
                    execution_time REAL DEFAULT 0.0,
                    test_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT CHECK(status IN ('passed', 'failed', 'error')) DEFAULT 'failed',
                    error_message TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    category TEXT,
                    difficulty TEXT,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (id)
                )
            """)
            
            # Create test_metrics table for aggregated statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_results_session_id ON test_results(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_results_test_id ON test_results(test_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_results_status ON test_results(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_results_category ON test_results(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_sessions_status ON test_sessions(status)")
            
            conn.commit()
    
    def create_test_session(self, session_name: str = None) -> int:
        """
        Create a new test session.
        
        Args:
            session_name: Name for the test session (auto-generated if None)
            
        Returns:
            Session ID of the created session
        """
        if session_name is None:
            session_name = f"Test Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_sessions (session_name, start_time, status)
                VALUES (?, ?, ?)
            """, (session_name, datetime.now(), 'running'))
            
            session_id = cursor.lastrowid
            conn.commit()
            return session_id
    
    def update_test_session(self, session_id: int, **kwargs):
        """
        Update test session with new data.
        
        Args:
            session_id: ID of the session to update
            **kwargs: Fields to update (end_time, total_tests, passed_tests, etc.)
        """
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [session_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE test_sessions 
                SET {set_clause}
                WHERE id = ?
            """, values)
            conn.commit()
    
    def store_test_result(self, session_id: int, test_result: Dict[str, Any]) -> int:
        """
        Store a single test result.
        
        Args:
            session_id: ID of the test session
            test_result: Dictionary containing test result data
            
        Returns:
            ID of the stored test result
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_results (
                    session_id, test_id, question, generated_sql,
                    ai_answer, expected_answer, accuracy_score, execution_time,
                    status, error_message, confidence_score, category, difficulty
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                test_result.get('test_id', 0),
                test_result.get('question', ''),
                test_result.get('generated_sql', ''),
                test_result.get('ai_answer', ''),
                test_result.get('expected_answer', ''),
                test_result.get('accuracy_score', 0.0),
                test_result.get('execution_time', 0.0),
                test_result.get('status', 'failed'),
                test_result.get('error_message', ''),
                test_result.get('confidence_score', 0.0),
                test_result.get('category', ''),
                test_result.get('difficulty', '')
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            return result_id
    
    def get_test_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get test session details.
        
        Args:
            session_id: ID of the test session
            
        Returns:
            Dictionary containing session details or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions WHERE id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_test_results(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get all test results for a session.
        
        Args:
            session_id: ID of the test session
            
        Returns:
            List of dictionaries containing test results
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_results WHERE session_id = ?
                ORDER BY test_timestamp
            """, (session_id,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_test_results_by_status(self, session_id: int, status: str) -> List[Dict[str, Any]]:
        """
        Get test results filtered by status.
        
        Args:
            session_id: ID of the test session
            status: Status to filter by ('passed', 'failed', 'error')
            
        Returns:
            List of test results with the specified status
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_results 
                WHERE session_id = ? AND status = ?
                ORDER BY test_timestamp
            """, (session_id, status))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_test_results_by_category(self, session_id: int, category: str) -> List[Dict[str, Any]]:
        """
        Get test results filtered by category.
        
        Args:
            session_id: ID of the test session
            category: Category to filter by
            
        Returns:
            List of test results for the specified category
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_results 
                WHERE session_id = ? AND category = ?
                ORDER BY test_timestamp
            """, (session_id, category))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def calculate_session_metrics(self, session_id: int) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics for a test session.
        
        Args:
            session_id: ID of the test session
            
        Returns:
            Dictionary containing calculated metrics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get basic counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tests,
                    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed_tests,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tests,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_tests,
                    AVG(accuracy_score) as average_accuracy,
                    AVG(execution_time) as average_execution_time
                FROM test_results 
                WHERE session_id = ?
            """, (session_id,))
            
            basic_metrics = cursor.fetchone()
            
            # Get category breakdown
            cursor.execute("""
                SELECT 
                    category,
                    COUNT(*) as total,
                    AVG(accuracy_score) as avg_accuracy,
                    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed
                FROM test_results 
                WHERE session_id = ?
                GROUP BY category
                ORDER BY total DESC
            """, (session_id,))
            
            category_breakdown = cursor.fetchall()
            
            # Get difficulty breakdown
            cursor.execute("""
                SELECT 
                    difficulty,
                    COUNT(*) as total,
                    AVG(accuracy_score) as avg_accuracy,
                    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed
                FROM test_results 
                WHERE session_id = ?
                GROUP BY difficulty
                ORDER BY total DESC
            """, (session_id,))
            
            difficulty_breakdown = cursor.fetchall()
            
            return {
                'basic_metrics': {
                    'total_tests': basic_metrics[0] or 0,
                    'passed_tests': basic_metrics[1] or 0,
                    'failed_tests': basic_metrics[2] or 0,
                    'error_tests': basic_metrics[3] or 0,
                    'average_accuracy': basic_metrics[4] or 0.0,
                    'average_execution_time': basic_metrics[5] or 0.0
                },
                'category_breakdown': [
                    {
                        'category': row[0],
                        'total': row[1],
                        'avg_accuracy': row[2] or 0.0,
                        'passed': row[3]
                    }
                    for row in category_breakdown
                ],
                'difficulty_breakdown': [
                    {
                        'difficulty': row[0],
                        'total': row[1],
                        'avg_accuracy': row[2] or 0.0,
                        'passed': row[3]
                    }
                    for row in difficulty_breakdown
                ]
            }
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all test sessions.
        
        Returns:
            List of all test sessions
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions 
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def delete_test_session(self, session_id: int) -> bool:
        """
        Delete a test session and all its results.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete test results first (foreign key constraint)
                cursor.execute("DELETE FROM test_results WHERE session_id = ?", (session_id,))
                
                # Delete test session
                cursor.execute("DELETE FROM test_sessions WHERE id = ?", (session_id,))
                
                conn.commit()
                return True
        except Exception:
            return False
    
    def export_session_data(self, session_id: int, format: str = 'json') -> str:
        """
        Export test session data in specified format.
        
        Args:
            session_id: ID of the session to export
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data as string
        """
        session_data = self.get_test_session(session_id)
        test_results = self.get_test_results(session_id)
        metrics = self.calculate_session_metrics(session_id)
        
        export_data = {
            'session': session_data,
            'results': test_results,
            'metrics': metrics
        }
        
        if format.lower() == 'json':
            return json.dumps(export_data, indent=2, default=str)
        elif format.lower() == 'csv':
            # Simple CSV export for results
            import csv
            import io
            
            output = io.StringIO()
            if test_results:
                writer = csv.DictWriter(output, fieldnames=test_results[0].keys())
                writer.writeheader()
                writer.writerows(test_results)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def close(self):
        """Close database connection (if needed)."""
        # SQLite connections are automatically closed when out of scope
        pass
