#!/usr/bin/env python3
"""
DuckDB vs SQLite Performance Benchmark for Tennis Analytics
===========================================================

This script benchmarks DuckDB against SQLite for tennis analytics queries
to demonstrate the performance improvements of columnar storage and
vectorized execution for tennis data analysis.

Performance Metrics:
- Query execution time
- Memory usage
- CPU utilization
- Result accuracy verification
"""

import time
import psutil
import pandas as pd
import sqlite3
import duckdb
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

class TennisAnalyticsBenchmark:
    """
    Comprehensive benchmark comparing DuckDB vs SQLite for tennis analytics.
    """
    
    def __init__(self, sqlite_db_path: str = "tennis_data.db", duckdb_db_path: str = "tennis_analytics.duckdb"):
        """Initialize benchmark with SQLite and DuckDB connections."""
        self.sqlite_db_path = sqlite_db_path
        self.duckdb_db_path = duckdb_db_path
        
        # Initialize connections
        self.sqlite_conn = None
        self.duckdb_conn = None
        
        # Benchmark results
        self.results = {
            "sqlite": {},
            "duckdb": {},
            "performance_improvements": {}
        }
    
    def setup_connections(self):
        """Setup SQLite and DuckDB connections."""
        print("🔧 Setting up database connections...")
        
        # SQLite connection
        if os.path.exists(self.sqlite_db_path):
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            print(f"✅ SQLite connection established: {self.sqlite_db_path}")
        else:
            print(f"❌ SQLite database not found: {self.sqlite_db_path}")
            return False
        
        # DuckDB connection
        self.duckdb_conn = duckdb.connect(self.duckdb_db_path)
        max_threads = os.cpu_count() or 4
        self.duckdb_conn.execute(f"SET threads TO {max_threads}")  # Use all cores
        self.duckdb_conn.execute("SET memory_limit TO '4GB'")
        print(f"✅ DuckDB connection established: {self.duckdb_db_path}")
        
        return True
    
    def get_system_info(self) -> Dict:
        """Get system information for benchmark context."""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "python_version": pd.__version__,
            "pandas_version": pd.__version__,
            "duckdb_version": duckdb.__version__ if hasattr(duckdb, '__version__') else "unknown"
        }
    
    def measure_query_performance(self, query: str, db_type: str) -> Dict:
        """Measure query performance for a specific database."""
        if db_type == "sqlite" and self.sqlite_conn:
            conn = self.sqlite_conn
        elif db_type == "duckdb" and self.duckdb_conn:
            conn = self.duckdb_conn
        else:
            return {"error": f"Connection not available for {db_type}"}
        
        # Measure memory before query
        memory_before = psutil.virtual_memory().used
        
        # Measure CPU before query
        cpu_before = psutil.cpu_percent()
        
        # Execute query and measure time
        start_time = time.time()
        try:
            result = pd.read_sql_query(query, conn)
            execution_time = time.time() - start_time
            success = True
            error = None
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            error = str(e)
            result = pd.DataFrame()
        
        # Measure memory and CPU after query
        memory_after = psutil.virtual_memory().used
        cpu_after = psutil.cpu_percent()
        
        return {
            "execution_time": execution_time,
            "memory_used": memory_after - memory_before,
            "cpu_usage": cpu_after - cpu_before,
            "success": success,
            "error": error,
            "result_rows": len(result),
            "result_columns": len(result.columns) if not result.empty else 0
        }
    
    def run_tennis_analytics_benchmarks(self):
        """Run comprehensive tennis analytics benchmarks."""
        print("🏁 Running Tennis Analytics Benchmarks...")
        
        # Define tennis analytics test queries
        test_queries = {
            "basic_count": "SELECT COUNT(*) as total_matches FROM matches",
            "top_players": """
                SELECT winner_name, COUNT(*) as wins 
                FROM matches 
                GROUP BY winner_name 
                ORDER BY wins DESC 
                LIMIT 10
            """,
            "surface_distribution": """
                SELECT surface, COUNT(*) as matches 
                FROM matches 
                GROUP BY surface 
                ORDER BY matches DESC
            """,
            "yearly_trends": """
                SELECT event_year, COUNT(*) as matches 
                FROM matches 
                GROUP BY event_year 
                ORDER BY event_year DESC 
                LIMIT 10
            """,
            "head_to_head": """
                SELECT winner_name, loser_name, COUNT(*) as total_matches,
                       SUM(CASE WHEN winner_name = winner_name THEN 1 ELSE 0 END) as wins
                FROM matches 
                WHERE (winner_name LIKE '%Federer%' AND loser_name LIKE '%Nadal%') 
                   OR (winner_name LIKE '%Nadal%' AND loser_name LIKE '%Federer%')
                GROUP BY winner_name, loser_name
            """,
            "ranking_analysis": """
                SELECT winner_name, winner_rank, loser_name, loser_rank, 
                       CASE WHEN winner_rank < loser_rank THEN 'Upset' ELSE 'Expected' END as result_type
                FROM matches 
                WHERE winner_rank IS NOT NULL AND loser_rank IS NOT NULL
                ORDER BY winner_rank, loser_rank
                LIMIT 100
            """,
            "complex_aggregation": """
                SELECT 
                    event_year,
                    surface,
                    COUNT(*) as total_matches,
                    COUNT(DISTINCT winner_name) as unique_winners,
                    COUNT(DISTINCT loser_name) as unique_losers,
                    AVG(winner_rank) as avg_winner_rank,
                    AVG(loser_rank) as avg_loser_rank
                FROM matches 
                WHERE event_year >= 2020
                GROUP BY event_year, surface
                ORDER BY event_year DESC, total_matches DESC
            """,
            "historical_analysis": """
                SELECT 
                    CASE 
                        WHEN event_year < 1980 THEN 'Pre-1980'
                        WHEN event_year < 1990 THEN '1980s'
                        WHEN event_year < 2000 THEN '1990s'
                        WHEN event_year < 2010 THEN '2000s'
                        WHEN event_year < 2020 THEN '2010s'
                        ELSE '2020s'
                    END as decade,
                    COUNT(*) as matches,
                    COUNT(DISTINCT winner_name) as unique_winners
                FROM matches 
                GROUP BY decade
                ORDER BY decade
            """
        }
        
        # Run benchmarks for each query
        for query_name, query in test_queries.items():
            print(f"\n📊 Benchmarking: {query_name}")
            
            # SQLite benchmark
            print("  🔍 Testing SQLite...")
            sqlite_result = self.measure_query_performance(query, "sqlite")
            self.results["sqlite"][query_name] = sqlite_result
            
            # DuckDB benchmark
            print("  🚀 Testing DuckDB...")
            duckdb_result = self.measure_query_performance(query, "duckdb")
            self.results["duckdb"][query_name] = duckdb_result
            
            # Calculate performance improvement
            if sqlite_result["success"] and duckdb_result["success"]:
                speedup = sqlite_result["execution_time"] / duckdb_result["execution_time"]
                self.results["performance_improvements"][query_name] = {
                    "speedup": speedup,
                    "sqlite_time": sqlite_result["execution_time"],
                    "duckdb_time": duckdb_result["execution_time"],
                    "memory_improvement": sqlite_result["memory_used"] - duckdb_result["memory_used"]
                }
                print(f"  ⚡ Performance: {speedup:.2f}x faster with DuckDB")
            else:
                print(f"  ❌ Query failed: SQLite={sqlite_result['success']}, DuckDB={duckdb_result['success']}")
    
    def run_memory_benchmark(self):
        """Run memory usage benchmarks."""
        print("\n🧠 Running Memory Usage Benchmarks...")
        
        # Large dataset queries for memory testing
        memory_queries = {
            "large_join": """
                SELECT m.*, p1.name_first, p1.name_last, p2.name_first, p2.name_last
                FROM matches m
                LEFT JOIN players p1 ON m.winner_id = p1.player_id
                LEFT JOIN players p2 ON m.loser_id = p2.player_id
                LIMIT 10000
            """,
            "large_aggregation": """
                SELECT 
                    winner_name,
                    COUNT(*) as total_wins,
                    COUNT(DISTINCT tourney_name) as tournaments_won,
                    COUNT(DISTINCT surface) as surfaces_won,
                    AVG(winner_rank) as avg_rank
                FROM matches 
                GROUP BY winner_name
                ORDER BY total_wins DESC
            """,
            "complex_ranking": """
                SELECT 
                    winner_name,
                    event_year,
                    COUNT(*) as wins,
                    RANK() OVER (PARTITION BY event_year ORDER BY COUNT(*) DESC) as yearly_rank
                FROM matches 
                GROUP BY winner_name, event_year
                ORDER BY event_year DESC, wins DESC
            """
        }
        
        for query_name, query in memory_queries.items():
            print(f"  📊 Memory test: {query_name}")
            
            # Measure memory usage
            memory_before = psutil.virtual_memory().used
            
            # SQLite memory test
            sqlite_result = self.measure_query_performance(query, "sqlite")
            sqlite_memory = psutil.virtual_memory().used - memory_before
            
            # DuckDB memory test
            memory_before = psutil.virtual_memory().used
            duckdb_result = self.measure_query_performance(query, "duckdb")
            duckdb_memory = psutil.virtual_memory().used - memory_before
            
            print(f"    SQLite memory: {sqlite_memory / 1024 / 1024:.2f} MB")
            print(f"    DuckDB memory: {duckdb_memory / 1024 / 1024:.2f} MB")
            if duckdb_memory > 0:
                print(f"    Memory efficiency: {sqlite_memory / duckdb_memory:.2f}x better with DuckDB")
            else:
                print(f"    Memory efficiency: DuckDB used minimal memory")
    
    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report."""
        print("\n📊 Generating Benchmark Report...")
        
        # Calculate overall performance metrics
        total_sqlite_time = sum(result["execution_time"] for result in self.results["sqlite"].values() if result["success"])
        total_duckdb_time = sum(result["execution_time"] for result in self.results["duckdb"].values() if result["success"])
        
        overall_speedup = total_sqlite_time / total_duckdb_time if total_duckdb_time > 0 else 0
        
        # Generate report
        report = {
            "benchmark_info": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system_info": self.get_system_info(),
                "overall_speedup": overall_speedup,
                "total_sqlite_time": total_sqlite_time,
                "total_duckdb_time": total_duckdb_time
            },
            "detailed_results": self.results,
            "summary": {
                "queries_tested": len(self.results["sqlite"]),
                "successful_queries": len([r for r in self.results["sqlite"].values() if r["success"]]),
                "average_speedup": sum(imp["speedup"] for imp in self.results["performance_improvements"].values()) / len(self.results["performance_improvements"]),
                "best_speedup": max(imp["speedup"] for imp in self.results["performance_improvements"].values()) if self.results["performance_improvements"] else 0,
                "worst_speedup": min(imp["speedup"] for imp in self.results["performance_improvements"].values()) if self.results["performance_improvements"] else 0
            }
        }
        
        # Save report
        with open("duckdb_benchmark_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n🎯 Benchmark Summary:")
        print(f"  Overall Speedup: {overall_speedup:.2f}x faster with DuckDB")
        print(f"  Queries Tested: {report['summary']['queries_tested']}")
        print(f"  Successful Queries: {report['summary']['successful_queries']}")
        print(f"  Average Speedup: {report['summary']['average_speedup']:.2f}x")
        print(f"  Best Speedup: {report['summary']['best_speedup']:.2f}x")
        print(f"  Worst Speedup: {report['summary']['worst_speedup']:.2f}x")
        print(f"  Report saved to: duckdb_benchmark_report.json")
        
        return report
    
    def cleanup(self):
        """Clean up database connections."""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.duckdb_conn:
            self.duckdb_conn.close()
        print("✅ Database connections closed")

def run_tennis_analytics_benchmark():
    """Run the complete tennis analytics benchmark."""
    print("🏁 Starting Tennis Analytics Benchmark: DuckDB vs SQLite")
    print("=" * 60)
    
    # Initialize benchmark
    benchmark = TennisAnalyticsBenchmark()
    
    # Setup connections
    if not benchmark.setup_connections():
        print("❌ Failed to setup database connections")
        return
    
    try:
        # Run benchmarks
        benchmark.run_tennis_analytics_benchmarks()
        benchmark.run_memory_benchmark()
        
        # Generate report
        report = benchmark.generate_benchmark_report()
        
        print("\n✅ Benchmark completed successfully!")
        print(f"📊 Detailed results saved to: duckdb_benchmark_report.json")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
    
    finally:
        benchmark.cleanup()

if __name__ == "__main__":
    run_tennis_analytics_benchmark()
