#!/usr/bin/env python3
"""
Demo script for the automated testing framework.
Shows how to use the testing system with examples.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from testing.test_runner import TennisTestRunner
from testing.test_data.tennis_qa_dataset import TENNIS_QA_DATASET, get_test_categories


def demo_quick_test():
    """Demonstrate a quick test run."""
    print("🧪 Demo: Quick Test Run")
    print("=" * 50)
    
    runner = TennisTestRunner()
    
    try:
        # Run a quick test with 5 tests
        print("Running 5 test cases...")
        results = runner.run_quick_test(num_tests=5)
        
        if results.get('success'):
            print("\n✅ Demo test completed successfully!")
            
            # Show some results
            report = results['report']
            basic_metrics = report.get('basic_metrics', {})
            
            print(f"\n📊 Results:")
            print(f"  • Total tests: {basic_metrics.get('total_tests', 0)}")
            print(f"  • Passed: {basic_metrics.get('passed_tests', 0)}")
            print(f"  • Pass rate: {basic_metrics.get('pass_rate', 0):.1%}")
            
            # Show individual results
            print(f"\n📋 Individual Results:")
            for i, result in enumerate(results['results'][:3]):  # Show first 3
                status = "✅" if result['status'] == 'passed' else "❌"
                print(f"  {i+1}. {status} {result['question'][:40]}...")
                print(f"     Accuracy: {result['accuracy_score']:.2f}")
        else:
            print(f"❌ Demo test failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in demo: {e}")
    finally:
        runner.close()


def demo_category_test():
    """Demonstrate category-specific testing."""
    print("\n🎯 Demo: Category Test")
    print("=" * 50)
    
    runner = TennisTestRunner()
    
    try:
        # Show available categories
        categories = get_test_categories()
        print("Available categories:")
        for category, count in categories.items():
            print(f"  • {category}: {count} tests")
        
        # Run tournament winner tests
        print(f"\nRunning tournament winner tests...")
        results = runner.run_category_test('tournament_winner', interval_seconds=1)
        
        if results.get('success'):
            print("✅ Category test completed!")
            
            report = results['report']
            basic_metrics = report.get('basic_metrics', {})
            
            print(f"\n📊 Tournament Winner Results:")
            print(f"  • Tests run: {basic_metrics.get('total_tests', 0)}")
            print(f"  • Passed: {basic_metrics.get('passed_tests', 0)}")
            print(f"  • Pass rate: {basic_metrics.get('pass_rate', 0):.1%}")
        else:
            print(f"❌ Category test failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in category demo: {e}")
    finally:
        runner.close()


def demo_test_data():
    """Demonstrate test data structure."""
    print("\n📋 Demo: Test Data Structure")
    print("=" * 50)
    
    # Show sample test cases
    print("Sample test cases:")
    for i, test_case in enumerate(TENNIS_QA_DATASET[:3]):
        print(f"\n{i+1}. {test_case['question']}")
        print(f"   Expected: {test_case['expected_answer']}")
        print(f"   Category: {test_case['category'].value}")
        print(f"   Difficulty: {test_case['difficulty']}")
    
    # Show category breakdown
    categories = get_test_categories()
    print(f"\n📊 Test Categories:")
    for category, count in categories.items():
        print(f"  • {category}: {count} tests")


def demo_database_operations():
    """Demonstrate database operations."""
    print("\n💾 Demo: Database Operations")
    print("=" * 50)
    
    runner = TennisTestRunner()
    
    try:
        # List all sessions
        sessions = runner.list_all_sessions()
        print(f"Found {len(sessions)} test sessions")
        
        if sessions:
            print("\nRecent sessions:")
            for session in sessions[:3]:  # Show last 3
                print(f"  • Session {session['id']}: {session['session_name']}")
                print(f"    Status: {session['status']}")
                print(f"    Tests: {session.get('total_tests', 0)}")
        else:
            print("No test sessions found. Run some tests first!")
            
    except Exception as e:
        print(f"❌ Error in database demo: {e}")
    finally:
        runner.close()


def main():
    """Main demo function."""
    print("🎪 AskTennis AI - Testing Framework Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Test data structure
        demo_test_data()
        
        # Demo 2: Quick test run
        demo_quick_test()
        
        # Demo 3: Category test
        demo_category_test()
        
        # Demo 4: Database operations
        demo_database_operations()
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo run your own tests, use:")
        print("  python run_automated_tests.py --quick --num-tests 5")
        print("  python run_automated_tests.py --full")
        print("  python run_automated_tests.py --category tournament_winner")
        print("  python run_automated_tests.py --interval 120  # Custom interval (min 90s)")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
