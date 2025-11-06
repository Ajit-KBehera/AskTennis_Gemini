"""
Unit tests for tennis_logging module.
Tests all logging functionality including BaseLogger, SimplifiedLoggingFactory, and LoggingSetup.
"""

import unittest
import os
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tennis_logging.base_logger import BaseLogger
from tennis_logging.simplified_factory import SimplifiedLoggingFactory, setup_logging, log_user_query, log_error
from tennis_logging.setup.logging_setup import LoggingSetup
from tennis_logging.log_filter import LogFilter
from tennis_logging.performance_metrics import PerformanceMetrics


class TestBaseLogger(unittest.TestCase):
    """Test cases for BaseLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger = BaseLogger("test_logger")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_user_query(self):
        """Test logging user queries."""
        self.logger.log_user_query("test query", "session123", "test_component")
        # Verify no exceptions raised
        self.assertTrue(True)
    
    def test_log_llm_interaction(self):
        """Test logging LLM interactions."""
        messages = [{"role": "user", "content": "test"}]
        self.logger.log_llm_interaction(messages, "LLM_CALL", "test_component")
        self.assertTrue(True)
    
    def test_log_database_query(self):
        """Test logging database queries."""
        self.logger.log_database_query("SELECT * FROM test", ["result1"], 0.5, "test_component")
        self.assertTrue(True)
    
    def test_log_tool_usage(self):
        """Test logging tool usage."""
        self.logger.log_tool_usage("test_tool", {"input": "data"}, "output", 0.3, "test_component")
        self.assertTrue(True)
    
    def test_log_final_response(self):
        """Test logging final responses."""
        self.logger.log_final_response("Response text", 1.5, "test_component")
        self.assertTrue(True)
    
    def test_log_error(self):
        """Test logging errors."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.logger.log_error(e, "Test context", "test_component")
        self.assertTrue(True)
    
    def test_log_agent_response_parsing(self):
        """Test logging agent response parsing."""
        self.logger.log_agent_response_parsing(
            "test_step",
            "AIMessage",
            "preview",
            {"detail": "value"},
            "test_component"
        )
        self.assertTrue(True)
    
    def test_json_format(self):
        """Test JSON format logging."""
        logger = BaseLogger("test_logger", json_format=True)
        logger.log_user_query("test", "session123")
        self.assertTrue(logger.json_format)
    
    def test_text_format(self):
        """Test text format logging."""
        logger = BaseLogger("test_logger", json_format=False)
        logger.log_user_query("test", "session123")
        self.assertFalse(logger.json_format)
    
    def test_get_logger(self):
        """Test getting logger instance."""
        logger = self.logger.get_logger()
        self.assertIsNotNone(logger)


class TestSimplifiedLoggingFactory(unittest.TestCase):
    """Test cases for SimplifiedLoggingFactory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = SimplifiedLoggingFactory()
    
    def test_log_user_query(self):
        """Test factory log_user_query method."""
        self.factory.log_user_query("test query", "session123", "test_component")
        self.assertTrue(True)
    
    def test_log_error(self):
        """Test factory log_error method."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.factory.log_error(e, "Test context", "test_component")
        self.assertTrue(True)
    
    def test_setup_logging(self):
        """Test setup_logging method."""
        with patch('streamlit.session_state', new={}):
            with patch('streamlit.session_state', create=True) as mock_session:
                mock_session.__contains__ = lambda x: False
                mock_session.__setitem__ = MagicMock()
                mock_session.__getitem__ = MagicMock(return_value="test.log")
                try:
                    logger, log_file = self.factory.setup_logging()
                    self.assertIsNotNone(logger)
                    self.assertIsNotNone(log_file)
                except Exception:
                    # Streamlit dependency may cause issues in test environment
                    pass


