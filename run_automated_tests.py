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
    pass


def print_test_categories():
    """Print available test categories."""
    pass


def run_full_test_suite(args):
    """Run the full test suite."""
    runner = TennisTestRunner()
    
    try:
        results = runner.run_automated_tests(
            interval_seconds=args.interval,
            progress_callback=progress_callback
        )
        
        if results.get('success'):
            print_summary(results['report'])
        else:
            return False
            
    except Exception as e:
        return False
    finally:
        runner.close()
    
    return True


def run_quick_test(args):
    """Run a quick test with subset of tests."""
    runner = TennisTestRunner()
    
    try:
        results = runner.run_quick_test(num_tests=args.num_tests)
        
        if results.get('success'):
            print_summary(results['report'])
        else:
            return False
            
    except Exception as e:
        return False
    finally:
        runner.close()
    
    return True


def run_category_test(args):
    """Run tests for a specific category."""
    runner = TennisTestRunner()
    
    try:
        results = runner.run_category_test(
            category=args.category,
            interval_seconds=args.interval
        )
        
        if results.get('success'):
            print_summary(results['report'])
        else:
            return False
            
    except Exception as e:
        return False
    finally:
        runner.close()
    
    return True


def run_specific_questions(args):
    """Run specific question numbers."""
    if not args.questions:
        return False
    
    # Parse question numbers
    question_ids = []
    for q in args.questions:
        if '-' in q:
            # Handle ranges like "1-10"
            start, end = map(int, q.split('-'))
            question_ids.extend(range(start, end + 1))
        else:
            # Handle individual numbers
            question_ids.append(int(q))
    
    # Remove duplicates and sort
    question_ids = sorted(list(set(question_ids)))
    
    runner = TennisTestRunner()
    
    try:
        results = runner.run_automated_tests(
            test_subset=question_ids,
            interval_seconds=args.interval,
            progress_callback=progress_callback
        )
        
        if results.get('success'):
            print_summary(results['report'])
        else:
            return False
            
    except Exception as e:
        return False
    finally:
        runner.close()
    
    return True


def list_sessions(args):
    """List all test sessions."""
    runner = TennisTestRunner()
    
    try:
        sessions = runner.list_all_sessions()
        return True
        
    except Exception as e:
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
        
        return True
        
    except Exception as e:
        return False
    finally:
        runner.close()


def print_summary(report):
    """Print test summary."""
    pass


def progress_callback(current, total, result):
    """Progress callback for test execution."""
    pass


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="AskTennis AI - Automated Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_automated_tests.py --full                    # Run all tests (30s intervals)
  python run_automated_tests.py --quick --num-tests 5     # Run 5 quick tests (30s intervals)
  python run_automated_tests.py --category tournament_winner  # Run category tests (30s intervals)
  python run_automated_tests.py --questions 28            # Run specific question 28
  python run_automated_tests.py --questions 1,5,10,15     # Run specific questions 1,5,10,15
  python run_automated_tests.py --questions 80-100        # Run questions 80-100
  python run_automated_tests.py --questions 1-20 --interval 60  # Run questions 1-20 with 60s intervals
  python run_automated_tests.py --interval 60           # Run with 60s intervals
  python run_automated_tests.py --list-sessions           # List all sessions
  python run_automated_tests.py --export 1 --output results.json  # Export session
        """
    )
    
    # Test execution options
    parser.add_argument('--full', action='store_true', help='Run full test suite')
    parser.add_argument('--quick', action='store_true', help='Run quick test with subset')
    parser.add_argument('--category', type=str, help='Run tests for specific category')
    parser.add_argument('--questions', nargs='+', help='Run specific question numbers (e.g., --questions 1,2,3 or --questions 1-10)')
    parser.add_argument('--num-tests', type=int, default=10, help='Number of tests for quick run')
    parser.add_argument('--interval', type=int, default=30, help='Interval between tests (seconds, minimum 30)')
    
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
    
    if args.questions:
        success = run_specific_questions(args)
        return 0 if success else 1
    
    # No specific command provided, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
