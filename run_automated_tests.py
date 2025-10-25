#!/usr/bin/env python3
"""
Main execution script for automated tennis AI testing.
Provides command-line interface for running automated tests.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from testing.test_runner import TennisTestRunner
from testing.test_data.tennis_qa_dataset import TENNIS_QA_DATASET, get_test_categories


def print_banner():
    """Print the test runner banner."""
    print("=" * 80)
    print("🧪 AskTennis AI - Automated Testing Framework")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total test cases available: {len(TENNIS_QA_DATASET)}")
    print("=" * 80)


def print_test_categories():
    """Print available test categories."""
    categories = get_test_categories()
    print("\n📋 Available Test Categories:")
    print("-" * 40)
    for category, count in categories.items():
        print(f"  • {category}: {count} tests")
    print()


def run_full_test_suite(args):
    """Run the full test suite."""
    print("🚀 Starting full test suite execution...")
    
    runner = TennisTestRunner()
    
    try:
        results = runner.run_automated_tests(
            interval_seconds=args.interval,
            progress_callback=progress_callback
        )
        
        if results.get('success'):
            print("\n✅ Full test suite completed successfully!")
            print_summary(results['report'])
        else:
            print(f"\n❌ Test suite failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running test suite: {e}")
        return False
    finally:
        runner.close()
    
    return True


def run_quick_test(args):
    """Run a quick test with subset of tests."""
    print(f"🏃‍♂️ Starting quick test with {args.num_tests} tests...")
    
    runner = TennisTestRunner()
    
    try:
        results = runner.run_quick_test(num_tests=args.num_tests)
        
        if results.get('success'):
            print("\n✅ Quick test completed successfully!")
            print_summary(results['report'])
        else:
            print(f"\n❌ Quick test failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running quick test: {e}")
        return False
    finally:
        runner.close()
    
    return True


def run_category_test(args):
    """Run tests for a specific category."""
    print(f"🎯 Starting category test for: {args.category}")
    
    runner = TennisTestRunner()
    
    try:
        results = runner.run_category_test(
            category=args.category,
            interval_seconds=args.interval
        )
        
        if results.get('success'):
            print(f"\n✅ Category test for '{args.category}' completed successfully!")
            print_summary(results['report'])
        else:
            print(f"\n❌ Category test failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running category test: {e}")
        return False
    finally:
        runner.close()
    
    return True


def list_sessions(args):
    """List all test sessions."""
    runner = TennisTestRunner()
    
    try:
        sessions = runner.list_all_sessions()
        
        if not sessions:
            print("📭 No test sessions found.")
            return True
        
        print(f"\n📋 Found {len(sessions)} test sessions:")
        print("-" * 80)
        print(f"{'ID':<5} {'Session Name':<30} {'Status':<10} {'Tests':<8} {'Pass Rate':<10} {'Date':<20}")
        print("-" * 80)
        
        for session in sessions:
            pass_rate = (session.get('passed_tests', 0) / session.get('total_tests', 1)) * 100
            print(f"{session['id']:<5} {session['session_name'][:29]:<30} {session['status']:<10} "
                  f"{session['total_tests']:<8} {pass_rate:.1f}%{'':<5} {session['created_at'][:19]:<20}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error listing sessions: {e}")
        return False
    finally:
        runner.close()


def export_session(args):
    """Export session data."""
    runner = TennisTestRunner()
    
    try:
        data = runner.export_session_data(args.session_id, args.format)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(data)
            
            print(f"📁 Session data exported to: {output_path}")
        else:
            print(data)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error exporting session: {e}")
        return False
    finally:
        runner.close()


def print_summary(report):
    """Print test summary."""
    if not report:
        return
    
    basic_metrics = report.get('basic_metrics', {})
    accuracy_metrics = report.get('accuracy_metrics', {})
    performance_metrics = report.get('performance_metrics', {})
    
    print("\n📊 Test Summary:")
    print("-" * 40)
    print(f"Total Tests: {basic_metrics.get('total_tests', 0)}")
    print(f"Passed: {basic_metrics.get('passed_tests', 0)}")
    print(f"Failed: {basic_metrics.get('failed_tests', 0)}")
    print(f"Errors: {basic_metrics.get('error_tests', 0)}")
    print(f"Pass Rate: {basic_metrics.get('pass_rate', 0):.1%}")
    print(f"Average Accuracy: {accuracy_metrics.get('average_accuracy', 0):.2%}")
    print(f"Average Execution Time: {performance_metrics.get('average_execution_time', 0):.2f}s")


def progress_callback(current, total, result):
    """Progress callback for test execution."""
    if current % 10 == 0 or current == total:
        print(f"📈 Progress: {current}/{total} tests completed")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="AskTennis AI - Automated Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_automated_tests.py --full                    # Run all tests (90s intervals)
  python run_automated_tests.py --quick --num-tests 5     # Run 5 quick tests (90s intervals)
  python run_automated_tests.py --category tournament_winner  # Run category tests (90s intervals)
  python run_automated_tests.py --interval 120           # Run with 120s intervals
  python run_automated_tests.py --list-sessions           # List all sessions
  python run_automated_tests.py --export 1 --output results.json  # Export session
        """
    )
    
    # Test execution options
    parser.add_argument('--full', action='store_true', help='Run full test suite')
    parser.add_argument('--quick', action='store_true', help='Run quick test with subset')
    parser.add_argument('--category', type=str, help='Run tests for specific category')
    parser.add_argument('--num-tests', type=int, default=10, help='Number of tests for quick run')
    parser.add_argument('--interval', type=int, default=90, help='Interval between tests (seconds, minimum 90)')
    
    # Session management options
    parser.add_argument('--list-sessions', action='store_true', help='List all test sessions')
    parser.add_argument('--export', type=int, help='Export session data (specify session ID)')
    parser.add_argument('--format', type=str, default='json', choices=['json', 'csv'], help='Export format')
    parser.add_argument('--output', type=str, help='Output file for export')
    
    # General options
    parser.add_argument('--categories', action='store_true', help='Show available test categories')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Handle different commands
    if args.categories:
        print_test_categories()
        return 0
    
    if args.list_sessions:
        success = list_sessions(args)
        return 0 if success else 1
    
    if args.export:
        success = export_session(args)
        return 0 if success else 1
    
    if args.full:
        success = run_full_test_suite(args)
        return 0 if success else 1
    
    if args.quick:
        success = run_quick_test(args)
        return 0 if success else 1
    
    if args.category:
        success = run_category_test(args)
        return 0 if success else 1
    
    # No specific command provided, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
