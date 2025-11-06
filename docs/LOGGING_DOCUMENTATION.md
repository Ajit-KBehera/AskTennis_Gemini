# Tennis Logging System Documentation

## Overview

The tennis logging system provides comprehensive logging capabilities for the AskTennis AI application. It supports structured logging, component tracking, performance metrics, and log filtering.

**Key Features:**
- Global logging enable/disable flag (master switch)
- Structured logging for different event types
- Component tracking for better debugging
- Performance metrics aggregation and analysis
- Log filtering and analysis utilities
- Support for both JSON and text log formats
- Session-based logging with unique session IDs
- Automatic log rotation and cleanup
- Configurable log levels and formats

## Table of Contents

1. [Quick Start](#quick-start)
   - [Basic Usage](#basic-usage)
   - [Enabling/Disabling Logging](#enablingdisabling-logging)
   - [Advanced Usage](#advanced-usage)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Usage Examples](#usage-examples)
5. [Configuration](#configuration)
   - [Environment Variables](#environment-variables)
   - [Global Logging Enable/Disable](#global-logging-enabledisable)
   - [Log Format](#log-format)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Usage

```python
from tennis_logging import setup_logging, log_user_query, log_error

# Initialize logging
logger, log_file = setup_logging()

# Log a user query
log_user_query("Who won Wimbledon 2022?", session_id="abc123", component="query_service")

# Log an error
try:
    result = risky_operation()
except Exception as e:
    log_error(e, "Failed to execute risky operation", component="query_service")
```

### Enabling/Disabling Logging

The logging system includes a global master switch to enable or disable all logging activity:

```python
from tennis_logging import is_logging_enabled, log_user_query

# Check if logging is enabled
if is_logging_enabled():
    print("Logging is active")
    log_user_query("test query")  # Will log
else:
    print("Logging is disabled")
    log_user_query("test query")  # Will NOT log (early return)
```

**Disable logging via environment variable:**
```bash
export LOG_ENABLED=false
streamlit run app_ui.py
```

**Enable logging (default):**
```bash
export LOG_ENABLED=true
# or simply don't set it (defaults to true)
streamlit run app_ui.py
```

### Advanced Usage

```python
from tennis_logging import (
    log_database_query,
    log_tool_usage,
    log_final_response,
    log_llm_interaction,
    get_session_id
)

# Get session ID
session_id = get_session_id()

# Log database query
log_database_query(
    sql_query="SELECT * FROM matches WHERE year = 2022",
    results=[...],
    execution_time=0.5,
    component="database_service"
)

# Log tool usage
log_tool_usage(
    tool_name="sql_db_query",
    tool_input={"query": "SELECT * FROM matches"},
    tool_output=[...],
    execution_time=0.3,
    component="langgraph_builder"
)

# Log LLM interaction
log_llm_interaction(
    messages=[...],
    interaction_type="LLM_CALL",
    component="query_service"
)

# Log final response
log_final_response(
    response="The winner was...",
    processing_time=2.5,
    component="query_service"
)
```

## Architecture

The logging system consists of several key components:

1. **BaseLogger**: Core logging class with structured logging methods
2. **SimplifiedLoggingFactory**: Factory pattern for accessing logging functions
3. **LoggingSetup**: Handles logging configuration and initialization
4. **LogFilter**: Utilities for filtering and analyzing logs
5. **PerformanceMetrics**: Aggregates and analyzes performance metrics

### Component Diagram

```
┌─────────────────┐
│  Application    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SimplifiedFactory│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│BaseLogger│ │LoggingSetup│
└─────────┘ └──────────┘
    │
    ▼
┌─────────┐
│ LogFile │
└─────────┘
```

## Core Components

### BaseLogger

The `BaseLogger` class provides structured logging methods for different event types:

- `log_user_query()`: Log user queries
- `log_llm_interaction()`: Log LLM interactions
- `log_database_query()`: Log database queries
- `log_tool_usage()`: Log tool usage
- `log_final_response()`: Log final responses
- `log_error()`: Log errors with stack traces
- `log_agent_response_parsing()`: Log agent response parsing steps

### SimplifiedLoggingFactory

Provides a simplified interface to logging functionality. Can be used directly or through module-level functions.

### LoggingSetup

Handles logging configuration:
- Session ID management
- Log file creation
- Log level configuration
- Log format configuration (JSON/text)

### LogFilter

Provides utilities for filtering and analyzing logs:
- Filter by section type
- Filter by session ID
- Filter by component
- Filter by date range
- Filter by keyword

### PerformanceMetrics

Aggregates and analyzes performance metrics:
- Database query statistics
- Tool usage statistics
- Response processing statistics
- Bottleneck identification
- Trend analysis

## Usage Examples

### Logging User Queries

```python
from tennis_logging import log_user_query, get_session_id

session_id = get_session_id()
log_user_query(
    query="Who won Wimbledon 2022?",
    session_id=session_id,
    component="query_service"
)
```

### Logging Errors

```python
from tennis_logging import log_error

try:
    result = risky_operation()
except Exception as e:
    log_error(
        error=e,
        context="Failed to process user query",
        component="query_service"
    )
```

### Logging Database Queries

```python
from tennis_logging import log_database_query
import time

start_time = time.time()
results = execute_query("SELECT * FROM matches")
execution_time = time.time() - start_time

log_database_query(
    sql_query="SELECT * FROM matches",
    results=results,
    execution_time=execution_time,
    component="database_service"
)
```

### Logging Tool Usage

```python
from tennis_logging import log_tool_usage
import time

start_time = time.time()
result = tool.invoke(input_data)
execution_time = time.time() - start_time

log_tool_usage(
    tool_name="sql_db_query",
    tool_input=input_data,
    tool_output=result,
    execution_time=execution_time,
    component="langgraph_builder"
)
```

### Filtering Logs

```python
from tennis_logging import LogFilter

# Load logs
filter_obj = LogFilter()

# Filter by section type
errors = filter_obj.filter_by_section(["ERROR"])

# Filter by session
session_logs = filter_obj.filter_by_session("abc123")

# Filter by component
component_logs = filter_obj.filter_by_component("query_service")

# Get statistics
sessions = filter_obj.get_unique_sessions()
components = filter_obj.get_unique_components()
counts = filter_obj.get_section_counts()
```

### Analyzing Performance

```python
from tennis_logging import PerformanceMetrics

# Load metrics
metrics = PerformanceMetrics()

# Get statistics
overall_stats = metrics.get_overall_stats()
db_stats = metrics.get_database_query_stats()
tool_stats = metrics.get_tool_usage_stats()

# Identify bottlenecks
bottlenecks = metrics.identify_bottlenecks(threshold_seconds=1.0)

# Get trends
trends = metrics.get_trends(time_window_hours=24)

# Export report
metrics.export_metrics_report("performance_report.json", format="json")
```

## Configuration

### Environment Variables

The logging system can be configured using environment variables:

- `LOG_ENABLED`: Enable or disable all logging activity (master switch)
  - Default: true (logging enabled)
  - Accepted values: `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off`
  - Example: `export LOG_ENABLED=false` (disables all logging)
  - **Note**: When disabled, no log files are created and all logging calls return immediately

- `LOG_LEVEL`: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Default: INFO
  - Example: `export LOG_LEVEL=DEBUG`

- `LOG_FORMAT`: Set log format (json, text)
  - Default: text
  - Example: `export LOG_FORMAT=json`

- `LOG_MAX_BYTES`: Maximum log file size before rotation (in bytes)
  - Default: 10485760 (10MB)
  - Example: `export LOG_MAX_BYTES=5242880` (5MB)

- `LOG_BACKUP_COUNT`: Number of backup log files to keep
  - Default: 5
  - Example: `export LOG_BACKUP_COUNT=10`

- `LOG_MAX_AGE_DAYS`: Number of days to keep old log files
  - Default: 30
  - Example: `export LOG_MAX_AGE_DAYS=7` (keep logs for 7 days)

### Log Files

Log files are automatically created in the `logs/` directory with the format:
```
logs/asktennis_ai_interaction_{timestamp}_{session_id}.log
```

### Global Logging Enable/Disable

The logging system includes a master switch that can completely disable all logging activity. This is useful for:
- Production environments where logging overhead should be minimized
- Performance testing
- Situations where disk space is limited

**How it works:**
- When `LOG_ENABLED=false`, all logging methods return immediately without any file I/O
- No log files are created when logging is disabled
- All logging calls are no-ops (early return)
- Performance overhead is eliminated

**Usage:**
```bash
# Disable logging
export LOG_ENABLED=false
streamlit run app_ui.py

# Enable logging (default)
export LOG_ENABLED=true
# or unset the variable
unset LOG_ENABLED
streamlit run app_ui.py
```

**Check status programmatically:**
```python
from tennis_logging import is_logging_enabled

if is_logging_enabled():
    # Logging is active
    pass
else:
    # Logging is disabled
    pass
```

### Log Format

#### Text Format (Default)

```
=== USER QUERY START ===
session_id: abc123
query: Who won Wimbledon 2022?
component: query_service
=== USER QUERY END ===
```

#### JSON Format

```json
{"timestamp": "2025-11-05T16:46:49.123456", "section": "USER QUERY", "data": {"session_id": "abc123", "query": "Who won Wimbledon 2022?", "component": "query_service"}}
```

## API Reference

### Module-Level Functions

#### `setup_logging() -> Tuple[logging.Logger, str]`

Initialize logging system and return logger instance and log file path.

**Returns:**
- `Tuple[logging.Logger, str]`: Logger instance and log file path

#### `log_user_query(query: str, session_id: Optional[str] = None, component: Optional[str] = None) -> None`

Log a user query.

**Parameters:**
- `query`: The user's query string
- `session_id`: Session ID for tracking (optional)
- `component`: Component/module name (optional)

#### `log_llm_interaction(messages: List[Any], interaction_type: str = "LLM_CALL", component: Optional[str] = None) -> None`

Log LLM interactions.

**Parameters:**
- `messages`: List of messages in the interaction
- `interaction_type`: Type of interaction (default: "LLM_CALL")
- `component`: Component/module name (optional)

#### `log_database_query(sql_query: str, results: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None`

Log database queries.

**Parameters:**
- `sql_query`: The SQL query string
- `results`: Query results
- `execution_time`: Execution time in seconds (optional)
- `component`: Component/module name (optional)

#### `log_tool_usage(tool_name: str, tool_input: Any, tool_output: Any, execution_time: Optional[float] = None, component: Optional[str] = None) -> None`

Log tool usage.

**Parameters:**
- `tool_name`: Name of the tool being used
- `tool_input`: Input to the tool
- `tool_output`: Output from the tool
- `execution_time`: Execution time in seconds (optional)
- `component`: Component/module name (optional)

#### `log_final_response(response: str, processing_time: Optional[float] = None, component: Optional[str] = None) -> None`

Log final responses.

**Parameters:**
- `response`: The final response text
- `processing_time`: Total processing time in seconds (optional)
- `component`: Component/module name (optional)

#### `log_error(error: Exception, context: str = "", component: Optional[str] = None) -> None`

Log errors with full context and stack trace.

**Parameters:**
- `error`: The exception that was raised
- `context`: Additional context about where/why the error occurred
- `component`: Component/module name (optional)

#### `log_agent_response_parsing(step: str, message_type: Optional[str] = None, content_preview: Optional[str] = None, details: Optional[Dict[str, Any]] = None, component: Optional[str] = None) -> None`

Log agent response parsing steps.

**Parameters:**
- `step`: The parsing step
- `message_type`: Type of message being parsed (optional)
- `content_preview`: Preview of content (optional, limited to 200 chars)
- `details`: Additional details dict (optional)
- `component`: Component/module name (optional)

#### `get_session_id() -> str`

Get the current session ID, creating one if it doesn't exist.

**Returns:**
- `str`: The session ID (8-character UUID)

#### `is_logging_enabled() -> bool`

Check if logging is globally enabled or disabled.

**Returns:**
- `bool`: True if logging is enabled, False if disabled

**Example:**
```python
from tennis_logging import is_logging_enabled

if is_logging_enabled():
    print("Logging is active")
else:
    print("Logging is disabled")
```

### Classes

#### `BaseLogger`

Core logging class with structured logging methods.

**Methods:**
- `log_user_query()`
- `log_llm_interaction()`
- `log_database_query()`
- `log_tool_usage()`
- `log_final_response()`
- `log_error()`
- `log_agent_response_parsing()`
- `get_logger()`

#### `SimplifiedLoggingFactory`

Factory pattern for accessing logging functionality.

**Methods:**
- `setup_logging()`
- All logging methods (same as module-level functions)

#### `LoggingSetup`

Handles logging configuration and initialization.

**Methods:**
- `setup_logging()`
- `get_logger()`
- `get_log_file()`
- `is_initialized()`
- `get_session_id()`
- `get_log_level()`
- `get_log_format()`

#### `LogFilter`

Utilities for filtering and analyzing logs.

**Methods:**
- `filter_by_section()`
- `filter_by_session()`
- `filter_by_component()`
- `filter_by_date_range()`
- `filter_by_keyword()`
- `get_unique_sessions()`
- `get_unique_components()`
- `get_section_counts()`
- `get_errors_summary()`
- `export_filtered()`

#### `PerformanceMetrics`

Aggregates and analyzes performance metrics.

**Methods:**
- `get_database_query_stats()`
- `get_tool_usage_stats()`
- `get_response_processing_stats()`
- `get_overall_stats()`
- `identify_bottlenecks()`
- `get_trends()`
- `export_metrics_report()`

## Best Practices

### 1. Use Global Logging Flag for Production

```python
# Check logging status before expensive operations
from tennis_logging import is_logging_enabled

if is_logging_enabled():
    # Only prepare logging data if logging is enabled
    detailed_data = prepare_detailed_log_data()
    log_database_query(query, detailed_data, component="db_service")
else:
    # Skip logging overhead when disabled
    execute_query(query)
```

### 2. Always Include Component Information

```python
# Good
log_user_query(query, session_id, component="query_service")

# Bad
log_user_query(query, session_id)
```

### 3. Use Session IDs Consistently

```python
# Good
session_id = get_session_id()
log_user_query(query, session_id, component="query_service")
config = {"configurable": {"thread_id": session_id}}

# Bad
log_user_query(query, "hardcoded_session", component="query_service")
```

### 4. Include Execution Times When Available

```python
# Good
start_time = time.time()
result = execute_operation()
execution_time = time.time() - start_time
log_database_query(query, result, execution_time, component="db_service")

# Bad
result = execute_operation()
log_database_query(query, result, component="db_service")
```

### 5. Provide Context for Errors

```python
# Good
try:
    result = risky_operation()
except Exception as e:
    log_error(e, "Failed to process user query: query_text", component="query_service")

# Bad
try:
    result = risky_operation()
except Exception as e:
    log_error(e)
```

### 6. Use Appropriate Log Levels

- Use `log_error()` for exceptions
- Use other logging methods for normal operations
- Don't log sensitive information

### 7. Filter Logs for Analysis

```python
# Filter errors from specific component
filter_obj = LogFilter()
errors = filter_obj.filter_by_section(["ERROR"])
component_errors = [e for e in errors if e.get("data", {}).get("component") == "query_service"]
```

### 8. Monitor Performance Metrics

```python
# Regularly check for bottlenecks
metrics = PerformanceMetrics()
bottlenecks = metrics.identify_bottlenecks(threshold_seconds=1.0)
if bottlenecks:
    print(f"Found {len(bottlenecks)} bottlenecks")
```

### 9. Disable Logging in Production (Optional)

For production environments where logging overhead should be minimized:

```bash
# In production environment
export LOG_ENABLED=false
streamlit run app_ui.py
```

This eliminates all logging overhead including:
- File I/O operations
- String formatting
- JSON serialization
- Disk space usage

## Troubleshooting

### Logs Not Appearing

1. **Check if logging is enabled:**
   ```python
   from tennis_logging import is_logging_enabled
   print(f"Logging enabled: {is_logging_enabled()}")
   ```
   If `False`, check `LOG_ENABLED` environment variable

2. Check that `setup_logging()` has been called
3. Verify log file exists in `logs/` directory
4. Check log level configuration (may be filtering out logs)

### Performance Issues

1. Consider disabling logging in production:
   ```bash
   export LOG_ENABLED=false
   ```
2. Use `PerformanceMetrics` to identify bottlenecks
3. Check execution times for database queries
4. Monitor tool usage statistics

### Session ID Issues

1. Always use `get_session_id()` instead of hardcoding
2. Verify session ID is consistent across operations
3. Check session state is properly initialized

### Logging Disabled When Expected

1. Check `LOG_ENABLED` environment variable:
   ```bash
   echo $LOG_ENABLED
   ```
2. Verify it's not set to `false`, `0`, `no`, or `off`
3. Use `is_logging_enabled()` to check programmatically:
   ```python
   from tennis_logging import is_logging_enabled
   if not is_logging_enabled():
       print("Logging is disabled. Set LOG_ENABLED=true to enable.")
   ```

## Additional Resources

- See `docs/09_Logging_Analysis.md` for detailed analysis
- See `testing/test_logging.py` for test examples
- Check log files in `logs/` directory for examples

