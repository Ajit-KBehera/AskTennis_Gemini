"""
Database verification utilities for AskTennis data loading.
Handles verification of data integrity and completeness.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from config.settings import VERBOSE_LOGGING
from config.paths import DataPaths


class DatabaseVerifier:
    """
    Verifies database integrity and data completeness.
    
    Handles:
    - Data integrity checks
    - Completeness verification
    - Statistical analysis
    - Data quality assessment
    """
    
    def __init__(self, verbose: bool = None):
        """
        Initialize the database verifier.
        
        Args:
            verbose (bool): Enable verbose logging
        """
        self.verbose = verbose if verbose is not None else VERBOSE_LOGGING
        self.paths = DataPaths()
        
    def verify_enhancement(self, database_file: str = None) -> Dict[str, Any]:
        """
        Verifies that the player, rankings, and historical data integration worked correctly.
        
        Args:
            database_file: Database file path
            
        Returns:
            Dictionary with verification results
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        if self.verbose:
            print("\n--- Verifying Complete Historical Integration ---")
        
        try:
            conn = sqlite3.connect(database_file)
            
            verification_results = {
                'database_file': database_file,
                'tables_exist': self._check_tables_exist(conn),
                'data_counts': self._get_data_counts(conn),
                'historical_coverage': self._get_historical_coverage(conn),
                'era_distribution': self._get_era_distribution(conn),
                'tournament_type_distribution': self._get_tournament_type_distribution(conn),
                'tourney_level_distribution': self._get_tourney_level_distribution(conn),
                'decade_distribution': self._get_decade_distribution(conn),
                'player_match_integration': self._check_player_match_integration(conn),
                'data_quality': self._assess_data_quality(conn)
            }
            
            conn.close()
            
            if self.verbose:
                self._print_verification_summary(verification_results)
            
            return verification_results
            
        except Exception as e:
            if self.verbose:
                print(f"Error verifying database: {e}")
            return {'error': str(e)}
    
    def _check_tables_exist(self, conn: sqlite3.Connection) -> Dict[str, bool]:
        """Check if required tables exist."""
        tables = ['matches', 'players', 'rankings', 'doubles_matches']
        results = {}
        
        for table in tables:
            try:
                conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                results[table] = True
            except:
                results[table] = False
        
        return results
    
    def _get_data_counts(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """Get data counts for each table."""
        counts = {}
        
        tables = ['matches', 'players', 'rankings', 'doubles_matches']
        for table in tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                counts[table] = count
            except:
                counts[table] = 0
        
        return counts
    
    def _get_historical_coverage(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Get historical coverage information."""
        try:
            date_range = conn.execute("SELECT MIN(event_year), MAX(event_year) FROM matches").fetchone()
            return {
                'start_year': date_range[0],
                'end_year': date_range[1],
                'total_years': date_range[1] - date_range[0] + 1 if date_range[0] and date_range[1] else 0
            }
        except:
            return {'start_year': None, 'end_year': None, 'total_years': 0}
    
    def _get_era_distribution(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """Get era distribution."""
        try:
            era_counts = conn.execute("""
                SELECT era, COUNT(*) as matches 
                FROM matches 
                GROUP BY era 
                ORDER BY era
            """).fetchall()
            return {era: count for era, count in era_counts}
        except:
            return {}
    
    def _get_tournament_type_distribution(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """Get tournament type distribution."""
        try:
            type_counts = conn.execute("""
                SELECT tournament_type, COUNT(*) as matches 
                FROM matches 
                GROUP BY tournament_type 
                ORDER BY matches DESC
            """).fetchall()
            return {tournament_type: count for tournament_type, count in type_counts}
        except:
            return {}
    
    def _get_tourney_level_distribution(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """Get tournament level distribution."""
        try:
            level_counts = conn.execute("""
                SELECT tourney_level, COUNT(*) as matches 
                FROM matches 
                GROUP BY tourney_level 
                ORDER BY matches DESC
            """).fetchall()
            return {tourney_level: count for tourney_level, count in level_counts}
        except:
            return {}
    
    def _get_decade_distribution(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """Get decade distribution."""
        try:
            decade_counts = conn.execute("""
                SELECT 
                    CASE 
                        WHEN event_year < 1880 THEN '1870s'
                        WHEN event_year < 1890 THEN '1880s'
                        WHEN event_year < 1900 THEN '1890s'
                        WHEN event_year < 1910 THEN '1900s'
                        WHEN event_year < 1920 THEN '1910s'
                        WHEN event_year < 1930 THEN '1920s'
                        WHEN event_year < 1940 THEN '1930s'
                        WHEN event_year < 1950 THEN '1940s'
                        WHEN event_year < 1960 THEN '1950s'
                        WHEN event_year < 1970 THEN '1960s'
                        WHEN event_year < 1980 THEN '1970s'
                        WHEN event_year < 1990 THEN '1980s'
                        WHEN event_year < 2000 THEN '1990s'
                        WHEN event_year < 2010 THEN '2000s'
                        WHEN event_year < 2020 THEN '2010s'
                        ELSE '2020s'
                    END as decade,
                    COUNT(*) as matches
                FROM matches 
                GROUP BY decade 
                ORDER BY decade
            """).fetchall()
            return {decade: count for decade, count in decade_counts}
        except:
            return {}
    
    def _check_player_match_integration(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """Check player-match integration."""
        try:
            total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
            
            matches_with_winner_info = conn.execute("""
                SELECT COUNT(*) FROM matches_with_full_info 
                WHERE winner_first_name IS NOT NULL
            """).fetchone()[0]
            
            matches_with_loser_info = conn.execute("""
                SELECT COUNT(*) FROM matches_with_full_info 
                WHERE loser_first_name IS NOT NULL
            """).fetchone()[0]
            
            return {
                'total_matches': total_matches,
                'matches_with_winner_info': matches_with_winner_info,
                'matches_with_loser_info': matches_with_loser_info,
                'winner_integration_rate': (matches_with_winner_info / total_matches * 100) if total_matches > 0 else 0,
                'loser_integration_rate': (matches_with_loser_info / total_matches * 100) if total_matches > 0 else 0
            }
        except:
            return {}
    
    def _assess_data_quality(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Assess overall data quality."""
        try:
            # Check for missing data
            missing_data = {}
            
            # Check missing surface data
            try:
                missing_surface = conn.execute("SELECT COUNT(*) FROM matches WHERE surface IS NULL OR surface = ''").fetchone()[0]
                missing_data['missing_surface'] = missing_surface
            except:
                missing_data['missing_surface'] = 0
            
            # Check missing score data
            try:
                missing_score = conn.execute("SELECT COUNT(*) FROM matches WHERE score IS NULL OR score = ''").fetchone()[0]
                missing_data['missing_score'] = missing_score
            except:
                missing_data['missing_score'] = 0
            
            # Check missing tournament level data
            try:
                missing_level = conn.execute("SELECT COUNT(*) FROM matches WHERE tourney_level IS NULL OR tourney_level = ''").fetchone()[0]
                missing_data['missing_level'] = missing_level
            except:
                missing_data['missing_level'] = 0
            
            total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
            
            return {
                'total_matches': total_matches,
                'missing_data': missing_data,
                'data_completeness': {
                    'surface_completeness': ((total_matches - missing_data['missing_surface']) / total_matches * 100) if total_matches > 0 else 0,
                    'score_completeness': ((total_matches - missing_data['missing_score']) / total_matches * 100) if total_matches > 0 else 0,
                    'level_completeness': ((total_matches - missing_data['missing_level']) / total_matches * 100) if total_matches > 0 else 0
                }
            }
        except:
            return {}
    
    def _print_verification_summary(self, results: Dict[str, Any]):
        """Print verification summary."""
        if 'error' in results:
            print(f"Verification failed: {results['error']}")
            return
        
        print(f"Database: {results['database_file']}")
        
        # Data counts
        counts = results['data_counts']
        print(f"Players in database: {counts.get('players', 0):,}")
        print(f"Rankings in database: {counts.get('rankings', 0):,}")
        print(f"Matches in database: {counts.get('matches', 0):,}")
        print(f"Doubles matches in database: {counts.get('doubles_matches', 0):,}")
        
        # Historical coverage
        coverage = results['historical_coverage']
        if coverage['start_year'] and coverage['end_year']:
            print(f"Historical coverage: {coverage['start_year']} to {coverage['end_year']}")
        
        # Era distribution
        era_dist = results['era_distribution']
        if era_dist:
            print("Matches by era:")
            for era, count in era_dist.items():
                print(f"  {era}: {count:,} matches")
        
        # Tournament type distribution
        type_dist = results['tournament_type_distribution']
        if type_dist:
            print("Matches by tournament type:")
            for tournament_type, count in type_dist.items():
                print(f"  {tournament_type}: {count:,} matches")
        
        # Data quality
        quality = results['data_quality']
        if quality:
            completeness = quality['data_completeness']
            print(f"Data completeness:")
            print(f"  Surface: {completeness['surface_completeness']:.1f}%")
            print(f"  Score: {completeness['score_completeness']:.1f}%")
            print(f"  Level: {completeness['level_completeness']:.1f}%")
    
    def get_database_statistics(self, database_file: str = None) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Args:
            database_file: Database file path
            
        Returns:
            Dictionary with database statistics
        """
        if database_file is None:
            database_file = self.paths.main_database_file
        
        try:
            conn = sqlite3.connect(database_file)
            
            stats = {
                'file_info': {
                    'path': database_file,
                    'size_bytes': self.paths.get_file_size(database_file)
                },
                'table_info': self._get_table_info(conn),
                'view_info': self._get_view_info(conn),
                'index_info': self._get_index_info(conn)
            }
            
            conn.close()
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_table_info(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Get table information."""
        try:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_info = {}
            
            for table in tables:
                table_name = table[0]
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                table_info[table_name] = {'row_count': count}
            
            return table_info
        except:
            return {}
    
    def _get_view_info(self, conn: sqlite3.Connection) -> List[str]:
        """Get view information."""
        try:
            views = conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()
            return [view[0] for view in views]
        except:
            return []
    
    def _get_index_info(self, conn: sqlite3.Connection) -> List[str]:
        """Get index information."""
        try:
            indexes = conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
            return [index[0] for index in indexes]
        except:
            return []
    
    def __str__(self):
        """String representation."""
        return f"DatabaseVerifier(verbose={self.verbose})"
    
    def __repr__(self):
        """Detailed string representation."""
        return f"DatabaseVerifier(verbose={self.verbose}, paths={self.paths})"
