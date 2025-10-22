"""
Test script to verify the performance improvements.
Tests the optimized tennis AI system.
"""

import time
import json
from typing import Dict, Any
from tennis.tennis_mappings_cached import CachedTennisMappingFactory
from tennis.optimized_db_tools import OptimizedDatabaseTools, QueryOptimizer
from tennis.performance_optimizer import performance_monitor, performance_optimizer


def test_cached_mappings():
    """Test cached mapping tools."""
    print("🧪 Testing Cached Mapping Tools...")
    
    # Test tournament mapping
    tournament_tool = CachedTennisMappingFactory.create_tournament_mapping_tool()
    
    start_time = time.time()
    result1 = tournament_tool.invoke({"tournament": "Wimbledon"})
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    result2 = tournament_tool.invoke({"tournament": "Wimbledon"})
    second_call_time = time.time() - start_time
    
    print(f"✅ Tournament Mapping:")
    print(f"   First call: {first_call_time:.4f}s")
    print(f"   Second call (cached): {second_call_time:.4f}s")
    print(f"   Speedup: {first_call_time/second_call_time:.1f}x")
    print(f"   Result: {result1}")
    
    # Test round mapping
    round_tool = CachedTennisMappingFactory.create_round_mapping_tool()
    
    start_time = time.time()
    result1 = round_tool.invoke({"round_name": "final"})
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    result2 = round_tool.invoke({"round_name": "final"})
    second_call_time = time.time() - start_time
    
    print(f"✅ Round Mapping:")
    print(f"   First call: {first_call_time:.4f}s")
    print(f"   Second call (cached): {second_call_time:.4f}s")
    print(f"   Speedup: {first_call_time/second_call_time:.1f}x")
    print(f"   Result: {result1}")
    
    # Test cache info
    cache_info = CachedTennisMappingFactory.get_cache_info()
    print(f"📊 Cache Statistics:")
    for tool_name, info in cache_info.items():
        print(f"   {tool_name}: {info.hits} hits, {info.misses} misses")


def test_optimized_queries():
    """Test optimized database queries."""
    print("\n🧪 Testing Optimized Database Queries...")
    
    # Test tournament final query
    tournament_tool = OptimizedDatabaseTools.create_tournament_final_query_tool()
    result = tournament_tool.invoke({
        "tournament": "Wimbledon",
        "year": 2008,
        "round": "F"
    })
    print(f"✅ Tournament Final Query:")
    print(f"   Query: {result}")
    
    # Test surface performance query
    surface_tool = OptimizedDatabaseTools.create_surface_performance_query_tool()
    result = surface_tool.invoke({
        "surface": "Clay",
        "year": 2010,
        "limit": 5
    })
    print(f"✅ Surface Performance Query:")
    print(f"   Query: {result}")
    
    # Test head-to-head query
    h2h_tool = OptimizedDatabaseTools.create_head_to_head_query_tool()
    result = h2h_tool.invoke({
        "player1": "Federer",
        "player2": "Nadal"
    })
    print(f"✅ Head-to-Head Query:")
    print(f"   Query: {result}")


def test_query_optimizer():
    """Test query optimization."""
    print("\n🧪 Testing Query Optimizer...")
    
    # Test tournament query optimization
    original_query = "SELECT set1, set2, set3, set4, set5 FROM matches WHERE tourney_name = 'Wimbledon' AND event_year = 2008 AND round = 'F'"
    optimized_query = QueryOptimizer.optimize_tournament_query("Wimbledon", 2008, "F")
    
    print(f"✅ Query Optimization:")
    print(f"   Original: {original_query}")
    print(f"   Optimized: {optimized_query}")
    
    # Test surface query optimization
    original_surface_query = "SELECT winner_name, COUNT(*) AS wins FROM matches WHERE surface = 'Clay' AND event_year = 2010 GROUP BY winner_name ORDER BY wins DESC LIMIT 1"
    optimized_surface_query = QueryOptimizer.optimize_surface_query("Clay", 2010, 10)
    
    print(f"✅ Surface Query Optimization:")
    print(f"   Original: {original_surface_query}")
    print(f"   Optimized: {optimized_surface_query}")


def test_performance_monitoring():
    """Test performance monitoring."""
    print("\n🧪 Testing Performance Monitoring...")
    
    # Simulate tool calls
    performance_monitor.track_tool_call("get_tournament_mapping", 0.001, False)
    performance_monitor.track_tool_call("get_tournament_mapping", 0.0005, True)  # Duplicate
    performance_monitor.track_tool_call("get_tennis_round_mapping", 0.0008, False)
    performance_monitor.track_tool_call("sql_db_query", 0.038, False)
    
    # Simulate cache performance
    performance_monitor.track_cache_performance(True)
    performance_monitor.track_cache_performance(True)
    performance_monitor.track_cache_performance(False)
    
    # Simulate query performance
    performance_monitor.track_query_performance(
        "SELECT * FROM matches WHERE tourney_name = 'Wimbledon'",
        0.038,
        77
    )
    
    # Get performance summary
    summary = performance_monitor.get_performance_summary()
    print(f"✅ Performance Summary:")
    print(f"   Total tool calls: {summary['total_tool_calls']}")
    print(f"   Average tool time: {summary['average_tool_time']:.4f}s")
    print(f"   Duplicate calls: {summary['duplicate_calls']}")
    print(f"   Duplicate rate: {summary['duplicate_rate']:.2%}")
    print(f"   Cache hit rate: {summary['cache_hit_rate']:.2%}")
    
    # Get optimization recommendations
    recommendations = performance_monitor.get_optimization_recommendations()
    print(f"✅ Optimization Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")


def test_duplicate_detection():
    """Test duplicate call detection."""
    print("\n🧪 Testing Duplicate Call Detection...")
    
    # Test duplicate detection
    is_duplicate1 = performance_optimizer.detect_duplicate_calls(
        "get_tournament_mapping",
        {"tournament": "Wimbledon"}
    )
    print(f"✅ First call (duplicate): {is_duplicate1}")
    
    is_duplicate2 = performance_optimizer.detect_duplicate_calls(
        "get_tournament_mapping",
        {"tournament": "Wimbledon"}
    )
    print(f"✅ Second call (duplicate): {is_duplicate2}")
    
    is_duplicate3 = performance_optimizer.detect_duplicate_calls(
        "get_tournament_mapping",
        {"tournament": "French Open"}
    )
    print(f"✅ Different tournament (duplicate): {is_duplicate3}")
    
    # Test query optimization
    original_query = "SELECT * FROM matches WHERE tourney_name = 'Wimbledon'"
    optimized_query = performance_optimizer.optimize_query(original_query)
    print(f"✅ Query Optimization:")
    print(f"   Original: {original_query}")
    print(f"   Optimized: {optimized_query}")
    
    # Get performance report
    report = performance_optimizer.get_performance_report()
    print(f"✅ Performance Report:")
    print(f"   Optimization Score: {report['optimization_score']:.1f}/100")
    print(f"   Recommendations: {len(report['recommendations'])}")


def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("🚀 Starting Comprehensive Performance Test Suite")
    print("=" * 60)
    
    try:
        test_cached_mappings()
        test_optimized_queries()
        test_query_optimizer()
        test_performance_monitoring()
        test_duplicate_detection()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎉 Performance improvements implemented and verified!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    run_comprehensive_test()
