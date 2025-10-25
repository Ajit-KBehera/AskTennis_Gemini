"""
Main test runner for automated testing framework.
Orchestrates test execution with interval control and comprehensive reporting.
"""

import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

# Add the parent directory to the path to import from the main project
sys.path.append(str(Path(__file__).parent.parent))

from agent.agent_factory import setup_langgraph_agent
from .test_executor import TestExecutor
from .result_analyzer import ResultAnalyzer
from .database.test_db_manager import TestDatabaseManager
from .test_data.tennis_qa_dataset import TENNIS_QA_DATASET, get_test_categories


class TennisTestRunner:
    """
    Main test runner for automated tennis AI testing.
    Handles test execution, interval control, and result management.
    """
    
    def __init__(self, db_path: str = "testing/test_results.db"):
        """
        Initialize the test runner.
        
        Args:
            db_path: Path to the test database
        """
        self.db_manager = TestDatabaseManager(db_path)
        self.result_analyzer = ResultAnalyzer()
        self.agent_graph = None
        self.test_executor = None
        self.current_session_id = None
    
    def initialize_agent(self):
        """Initialize the LangGraph agent for testing."""
        try:
            print("Initializing LangGraph agent...")
            self.agent_graph = setup_langgraph_agent()
            self.test_executor = TestExecutor(self.agent_graph)
            print("✅ Agent initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    def run_automated_tests(self, 
                          interval_seconds: int = 90,
                          test_subset: Optional[List[int]] = None,
                          progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Run automated tests with specified interval.
        
        Args:
            interval_seconds: Seconds to wait between tests (minimum 90 seconds)
            test_subset: Optional list of test IDs to run (if None, runs all tests)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing test execution results
        """
        # Ensure minimum interval of 90 seconds
        if interval_seconds < 90:
            print(f"⚠️  Warning: Interval {interval_seconds}s is less than minimum 90s. Setting to 90s.")
            interval_seconds = 90
        if not self.agent_graph:
            if not self.initialize_agent():
                return {"error": "Failed to initialize agent"}
        
        # Create test session
        session_name = f"Automated Test Run {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.current_session_id = self.db_manager.create_test_session(session_name)
        
        print(f"🚀 Starting automated test run (Session ID: {self.current_session_id})")
        print(f"⏱️  Interval between tests: {interval_seconds} seconds")
        
        # Select tests to run
        if test_subset:
            test_cases = [tc for tc in TENNIS_QA_DATASET if tc['id'] in test_subset]
            print(f"📋 Running {len(test_cases)} selected tests")
        else:
            test_cases = TENNIS_QA_DATASET
            print(f"📋 Running all {len(test_cases)} tests")
        
        # Execute tests
        results = []
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"\n🔄 Test {i+1}/{total_tests}: {test_case['question'][:50]}...")
                
                # Execute test
                result = self.test_executor.execute_single_test(test_case)
                results.append(result)
                
                # Store result in database
                self.db_manager.store_test_result(self.current_session_id, result)
                
                # Print result summary
                status_emoji = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⚠️"
                print(f"   {status_emoji} Status: {result['status']} | Accuracy: {result['accuracy_score']:.2f} | Time: {result['execution_time']:.2f}s")
                
                # Progress callback
                if progress_callback:
                    progress_callback(i + 1, total_tests, result)
                
                # Wait interval (except for last test)
                if i < total_tests - 1:
                    print(f"⏳ Waiting {interval_seconds} seconds...")
                    time.sleep(interval_seconds)
                
            except Exception as e:
                print(f"❌ Error in test {i+1}: {e}")
                category = test_case.get('category', '')
                category_str = category.value if hasattr(category, 'value') else str(category)
                
                error_result = {
                    'test_id': test_case.get('id', 0),
                    'question': test_case.get('question', ''),
                    'ai_response': '',
                    'generated_sql': '',
                    'ai_answer': '',
                    'expected_answer': test_case.get('expected_answer', ''),
                    'accuracy_score': 0.0,
                    'execution_time': 0.0,
                    'status': 'error',
                    'error_message': str(e),
                    'confidence_score': 0.0,
                    'category': category_str,
                    'difficulty': test_case.get('difficulty', '')
                }
                results.append(error_result)
                self.db_manager.store_test_result(self.current_session_id, error_result)
        
        # Update session with final metrics
        self._update_session_metrics(results)
        
        # Generate final report
        final_report = self._generate_final_report(results)
        
        print(f"\n🎉 Test run completed!")
        print(f"📊 Results: {final_report['basic_metrics']['passed_tests']}/{final_report['basic_metrics']['total_tests']} passed")
        print(f"📈 Average accuracy: {final_report['accuracy_metrics']['average_accuracy']:.2%}")
        print(f"⏱️  Average execution time: {final_report['performance_metrics']['average_execution_time']:.2f}s")
        
        return {
            'session_id': self.current_session_id,
            'results': results,
            'report': final_report,
            'success': True
        }
    
    def run_quick_test(self, num_tests: int = 10) -> Dict[str, Any]:
        """
        Run a quick test with a subset of tests.
        
        Args:
            num_tests: Number of tests to run
            
        Returns:
            Dictionary containing test execution results
        """
        print(f"🏃‍♂️ Running quick test with {num_tests} tests...")
        
        # Select random subset of tests
        import random
        test_subset = random.sample([tc['id'] for tc in TENNIS_QA_DATASET], min(num_tests, len(TENNIS_QA_DATASET)))
        
        return self.run_automated_tests(
            interval_seconds=90,  # Minimum 90 seconds between tests
            test_subset=test_subset
        )
    
    def run_category_test(self, category: str, interval_seconds: int = 90) -> Dict[str, Any]:
        """
        Run tests for a specific category.
        
        Args:
            category: Test category to run
            interval_seconds: Seconds to wait between tests (minimum 90 seconds)
            
        Returns:
            Dictionary containing test execution results
        """
        print(f"🎯 Running tests for category: {category}")
        
        # Filter tests by category
        category_tests = [tc for tc in TENNIS_QA_DATASET if tc['category'].value == category]
        
        if not category_tests:
            return {"error": f"No tests found for category: {category}"}
        
        test_subset = [tc['id'] for tc in category_tests]
        return self.run_automated_tests(
            interval_seconds=interval_seconds,
            test_subset=test_subset
        )
    
    def _update_session_metrics(self, results: List[Dict[str, Any]]):
        """Update session with final metrics."""
        if not self.current_session_id:
            return
        
        # Calculate metrics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('status') == 'passed')
        failed_tests = sum(1 for r in results if r.get('status') == 'failed')
        error_tests = sum(1 for r in results if r.get('status') == 'error')
        
        avg_accuracy = sum(r.get('accuracy_score', 0.0) for r in results) / total_tests if total_tests > 0 else 0.0
        avg_execution_time = sum(r.get('execution_time', 0.0) for r in results) / total_tests if total_tests > 0 else 0.0
        
        # Update session
        self.db_manager.update_test_session(
            self.current_session_id,
            end_time=datetime.now(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            average_accuracy=avg_accuracy,
            average_execution_time=avg_execution_time,
            status='completed'
        )
    
    def _generate_final_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        return self.result_analyzer.analyze_test_results(results)
    
    def get_test_categories(self) -> Dict[str, int]:
        """Get available test categories and their counts."""
        return get_test_categories()
    
    def get_session_results(self, session_id: int) -> Dict[str, Any]:
        """Get results for a specific session."""
        session = self.db_manager.get_test_session(session_id)
        results = self.db_manager.get_test_results(session_id)
        metrics = self.db_manager.calculate_session_metrics(session_id)
        
        return {
            'session': session,
            'results': results,
            'metrics': metrics
        }
    
    def export_session_data(self, session_id: int, format: str = 'json') -> str:
        """Export session data in specified format."""
        return self.db_manager.export_session_data(session_id, format)
    
    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """Get list of all test sessions."""
        return self.db_manager.get_all_sessions()
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a test session and its results."""
        return self.db_manager.delete_test_session(session_id)
    
    def run_continuous_testing(self, 
                             interval_seconds: int = 90,
                             max_tests: int = 100,
                             progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Run continuous testing with specified parameters.
        
        Args:
            interval_seconds: Seconds to wait between tests (minimum 90 seconds)
            max_tests: Maximum number of tests to run
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing test execution results
        """
        print(f"🔄 Starting continuous testing (max {max_tests} tests, {interval_seconds}s interval)")
        
        # Select tests to run
        test_cases = TENNIS_QA_DATASET[:max_tests] if max_tests < len(TENNIS_QA_DATASET) else TENNIS_QA_DATASET
        
        return self.run_automated_tests(
            interval_seconds=interval_seconds,
            test_subset=[tc['id'] for tc in test_cases],
            progress_callback=progress_callback
        )
    
    def close(self):
        """Close database connections and cleanup."""
        if self.db_manager:
            self.db_manager.close()
