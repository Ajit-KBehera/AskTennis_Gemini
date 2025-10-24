#!/usr/bin/env python3
"""
Log Management System for AskTennis AI
Automatically manages log files to prevent disk space issues.
Deletes logs after 5 sessions to maintain optimal performance.
"""

import os
import glob
import re
from datetime import datetime, timedelta
from pathlib import Path
import logging

class LogManager:
    """Manages log files with automatic cleanup and session tracking."""
    
    def __init__(self, logs_dir="logs", max_sessions=5, max_age_days=7):
        """
        Initialize log manager.
        
        Args:
            logs_dir (str): Directory containing log files
            max_sessions (int): Maximum number of sessions to keep
            max_age_days (int): Maximum age of logs in days
        """
        self.logs_dir = Path(logs_dir)
        self.max_sessions = max_sessions
        self.max_age_days = max_age_days
        self.session_tracker_file = self.logs_dir / "session_tracker.json"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging for log manager
        self.setup_log_manager_logging()
    
    def setup_log_manager_logging(self):
        """Setup logging for the log manager itself."""
        log_manager_logger = logging.getLogger('log_manager')
        log_manager_logger.setLevel(logging.INFO)
        
        # Create handler for log manager
        handler = logging.FileHandler(self.logs_dir / 'log_manager.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log_manager_logger.addHandler(handler)
        
        # Disable console output
        log_manager_logger.propagate = False
        
        self.log_manager_logger = log_manager_logger
    
    def get_log_files(self):
        """Get all log files in the logs directory."""
        pattern = str(self.logs_dir / "asktennis_ai_interaction_*.log")
        return glob.glob(pattern)
    
    def parse_log_filename(self, filename):
        """
        Parse log filename to extract session information.
        
        Format: asktennis_ai_interaction_YYYYMMDD_HHMMSS_sessionid.log
        
        Args:
            filename (str): Log filename
            
        Returns:
            dict: Parsed information or None if invalid format
        """
        basename = os.path.basename(filename)
        pattern = r'asktennis_ai_interaction_(\d{8})_(\d{6})_([a-f0-9]{8})\.log'
        match = re.match(pattern, basename)
        
        if match:
            date_str, time_str, session_id = match.groups()
            try:
                # Parse date and time
                date_part = datetime.strptime(date_str, '%Y%m%d')
                time_part = datetime.strptime(time_str, '%H%M%S').time()
                full_datetime = datetime.combine(date_part.date(), time_part)
                
                return {
                    'filename': filename,
                    'datetime': full_datetime,
                    'session_id': session_id,
                    'date_str': date_str,
                    'time_str': time_str
                }
            except ValueError:
                return None
        return None
    
    def get_sessions(self):
        """
        Get all sessions with their log files.
        
        Returns:
            dict: Sessions grouped by session_id
        """
        sessions = {}
        log_files = self.get_log_files()
        
        for log_file in log_files:
            parsed = self.parse_log_filename(log_file)
            if parsed:
                session_id = parsed['session_id']
                if session_id not in sessions:
                    sessions[session_id] = []
                sessions[session_id].append(parsed)
        
        # Sort sessions by datetime
        for session_id in sessions:
            sessions[session_id].sort(key=lambda x: x['datetime'])
        
        return sessions
    
    def get_oldest_sessions(self, sessions):
        """
        Get the oldest sessions that should be deleted.
        
        Args:
            sessions (dict): All sessions
            
        Returns:
            list: Session IDs to delete
        """
        if len(sessions) <= self.max_sessions:
            return []
        
        # Sort sessions by their earliest log file
        session_times = []
        for session_id, session_logs in sessions.items():
            earliest_time = min(log['datetime'] for log in session_logs)
            session_times.append((session_id, earliest_time))
        
        # Sort by time (oldest first)
        session_times.sort(key=lambda x: x[1])
        
        # Get sessions to delete (oldest ones beyond max_sessions)
        sessions_to_delete = session_times[:-self.max_sessions]
        return [session_id for session_id, _ in sessions_to_delete]
    
    def delete_session_logs(self, session_id, sessions):
        """
        Delete all log files for a specific session.
        
        Args:
            session_id (str): Session ID to delete
            sessions (dict): All sessions
        """
        if session_id not in sessions:
            return 0
        
        deleted_count = 0
        for log_info in sessions[session_id]:
            try:
                if os.path.exists(log_info['filename']):
                    os.remove(log_info['filename'])
                    deleted_count += 1
                    self.log_manager_logger.info(f"Deleted log file: {log_info['filename']}")
            except OSError as e:
                self.log_manager_logger.error(f"Error deleting {log_info['filename']}: {e}")
        
        return deleted_count
    
    def cleanup_old_logs(self):
        """
        Clean up old log files based on age.
        
        Returns:
            int: Number of files deleted
        """
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        deleted_count = 0
        
        log_files = self.get_log_files()
        for log_file in log_files:
            parsed = self.parse_log_filename(log_file)
            if parsed and parsed['datetime'] < cutoff_date:
                try:
                    os.remove(log_file)
                    deleted_count += 1
                    self.log_manager_logger.info(f"Deleted old log file: {log_file}")
                except OSError as e:
                    self.log_manager_logger.error(f"Error deleting old log {log_file}: {e}")
        
        return deleted_count
    
    def cleanup_session_logs(self):
        """
        Clean up log files based on session count.
        
        Returns:
            int: Number of files deleted
        """
        sessions = self.get_sessions()
        sessions_to_delete = self.get_oldest_sessions(sessions)
        
        total_deleted = 0
        for session_id in sessions_to_delete:
            deleted_count = self.delete_session_logs(session_id, sessions)
            total_deleted += deleted_count
            self.log_manager_logger.info(f"Deleted session {session_id}: {deleted_count} files")
        
        return total_deleted
    
    def cleanup_all(self):
        """
        Perform complete log cleanup.
        
        Returns:
            dict: Cleanup statistics
        """
        self.log_manager_logger.info("Starting log cleanup process")
        
        # Get initial statistics
        initial_files = len(self.get_log_files())
        initial_sessions = len(self.get_sessions())
        
        # Clean up by age
        age_deleted = self.cleanup_old_logs()
        
        # Clean up by session count
        session_deleted = self.cleanup_session_logs()
        
        # Get final statistics
        final_files = len(self.get_log_files())
        final_sessions = len(self.get_sessions())
        
        stats = {
            'initial_files': initial_files,
            'initial_sessions': initial_sessions,
            'age_deleted': age_deleted,
            'session_deleted': session_deleted,
            'total_deleted': age_deleted + session_deleted,
            'final_files': final_files,
            'final_sessions': final_sessions
        }
        
        self.log_manager_logger.info(f"Log cleanup completed: {stats}")
        return stats
    
    def get_log_statistics(self):
        """
        Get current log statistics.
        
        Returns:
            dict: Current log statistics
        """
        log_files = self.get_log_files()
        sessions = self.get_sessions()
        
        total_size = 0
        for log_file in log_files:
            try:
                total_size += os.path.getsize(log_file)
            except OSError:
                pass
        
        return {
            'total_files': len(log_files),
            'total_sessions': len(sessions),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_sessions': self.max_sessions,
            'max_age_days': self.max_age_days
        }
    
    def list_sessions(self):
        """
        List all current sessions with details.
        
        Returns:
            list: Session information
        """
        sessions = self.get_sessions()
        session_list = []
        
        for session_id, session_logs in sessions.items():
            earliest = min(log['datetime'] for log in session_logs)
            latest = max(log['datetime'] for log in session_logs)
            file_count = len(session_logs)
            
            session_list.append({
                'session_id': session_id,
                'file_count': file_count,
                'earliest': earliest,
                'latest': latest,
                'duration': latest - earliest
            })
        
        # Sort by earliest time
        session_list.sort(key=lambda x: x['earliest'])
        return session_list

def main():
    """Main function for log management."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AskTennis AI Log Management')
    parser.add_argument('--logs-dir', default='logs', help='Logs directory')
    parser.add_argument('--max-sessions', type=int, default=5, help='Maximum sessions to keep')
    parser.add_argument('--max-age-days', type=int, default=7, help='Maximum age in days')
    parser.add_argument('--action', choices=['cleanup', 'stats', 'list'], default='cleanup', 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    # Create log manager
    log_manager = LogManager(
        logs_dir=args.logs_dir,
        max_sessions=args.max_sessions,
        max_age_days=args.max_age_days
    )
    
    if args.action == 'cleanup':
        stats = log_manager.cleanup_all()
        return stats
    
    elif args.action == 'stats':
        stats = log_manager.get_log_statistics()
        return stats
    
    elif args.action == 'list':
        sessions = log_manager.list_sessions()
        return sessions

if __name__ == "__main__":
    result = main()
    # Exit with appropriate code
    exit(0 if result else 1)