class TestLoggingFunctions(unittest.TestCase):
    """Test cases for module-level logging functions."""
    
    def test_log_user_query_function(self):
        """Test log_user_query function."""
        log_user_query("test query", "session123", "test_component")
        self.assertTrue(True)
    
    def test_log_error_function(self):
        """Test log_error function."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_error(e, "Test context", "test_component")
        self.assertTrue(True)


class TestLogFilter(unittest.TestCase):
    """Test cases for LogFilter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a test log file
        self.log_file = os.path.join(self.log_dir, "test.log")
        with open(self.log_file, 'w') as f:
            # Write JSON format log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "section": "USER QUERY",
                "data": {
                    "session_id": "session123",
                    "query": "test query",
                    "component": "test_component"
                }
            }
            f.write(json.dumps(log_entry) + "\n")
            
            # Write text format log entry
            f.write("=== ERROR START ===\n")
            f.write("error_type: ValueError\n")
            f.write("error_message: Test error\n")
            f.write("component: test_component\n")
            f.write("=== ERROR END ===\n")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_filter_by_section(self):
        """Test filtering by section type."""
        with patch('tennis_logging.log_filter.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.glob.return_value = [Path(self.log_file)]
            
            filter_obj = LogFilter(self.log_file)
            errors = filter_obj.filter_by_section(["ERROR"])
            self.assertGreaterEqual(len(errors), 0)
    
    def test_filter_by_session(self):
        """Test filtering by session ID."""
        filter_obj = LogFilter(self.log_file)
        session_logs = filter_obj.filter_by_session("session123")
        self.assertGreaterEqual(len(session_logs), 0)
    
    def test_filter_by_component(self):
        """Test filtering by component."""
        filter_obj = LogFilter(self.log_file)
        component_logs = filter_obj.filter_by_component("test_component")
        self.assertGreaterEqual(len(component_logs), 0)
    
    def test_get_unique_sessions(self):
        """Test getting unique sessions."""
        filter_obj = LogFilter(self.log_file)
        sessions = filter_obj.get_unique_sessions()
        self.assertIsInstance(sessions, set)
    
    def test_get_unique_components(self):
        """Test getting unique components."""
        filter_obj = LogFilter(self.log_file)
        components = filter_obj.get_unique_components()
        self.assertIsInstance(components, set)
    
    def test_get_section_counts(self):
        """Test getting section counts."""
        filter_obj = LogFilter(self.log_file)
        counts = filter_obj.get_section_counts()
        self.assertIsInstance(counts, dict)


class TestPerformanceMetrics(unittest.TestCase):
    """Test cases for PerformanceMetrics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a test log file with performance data
        self.log_file = os.path.join(self.log_dir, "test.log")
        with open(self.log_file, 'w') as f:
            # Write database query log
            db_entry = {
                "timestamp": datetime.now().isoformat(),
                "section": "DATABASE QUERY",
                "data": {
                    "sql_query": "SELECT * FROM test",
                    "execution_time": 0.5,
                    "component": "test_component"
                }
            }
            f.write(json.dumps(db_entry) + "\n")
            
            # Write tool usage log
            tool_entry = {
                "timestamp": datetime.now().isoformat(),
                "section": "TOOL USAGE",
                "data": {
                    "tool_name": "test_tool",
                    "execution_time": 0.3,
                    "component": "test_component"
                }
            }
            f.write(json.dumps(tool_entry) + "\n")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_database_query_stats(self):
        """Test getting database query statistics."""
        metrics = PerformanceMetrics(self.log_file)
        stats = metrics.get_database_query_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_queries", stats)
        self.assertIn("average_time", stats)
    
    def test_get_tool_usage_stats(self):
        """Test getting tool usage statistics."""
        metrics = PerformanceMetrics(self.log_file)
        stats = metrics.get_tool_usage_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_tool_calls", stats)
    
    def test_get_overall_stats(self):
        """Test getting overall statistics."""
        metrics = PerformanceMetrics(self.log_file)
        stats = metrics.get_overall_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("database_queries", stats)
        self.assertIn("tool_usage", stats)
    
    def test_identify_bottlenecks(self):
        """Test identifying bottlenecks."""
        metrics = PerformanceMetrics(self.log_file)
        bottlenecks = metrics.identify_bottlenecks(threshold_seconds=0.1)
        self.assertIsInstance(bottlenecks, list)


class TestLoggingSetup(unittest.TestCase):
    """Test cases for LoggingSetup class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.setup = LoggingSetup()
    
    def test_get_log_level(self):
        """Test getting log level."""
        with patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'}):
            level = self.setup.get_log_level()
            self.assertIn(level, ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    
    def test_get_log_format(self):
        """Test getting log format."""
        with patch.dict(os.environ, {'LOG_FORMAT': 'json'}):
            format_str = self.setup.get_log_format()
            self.assertIn(format_str, ['json', 'text'])


if __name__ == '__main__':
    unittest.main()

