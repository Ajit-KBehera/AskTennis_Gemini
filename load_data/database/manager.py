"""
Database management utilities for AskTennis data loading.
Handles general database operations and management tasks.
"""

import sqlite3
import pandas as pd
import os
from typing import Dict, Any, List, Optional
from config.settings import VERBOSE_LOGGING
from config.paths import DataPaths


class DatabaseManager:
    """
    Manages database operations and provides utility functions.
    
    Handles:
    - Database connection management
    - Query execution
    - Database maintenance
    - Backup and restore operations
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the database manager.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        
    def connect(self, database_file: str = None) -> sqlite3.Connection:
        """
        Create database connection.
        
        Args:
            database_file: Database file path
            
        Returns:
            SQLite connection object
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        try:
            conn = sqlite3.connect(database_file)
            return conn
        except Exception as e:
            if self.verbose:
                print(f"Error connecting to database: {e}")
            raise
    
    def execute_query(self, query: str, database_file: str = None) -> List[tuple]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            database_file: Database file path
            
        Returns:
            List of query results
        """
        try:
            conn = self.connect(database_file)
            cursor = conn.execute(query)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            if self.verbose:
                print(f"Error executing query: {e}")
            return []
    
    def execute_query_to_dataframe(self, query: str, database_file: str = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            database_file: Database file path
            
        Returns:
            DataFrame with query results
        """
        try:
            conn = self.connect(database_file)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            if self.verbose:
                print(f"Error executing query to DataFrame: {e}")
            return pd.DataFrame()
    
    def get_table_schema(self, table_name: str, database_file: str = None) -> List[Dict[str, Any]]:
        """
        Get table schema information.
        
        Args:
            table_name: Name of the table
            database_file: Database file path
            
        Returns:
            List of column information
        """
        try:
            conn = self.connect(database_file)
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            schema = []
            for col in columns:
                schema.append({
                    'cid': col[0],
                    'name': col[1],
                    'type': col[2],
                    'notnull': bool(col[3]),
                    'default_value': col[4],
                    'pk': bool(col[5])
                })
            
            return schema
        except Exception as e:
            if self.verbose:
                print(f"Error getting table schema: {e}")
            return []
    
    def get_all_tables(self, database_file: str = None) -> List[str]:
        """
        Get list of all tables in the database.
        
        Args:
            database_file: Database file path
            
        Returns:
            List of table names
        """
        try:
            conn = self.connect(database_file)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            if self.verbose:
                print(f"Error getting tables: {e}")
            return []
    
    def get_table_row_count(self, table_name: str, database_file: str = None) -> int:
        """
        Get row count for a specific table.
        
        Args:
            table_name: Name of the table
            database_file: Database file path
            
        Returns:
            Number of rows in the table
        """
        try:
            conn = self.connect(database_file)
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            if self.verbose:
                print(f"Error getting row count: {e}")
            return 0
    
    def backup_database(self, backup_file: str, database_file: str = None) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_file: Path for backup file
            database_file: Source database file path
            
        Returns:
            True if successful, False otherwise
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        try:
            # Ensure backup directory exists
            backup_dir = os.path.dirname(backup_file)
            if backup_dir:
                os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup
            conn = self.connect(database_file)
            backup_conn = sqlite3.connect(backup_file)
            conn.backup(backup_conn)
            conn.close()
            backup_conn.close()
            
            if self.verbose:
                print(f"Database backed up to: {backup_file}")
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error creating backup: {e}")
            return False
    
    def restore_database(self, backup_file: str, database_file: str = None) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_file: Path to backup file
            database_file: Target database file path
            
        Returns:
            True if successful, False otherwise
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        try:
            # Ensure target directory exists
            target_dir = os.path.dirname(database_file)
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)
            
            # Restore from backup
            backup_conn = sqlite3.connect(backup_file)
            conn = sqlite3.connect(database_file)
            backup_conn.backup(conn)
            conn.close()
            backup_conn.close()
            
            if self.verbose:
                print(f"Database restored from: {backup_file}")
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error restoring database: {e}")
            return False
    
    def optimize_database(self, database_file: str = None) -> bool:
        """
        Optimize database by running VACUUM and ANALYZE.
        
        Args:
            database_file: Database file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.connect(database_file)
            
            # Run VACUUM to reclaim space
            conn.execute("VACUUM")
            
            # Run ANALYZE to update statistics
            conn.execute("ANALYZE")
            
            conn.close()
            
            if self.verbose:
                print("Database optimized successfully")
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error optimizing database: {e}")
            return False
    
    def get_database_size(self, database_file: str = None) -> int:
        """
        Get database file size in bytes.
        
        Args:
            database_file: Database file path
            
        Returns:
            File size in bytes
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        return self.paths.get_file_size(database_file)
    
    def check_database_integrity(self, database_file: str = None) -> bool:
        """
        Check database integrity.
        
        Args:
            database_file: Database file path
            
        Returns:
            True if database is intact, False otherwise
        """
        try:
            conn = self.connect(database_file)
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            return result == "ok"
        except Exception as e:
            if self.verbose:
                print(f"Error checking database integrity: {e}")
            return False
    
    def __str__(self):
        """String representation."""
        return f"DatabaseManager(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"DatabaseManager(verbose={self.verbose}, paths={self.paths})"
