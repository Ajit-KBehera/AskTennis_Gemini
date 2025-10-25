#!/usr/bin/env python3
"""
Test script to verify the testing framework works correctly.
This is a meta-test to ensure our testing system is functional.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from testing.test_data.tennis_qa_dataset import TENNIS_QA_DATASET, get_test_categories
from testing.test_data.test_categories import TestCategory, ValidationMethod
from testing.result_analyzer import ResultAnalyzer
from testing.database.test_db_manager import TestDatabaseManager


def test_dataset_loading():
    """Test that the dataset loads correctly."""
    print("🧪 Testing dataset loading...")
    
    # Check dataset size
    assert len(TENNIS_QA_DATASET) == 100, f"Expected 100 test cases, got {len(TENNIS_QA_DATASET)}"
    print("✅ Dataset has 100 test cases")
    
    # Check dataset structure
    for i, test_case in enumerate(TENNIS_QA_DATASET[:5]):  # Check first 5
        required_fields = ['id', 'question', 'expected_answer', 'category', 'difficulty']
        for field in required_fields:
            assert field in test_case, f"Missing field '{field}' in test case {i+1}"
    print("✅ Dataset structure is correct")
    
    # Check categories
    categories = get_test_categories()
    assert len(categories) == 8, f"Expected 8 categories, got {len(categories)}"
    print("✅ Categories are properly defined")
    
    return True


def test_result_analyzer():
    """Test the result analyzer functionality."""
    print("🧪 Testing result analyzer...")
    
    analyzer = ResultAnalyzer()
    
    # Test exact match
    accuracy = analyzer.calculate_accuracy("Novak Djokovic", "Novak Djokovic", "tournament_winner")
    assert accuracy == 1.0, f"Expected 1.0 for exact match, got {accuracy}"
    print("✅ Exact match accuracy works")
    
    # Test partial match
    accuracy = analyzer.calculate_accuracy("Djokovic won", "Novak Djokovic", "tournament_winner")
    assert accuracy > 0.0, f"Expected > 0.0 for partial match, got {accuracy}"
    print("✅ Partial match accuracy works")
    
    # Test numerical accuracy
    accuracy = analyzer.calculate_accuracy("24", "24", "head_to_head")
    assert accuracy == 1.0, f"Expected 1.0 for numerical match, got {accuracy}"
    print("✅ Numerical accuracy works")
    
    return True


def test_database_operations():
    """Test database operations."""
    print("🧪 Testing database operations...")
    
    # Create test database manager
    db_manager = TestDatabaseManager("testing/test_framework_test.db")
    
    try:
        # Test session creation
        session_id = db_manager.create_test_session("Test Session")
        assert session_id > 0, f"Expected session ID > 0, got {session_id}"
        print("✅ Session creation works")
        
        # Test result storage
        test_result = {
            'test_id': 1,
            'question': 'Test question?',
            'generated_sql': 'SELECT * FROM test',
            'ai_answer': 'Test answer',
            'expected_answer': 'Expected answer',
            'accuracy_score': 0.8,
            'execution_time': 1.5,
            'status': 'passed',
            'category': 'test',
            'difficulty': 'easy'
        }
        
        result_id = db_manager.store_test_result(session_id, test_result)
        assert result_id > 0, f"Expected result ID > 0, got {result_id}"
        print("✅ Result storage works")
        
        # Test session retrieval
        session = db_manager.get_test_session(session_id)
        assert session is not None, "Expected session to be retrieved"
        assert session['session_name'] == "Test Session", "Session name mismatch"
        print("✅ Session retrieval works")
        
        # Test results retrieval
        results = db_manager.get_test_results(session_id)
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        print("✅ Results retrieval works")
        
        # Test metrics calculation
        metrics = db_manager.calculate_session_metrics(session_id)
        assert 'basic_metrics' in metrics, "Expected basic_metrics in session metrics"
        print("✅ Metrics calculation works")
        
    finally:
        # Cleanup
        db_manager.delete_test_session(session_id)
        db_manager.close()
    
    return True


def test_validation_methods():
    """Test validation methods."""
    print("🧪 Testing validation methods...")
    
    from testing.test_data.test_categories import get_validation_function
    
    # Test exact match validation
    exact_match_func = get_validation_function(ValidationMethod.EXACT_MATCH)
    accuracy = exact_match_func("Novak Djokovic", "Novak Djokovic")
    assert accuracy == 1.0, f"Expected 1.0 for exact match, got {accuracy}"
    print("✅ Exact match validation works")
    
    # Test numerical accuracy validation
    numerical_func = get_validation_function(ValidationMethod.NUMERICAL_ACCURACY)
    accuracy = numerical_func("24", "24")
    assert accuracy == 1.0, f"Expected 1.0 for numerical match, got {accuracy}"
    print("✅ Numerical accuracy validation works")
    
    return True


def main():
    """Run all framework tests."""
    print("🧪 AskTennis AI - Testing Framework Verification")
    print("=" * 60)
    
    tests = [
        ("Dataset Loading", test_dataset_loading),
        ("Result Analyzer", test_result_analyzer),
        ("Database Operations", test_database_operations),
        ("Validation Methods", test_validation_methods)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running {test_name}...")
            test_func()
            print(f"✅ {test_name} passed")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All framework tests passed! The testing system is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the framework setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
