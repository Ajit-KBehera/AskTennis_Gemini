"""
Log filtering utilities for AskTennis AI application.
Provides functionality to filter and analyze logs by type, session, component, etc.
"""

import json
import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from pathlib import Path


class LogFilter:
    """
    Utility class for filtering and analyzing log files.
    Supports filtering by section type, session ID, component, and more.
    """
    
    def __init__(self, log_file_path: Optional[str] = None):
        """Initialize the log filter.
        
        Args:
            log_file_path: Path to log file. If None, searches for latest log file.
        """
        self.log_file_path = log_file_path or self._find_latest_log_file()
        self.log_entries: List[Dict[str, Any]] = []
        self._load_logs()
    
    def _find_latest_log_file(self) -> Optional[str]:
        """Find the latest log file in the logs directory.
        
        Returns:
            Path to latest log file, or None if not found
        """
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return None
        
        log_files = list(logs_dir.glob("asktennis_ai_interaction_*.log"))
        if not log_files:
            return None
        
        # Sort by modification time, return most recent
        latest_file = max(log_files, key=lambda p: p.stat().st_mtime)
        return str(latest_file)
    
    def _load_logs(self):
        """Load logs from file, parsing both JSON and text formats."""
        if not self.log_file_path or not Path(self.log_file_path).exists():
            return
        
        current_entry = {}
        current_section = None
        current_timestamp = None
        
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Try to parse as JSON first
                try:
                    entry = json.loads(line)
                    if isinstance(entry, dict) and 'section' in entry:
                        self.log_entries.append(entry)
                    continue
                except (json.JSONDecodeError, ValueError):
                    pass
                
                # Parse text format - extract timestamp from log line format
                # Format: "2025-11-05 16:46:49 - module - INFO - message"
                timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    current_timestamp = timestamp_match.group(1)
                
                # Parse text format
                if line.endswith("START ==="):
                    # Extract section name
                    current_section = re.search(r'=== (.+) START ===', line)
                    if current_section:
                        current_section = current_section.group(1).strip()
                        current_entry = {"section": current_section, "data": {}}
                elif line.endswith("END ==="):
                    # End of section
                    if current_entry:
                        self.log_entries.append({
                            "timestamp": current_timestamp or datetime.now().isoformat(),
                            "section": current_section,
                            "data": current_entry.get("data", {})
                        })
                        current_entry = {}
                        current_section = None
                        current_timestamp = None
                elif current_entry and ":" in line and not line.startswith("==="):
                    # Parse key-value pairs (skip section markers)
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        # Skip timestamp/levelname lines from logging format
                        if key in ['asctime', 'name', 'levelname', 'message']:
                            continue
                        # Try to parse value as JSON, otherwise use as string
                        value_str = parts[1].strip()
                        try:
                            value = json.loads(value_str)
                        except (json.JSONDecodeError, ValueError):
                            value = value_str
                        current_entry["data"][key] = value
    
    def filter_by_section(self, section_types: List[str]) -> List[Dict[str, Any]]:
        """Filter logs by section type(s).
        
        Args:
            section_types: List of section types to filter (e.g., ["ERROR", "USER QUERY"])
            
        Returns:
            List of matching log entries
        """
        section_set = set(section_types)
        return [entry for entry in self.log_entries if entry.get("section") in section_set]
    
    def filter_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Filter logs by session ID.
        
        Args:
            session_id: Session ID to filter by
            
        Returns:
            List of matching log entries
        """
        return [
            entry for entry in self.log_entries
            if entry.get("data", {}).get("session_id") == session_id
        ]
    
    def filter_by_component(self, component: str) -> List[Dict[str, Any]]:
        """Filter logs by component name.
        
        Args:
            component: Component name to filter by (e.g., "query_service")
            
        Returns:
            List of matching log entries
        """
        return [
            entry for entry in self.log_entries
            if entry.get("data", {}).get("component") == component
        ]
    
    def filter_by_date_range(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Filter logs by date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of matching log entries
        """
        filtered = []
        for entry in self.log_entries:
            timestamp_str = entry.get("timestamp")
            if not timestamp_str:
                continue
            
            try:
                entry_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if start_date and entry_date < start_date:
                    continue
                if end_date and entry_date > end_date:
                    continue
                filtered.append(entry)
            except (ValueError, AttributeError):
                continue
        
        return filtered
    
    def filter_by_keyword(self, keyword: str, field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter logs by keyword search.
        
        Args:
            keyword: Keyword to search for
            field: Specific field to search in (None searches all fields)
            
        Returns:
            List of matching log entries
        """
        keyword_lower = keyword.lower()
        filtered = []
        
        for entry in self.log_entries:
            if field:
                # Search in specific field
                value = entry.get("data", {}).get(field)
                if value and keyword_lower in str(value).lower():
                    filtered.append(entry)
            else:
                # Search in all fields
                entry_str = json.dumps(entry).lower()
                if keyword_lower in entry_str:
                    filtered.append(entry)
        
        return filtered
    
    def get_unique_sessions(self) -> Set[str]:
        """Get all unique session IDs from logs.
        
        Returns:
            Set of unique session IDs
        """
        sessions = set()
        for entry in self.log_entries:
            session_id = entry.get("data", {}).get("session_id")
            if session_id:
                sessions.add(session_id)
        return sessions
    
    def get_unique_components(self) -> Set[str]:
        """Get all unique component names from logs.
        
        Returns:
            Set of unique component names
        """
        components = set()
        for entry in self.log_entries:
            component = entry.get("data", {}).get("component")
            if component:
                components.add(component)
        return components
    
    def get_section_counts(self) -> Dict[str, int]:
        """Get count of each section type.
        
        Returns:
            Dictionary mapping section names to counts
        """
        counts = {}
        for entry in self.log_entries:
            section = entry.get("section", "UNKNOWN")
            counts[section] = counts.get(section, 0) + 1
        return counts
    
    def get_errors_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all errors in logs.
        
        Returns:
            List of error entries with key information
        """
        errors = self.filter_by_section(["ERROR"])
        summary = []
        
        for error in errors:
            data = error.get("data", {})
            summary.append({
                "timestamp": error.get("timestamp"),
                "error_type": data.get("error_type"),
                "error_message": data.get("error_message"),
                "component": data.get("component"),
                "context": data.get("context"),
                "error_file": data.get("error_file"),
                "error_line": data.get("error_line")
            })
        
        return summary
    
    def export_filtered(self, filtered_entries: List[Dict[str, Any]], 
                       output_file: str, format: str = "json"):
        """Export filtered log entries to a file.
        
        Args:
            filtered_entries: List of log entries to export
            output_file: Path to output file
            format: Export format ("json" or "text")
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == "json":
                for entry in filtered_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            else:
                # Text format
                for entry in filtered_entries:
                    section = entry.get("section", "UNKNOWN")
                    f.write(f"=== {section} START ===\n")
                    f.write(f"timestamp: {entry.get('timestamp', 'N/A')}\n")
                    for key, value in entry.get("data", {}).items():
                        if value is not None:
                            f.write(f"{key}: {value}\n")
                    f.write(f"=== {section} END ===\n\n")

