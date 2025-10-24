#!/usr/bin/env python3
"""
Manual log cleanup script for AskTennis AI.
Immediately cleans up logs to keep only the 5 most recent sessions.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from log_management import LogManager

def main():
    """Main cleanup function."""
    print("🧹 AskTennis AI - Log Cleanup")
    print("=" * 50)
    
    # Create log manager with 5 session limit
    log_manager = LogManager(
        logs_dir="logs",
        max_sessions=5,
        max_age_days=7
    )
    
    # Get initial statistics
    print("📊 Current Log Status:")
    stats = log_manager.get_log_statistics()
    print(f"   - Total files: {stats['total_files']}")
    print(f"   - Total sessions: {stats['total_sessions']}")
    print(f"   - Total size: {stats['total_size_mb']} MB")
    print(f"   - Max sessions: {stats['max_sessions']}")
    print(f"   - Max age: {stats['max_age_days']} days")
    
    # List current sessions
    print("\n📋 Current Sessions:")
    sessions = log_manager.list_sessions()
    for i, session in enumerate(sessions, 1):
        print(f"   {i}. Session {session['session_id']}: {session['file_count']} files")
        print(f"      From: {session['earliest'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      To: {session['latest'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      Duration: {session['duration']}")
    
    # Perform cleanup
    print("\n🧹 Performing Cleanup...")
    cleanup_stats = log_manager.cleanup_all()
    
    print("\n✅ Cleanup Results:")
    print(f"   - Initial files: {cleanup_stats['initial_files']}")
    print(f"   - Initial sessions: {cleanup_stats['initial_sessions']}")
    print(f"   - Files deleted by age: {cleanup_stats['age_deleted']}")
    print(f"   - Files deleted by session: {cleanup_stats['session_deleted']}")
    print(f"   - Total deleted: {cleanup_stats['total_deleted']}")
    print(f"   - Final files: {cleanup_stats['final_files']}")
    print(f"   - Final sessions: {cleanup_stats['final_sessions']}")
    
    # Show final status
    print("\n📊 Final Status:")
    final_stats = log_manager.get_log_statistics()
    print(f"   - Total files: {final_stats['total_files']}")
    print(f"   - Total sessions: {final_stats['total_sessions']}")
    print(f"   - Total size: {final_stats['total_size_mb']} MB")
    
    print("\n✅ Log cleanup completed successfully!")
    print("🎯 Only the 5 most recent sessions are now kept.")

if __name__ == "__main__":
    main()
