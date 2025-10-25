# 🧪 AskTennis AI - Simplified Testing Framework

A streamlined automated testing framework for the AskTennis AI system, designed to generate and capture AI responses for 100 curated tennis questions.

## 📋 Overview

This simplified testing framework provides:
- **100 curated tennis questions** across 8 categories
- **Automated test execution** with configurable intervals
- **AI response capture** (SQL queries and answers)
- **SQLite database storage** for test results and sessions
- **Basic performance metrics** and execution tracking
- **Command-line interface** for easy test execution

## 🏗️ Architecture

```
testing/
├── __init__.py                 # Main testing module
├── test_runner.py              # Main test orchestrator
├── test_executor.py            # Individual test execution
├── result_analyzer.py          # Basic result analysis
├── test_data/
│   ├── tennis_qa_dataset.py    # 100 Q&A test cases
│   └── test_categories.py      # Test categorization
├── database/
│   └── test_db_manager.py      # SQLite database management
├── README.md                   # This documentation
└── requirements.txt            # Dependencies
```

## 🚀 Quick Start

### 1. Run a Quick Test
```bash
python run_automated_tests.py --quick --num-tests 5
```

### 2. Run Full Test Suite
```bash
python run_automated_tests.py --full
```

### 3. Run Category-Specific Tests
```bash
python run_automated_tests.py --category tournament_winner
```

### 4. Run with Custom Interval (minimum 30 seconds)
```bash
python run_automated_tests.py --full --interval 60
```

### 5. List Available Categories
```bash
python run_automated_tests.py --categories
```

## 📊 Test Categories

The framework includes 100 test cases across 8 categories:

| Category | Count | Description |
|----------|-------|-------------|
| **Tournament Winner** | 20 | Questions about tournament champions |
| **Head-to-Head** | 15 | Player vs player records |
| **Surface Performance** | 15 | Performance on different surfaces |
| **Statistical Analysis** | 15 | Numerical and statistical queries |
| **Historical Records** | 10 | Historical achievements and records |
| **Player Rankings** | 10 | Ranking positions and history |
| **Match Details** | 10 | Specific match information |
| **Complex Queries** | 5 | Multi-part analytical questions |

## 🎯 Test Execution

### Basic Commands

```bash
# Run all 100 tests with 30-second intervals
python run_automated_tests.py --full

# Run 20 quick tests with 30-second intervals
python run_automated_tests.py --quick --num-tests 20

# Run tournament winner tests only
python run_automated_tests.py --category tournament_winner

# Show available test categories
python run_automated_tests.py --categories
```

### Session Management

```bash
# List all test sessions
python run_automated_tests.py --list-sessions

# Export session data to JSON
python run_automated_tests.py --export 1 --output results.json

# Export session data to CSV
python run_automated_tests.py --export 1 --format csv --output results.csv
```

## 🔧 Framework Components

### Core Components

#### **TennisTestRunner** (`test_runner.py`)
- Main orchestrator for test execution
- Manages test sessions and intervals
- Handles test subset selection
- Provides progress tracking and reporting

#### **TestExecutor** (`test_executor.py`)
- Executes individual test cases
- Sends questions to LangGraph agent
- Extracts SQL queries and AI answers
- Handles execution timing and error management

#### **ResultAnalyzer** (`result_analyzer.py`)
- Provides basic execution metrics
- Generates category and difficulty breakdowns
- Creates summary reports
- Tracks performance statistics

#### **TestDatabaseManager** (`database/test_db_manager.py`)
- Manages SQLite database operations
- Stores test sessions and results
- Handles session lifecycle management
- Provides querying capabilities

### Test Data

#### **Tennis Q&A Dataset** (`test_data/tennis_qa_dataset.py`)
- Contains 100 curated tennis questions
- Includes categories, difficulty levels, and keywords
- Simplified structure without expected answers

#### **Test Categories** (`test_data/test_categories.py`)
- Defines 8 test categories
- Provides category metadata and descriptions
- Manages test classification system

## 📊 Database Schema

### Test Sessions Table
```sql
CREATE TABLE test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    total_tests INTEGER DEFAULT 0,
    completed_tests INTEGER DEFAULT 0,
    error_tests INTEGER DEFAULT 0,
    average_execution_time REAL DEFAULT 0.0,
    status TEXT DEFAULT 'running'
);
```

### Test Results Table
```sql
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    test_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    generated_sql TEXT,
    ai_answer TEXT,
    execution_time REAL DEFAULT 0.0,
    test_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    category TEXT,
    difficulty TEXT,
    FOREIGN KEY (session_id) REFERENCES test_sessions (id)
);
```

## 🎯 What This Framework Does

### ✅ Captures:
- **AI Generated SQL** - SQL queries produced by the AI
- **AI Answers** - Natural language responses from the AI
- **Execution Times** - How long each test takes
- **Test Metadata** - Category, difficulty, question ID
- **Error Information** - Any errors during execution

### ✅ Provides:
- **Basic Metrics** - Total tests, completion rates, execution times
- **Category Breakdown** - Results by test category
- **Difficulty Analysis** - Performance by difficulty level
- **Session Management** - Track multiple test runs
- **Data Export** - JSON/CSV export capabilities

## 🚫 What This Framework Does NOT Do

### ❌ Removed Components:
- **Accuracy Calculation** - No comparison with expected answers
- **Status Determination** - No pass/fail evaluation
- **Confidence Scoring** - No confidence metrics
- **Complex Analysis** - No detailed result evaluation
- **Expected Answer Validation** - No correctness checking

## 🔧 Usage Examples

### Python API Usage

```python
from testing.test_runner import TennisTestRunner

# Initialize test runner
runner = TennisTestRunner()

# Run specific test questions
result = runner.run_automated_tests(
    test_subset=[1, 2, 3, 4, 5],
    interval_seconds=30
)

# Run all tests
result = runner.run_automated_tests(interval_seconds=60)

# Run category-specific tests
result = runner.run_category_test("tournament_winner", interval_seconds=30)
```

### Command Line Usage

```bash
# Run tests 80-100 with 60-second intervals
python -c "
from testing.test_runner import TennisTestRunner
runner = TennisTestRunner()
result = runner.run_automated_tests(test_subset=list(range(80, 101)), interval_seconds=60)
print('Completed!')
"
```

## 📈 Performance Metrics

The framework tracks:
- **Execution Time** - How long each test takes
- **Completion Rate** - Percentage of successful tests
- **Error Rate** - Percentage of failed tests
- **Category Performance** - Results by test category
- **Difficulty Analysis** - Performance by difficulty level

## 🛠️ Requirements

- Python 3.8+
- SQLite3 (built-in)
- AskTennis AI system components
- LangGraph agent setup

## 📝 Notes

This is a **simplified testing framework** focused purely on:
1. **Generating AI responses** to tennis questions
2. **Capturing SQL queries** and answers
3. **Tracking basic performance** metrics
4. **Storing results** in database

The framework does **NOT** evaluate correctness or accuracy - it simply captures what the AI produces for analysis and review.