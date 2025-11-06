"""
Performance metrics aggregation and analysis for AskTennis AI application.
Provides functionality to extract, aggregate, and analyze performance metrics from logs.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from .log_filter import LogFilter


class PerformanceMetrics:
    """
    Performance metrics aggregation and analysis class.
    Extracts execution times from logs and provides aggregation and analysis capabilities.
    """
    
    def __init__(self, log_file_path: Optional[str] = None):
        """Initialize performance metrics analyzer.
        
        Args:
            log_file_path: Path to log file. If None, uses LogFilter to find latest log.
        """
        self.log_filter = LogFilter(log_file_path)
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._extract_metrics()
    
    def _extract_metrics(self):
        """Extract performance metrics from log entries."""
        all_entries = self.log_filter.log_entries
        
        for entry in all_entries:
            section = entry.get("section", "")
            data = entry.get("data", {})
            timestamp = entry.get("timestamp")
            
            # Extract database query execution times
            if section == "DATABASE QUERY":
                execution_time = data.get("execution_time")
                if execution_time is not None:
                    sql_query = data.get("sql_query", "")
                    # Extract operation type from SQL (SELECT, INSERT, etc.)
                    operation_type = self._extract_operation_type(sql_query)
                    component = data.get("component", "unknown")
                    
                    self.metrics["database_queries"].append({
                        "timestamp": timestamp,
                        "execution_time": float(execution_time),
                        "operation_type": operation_type,
                        "component": component,
                        "sql_query": sql_query[:100] if sql_query else "",  # Preview only
                        "result_count": data.get("result_count", "N/A")
                    })
            
            # Extract tool usage execution times
            elif section == "TOOL USAGE":
                execution_time = data.get("execution_time")
                if execution_time is not None:
                    tool_name = data.get("tool_name", "unknown")
                    component = data.get("component", "unknown")
                    
                    self.metrics["tool_usage"].append({
                        "timestamp": timestamp,
                        "execution_time": float(execution_time),
                        "tool_name": tool_name,
                        "component": component
                    })
            
            # Extract final response processing times
            elif section == "FINAL RESPONSE":
                processing_time = data.get("processing_time")
                if processing_time is not None:
                    component = data.get("component", "unknown")
                    
                    self.metrics["response_processing"].append({
                        "timestamp": timestamp,
                        "processing_time": float(processing_time),
                        "component": component
                    })
    
    def _extract_operation_type(self, sql_query: str) -> str:
        """Extract SQL operation type from query.
        
        Args:
            sql_query: SQL query string
            
        Returns:
            Operation type (SELECT, INSERT, UPDATE, DELETE, etc.)
        """
        if not sql_query:
            return "UNKNOWN"
        
        query_upper = sql_query.strip().upper()
        for op in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]:
            if query_upper.startswith(op):
                return op
        return "UNKNOWN"
    
    def get_database_query_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics for database queries.
        
        Returns:
            Dictionary with aggregated statistics
        """
        queries = self.metrics["database_queries"]
        if not queries:
            return {
                "total_queries": 0,
                "average_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "total_time": 0.0
            }
        
        execution_times = [q["execution_time"] for q in queries]
        
        return {
            "total_queries": len(queries),
            "average_time": sum(execution_times) / len(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "total_time": sum(execution_times),
            "operations": self._count_by_field(queries, "operation_type"),
            "components": self._count_by_field(queries, "component")
        }
    
    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics for tool usage.
        
        Returns:
            Dictionary with aggregated statistics
        """
        tools = self.metrics["tool_usage"]
        if not tools:
            return {
                "total_tool_calls": 0,
                "average_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "total_time": 0.0
            }
        
        execution_times = [t["execution_time"] for t in tools]
        
        return {
            "total_tool_calls": len(tools),
            "average_time": sum(execution_times) / len(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "total_time": sum(execution_times),
            "tools": self._aggregate_by_field(tools, "tool_name", "execution_time"),
            "components": self._count_by_field(tools, "component")
        }
    
    def get_response_processing_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics for response processing.
        
        Returns:
            Dictionary with aggregated statistics
        """
        responses = self.metrics["response_processing"]
        if not responses:
            return {
                "total_responses": 0,
                "average_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "total_time": 0.0
            }
        
        processing_times = [r["processing_time"] for r in responses]
        
        return {
            "total_responses": len(responses),
            "average_time": sum(processing_times) / len(processing_times),
            "min_time": min(processing_times),
            "max_time": max(processing_times),
            "total_time": sum(processing_times),
            "components": self._count_by_field(responses, "component")
        }
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics.
        
        Returns:
            Dictionary with overall statistics
        """
        db_stats = self.get_database_query_stats()
        tool_stats = self.get_tool_usage_stats()
        response_stats = self.get_response_processing_stats()
        
        total_time = db_stats["total_time"] + tool_stats["total_time"] + response_stats["total_time"]
        
        return {
            "database_queries": db_stats,
            "tool_usage": tool_stats,
            "response_processing": response_stats,
            "total_processing_time": total_time,
            "metrics_extracted_at": datetime.now().isoformat()
        }
    
    def identify_bottlenecks(self, threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks (operations taking longer than threshold).
        
        Args:
            threshold_seconds: Threshold in seconds for identifying bottlenecks
            
        Returns:
            List of bottleneck entries with details
        """
        bottlenecks = []
        
        # Check database queries
        for query in self.metrics["database_queries"]:
            if query["execution_time"] > threshold_seconds:
                bottlenecks.append({
                    "type": "database_query",
                    "execution_time": query["execution_time"],
                    "operation_type": query["operation_type"],
                    "component": query["component"],
                    "timestamp": query["timestamp"],
                    "details": query.get("sql_query", "")[:100]
                })
        
        # Check tool usage
        for tool in self.metrics["tool_usage"]:
            if tool["execution_time"] > threshold_seconds:
                bottlenecks.append({
                    "type": "tool_usage",
                    "execution_time": tool["execution_time"],
                    "tool_name": tool["tool_name"],
                    "component": tool["component"],
                    "timestamp": tool["timestamp"]
                })
        
        # Check response processing
        for response in self.metrics["response_processing"]:
            if response["processing_time"] > threshold_seconds:
                bottlenecks.append({
                    "type": "response_processing",
                    "execution_time": response["processing_time"],
                    "component": response["component"],
                    "timestamp": response["timestamp"]
                })
        
        # Sort by execution time (descending)
        bottlenecks.sort(key=lambda x: x["execution_time"], reverse=True)
        
        return bottlenecks
    
    def get_trends(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time.
        
        Args:
            time_window_hours: Time window in hours to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        trends = {
            "database_queries": self._get_trends_for_metric(
                self.metrics["database_queries"],
                "execution_time",
                cutoff_time
            ),
            "tool_usage": self._get_trends_for_metric(
                self.metrics["tool_usage"],
                "execution_time",
                cutoff_time
            ),
            "response_processing": self._get_trends_for_metric(
                self.metrics["response_processing"],
                "processing_time",
                cutoff_time
            )
        }
        
        return trends
    
    def _get_trends_for_metric(self, metric_list: List[Dict[str, Any]], 
                               time_field: str, cutoff_time: datetime) -> Dict[str, Any]:
        """Get trends for a specific metric type.
        
        Args:
            metric_list: List of metric entries
            time_field: Field name containing the time value
            cutoff_time: Cutoff time for filtering
            
        Returns:
            Trend analysis dictionary
        """
        # Filter by time window
        recent_metrics = [
            m for m in metric_list
            if self._parse_timestamp(m.get("timestamp")) and 
               self._parse_timestamp(m.get("timestamp")) > cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "count": 0,
                "average_time": 0.0,
                "trend": "insufficient_data"
            }
        
        times = [m[time_field] for m in recent_metrics]
        avg_time = sum(times) / len(times)
        
        # Compare with older metrics
        older_metrics = [
            m for m in metric_list
            if self._parse_timestamp(m.get("timestamp")) and 
               self._parse_timestamp(m.get("timestamp")) <= cutoff_time
        ]
        
        if older_metrics:
            older_times = [m[time_field] for m in older_metrics]
            older_avg = sum(older_times) / len(older_times)
            
            if avg_time > older_avg * 1.1:
                trend = "degrading"
            elif avg_time < older_avg * 0.9:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "count": len(recent_metrics),
            "average_time": avg_time,
            "trend": trend,
            "min_time": min(times),
            "max_time": max(times)
        }
    
    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime object.
        
        Args:
            timestamp_str: Timestamp string in various formats
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not timestamp_str:
            return None
        
        try:
            # Try ISO format first
            if 'T' in timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # Try standard log format: "2025-11-05 16:46:49"
            elif len(timestamp_str) == 19:
                return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def _count_by_field(self, items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
        """Count items by a specific field.
        
        Args:
            items: List of dictionaries
            field: Field name to count by
            
        Returns:
            Dictionary mapping field values to counts
        """
        counts = defaultdict(int)
        for item in items:
            value = item.get(field, "unknown")
            counts[value] += 1
        return dict(counts)
    
    def _aggregate_by_field(self, items: List[Dict[str, Any]], 
                           field: str, value_field: str) -> Dict[str, Dict[str, float]]:
        """Aggregate metrics by a specific field.
        
        Args:
            items: List of dictionaries
            field: Field name to aggregate by
            value_field: Field name containing the value to aggregate
            
        Returns:
            Dictionary mapping field values to aggregated statistics
        """
        aggregated = defaultdict(list)
        
        for item in items:
            key = item.get(field, "unknown")
            value = item.get(value_field, 0.0)
            aggregated[key].append(value)
        
        result = {}
        for key, values in aggregated.items():
            result[key] = {
                "count": len(values),
                "average": sum(values) / len(values) if values else 0.0,
                "min": min(values) if values else 0.0,
                "max": max(values) if values else 0.0,
                "total": sum(values)
            }
        
        return result
    
    def export_metrics_report(self, output_file: str, format: str = "json"):
        """Export performance metrics report to file.
        
        Args:
            output_file: Path to output file
            format: Export format ("json" or "text")
        """
        import json
        
        report = {
            "overall_stats": self.get_overall_stats(),
            "bottlenecks": self.identify_bottlenecks(),
            "trends": self.get_trends(),
            "generated_at": datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == "json":
                json.dump(report, f, indent=2, ensure_ascii=False)
            else:
                # Text format
                f.write("=== PERFORMANCE METRICS REPORT ===\n\n")
                f.write(f"Generated at: {report['generated_at']}\n\n")
                
                # Overall stats
                f.write("--- Overall Statistics ---\n")
                overall = report["overall_stats"]
                f.write(f"Total Processing Time: {overall['total_processing_time']:.2f}s\n\n")
                
                # Database queries
                db_stats = overall["database_queries"]
                f.write("--- Database Queries ---\n")
                f.write(f"Total Queries: {db_stats['total_queries']}\n")
                f.write(f"Average Time: {db_stats['average_time']:.2f}s\n")
                f.write(f"Min Time: {db_stats['min_time']:.2f}s\n")
                f.write(f"Max Time: {db_stats['max_time']:.2f}s\n\n")
                
                # Tool usage
                tool_stats = overall["tool_usage"]
                f.write("--- Tool Usage ---\n")
                f.write(f"Total Tool Calls: {tool_stats['total_tool_calls']}\n")
                f.write(f"Average Time: {tool_stats['average_time']:.2f}s\n")
                f.write(f"Min Time: {tool_stats['min_time']:.2f}s\n")
                f.write(f"Max Time: {tool_stats['max_time']:.2f}s\n\n")
                
                # Response processing
                resp_stats = overall["response_processing"]
                f.write("--- Response Processing ---\n")
                f.write(f"Total Responses: {resp_stats['total_responses']}\n")
                f.write(f"Average Time: {resp_stats['average_time']:.2f}s\n")
                f.write(f"Min Time: {resp_stats['min_time']:.2f}s\n")
                f.write(f"Max Time: {resp_stats['max_time']:.2f}s\n\n")
                
                # Bottlenecks
                bottlenecks = report["bottlenecks"]
                if bottlenecks:
                    f.write(f"--- Bottlenecks (>1.0s) ---\n")
                    for i, bottleneck in enumerate(bottlenecks[:10], 1):  # Top 10
                        f.write(f"{i}. {bottleneck['type']}: {bottleneck['execution_time']:.2f}s\n")
                        f.write(f"   Component: {bottleneck.get('component', 'unknown')}\n")
                        if 'tool_name' in bottleneck:
                            f.write(f"   Tool: {bottleneck['tool_name']}\n")
                        f.write(f"   Timestamp: {bottleneck.get('timestamp', 'N/A')}\n\n")

