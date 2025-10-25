# 🧪 AskTennis AI - Automated Testing Framework

A comprehensive automated testing framework for the AskTennis AI system, designed to validate AI responses against a curated dataset of 100 tennis questions.

## 📋 Overview

This testing framework provides:
- **100 curated tennis Q&A pairs** across 8 categories
- **Automated test execution** with configurable intervals
- **Comprehensive accuracy analysis** using multiple validation methods
- **SQLite database storage** for test results and metrics
- **Detailed reporting** with category and difficulty breakdowns
- **Command-line interface** for easy test execution

## 🏗️ Architecture

```
testing/
├── __init__.py                 # Main testing module
├── test_runner.py              # Main test orchestrator
├── test_executor.py            # Individual test execution
├── result_analyzer.py          # Response analysis & accuracy
├── test_data/
│   ├── tennis_qa_dataset.py    # 100 Q&A test cases
│   └── test_categories.py      # Test categorization
├── database/
│   └── test_db_manager.py      # SQLite database management
└── demo_test.py               # Demo script
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
# Run all 100 tests with 2-second intervals
python run_automated_tests.py --full

# Run 20 quick tests with 1-second intervals
python run_automated_tests.py --quick --num-tests 20 --interval 1

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

## 📈 Accuracy Analysis

The framework uses multiple validation methods:

### 1. **Exact Match**
- Direct string comparison
- Used for: Tournament winners, player names

### 2. **Semantic Similarity**
- Sequence matching algorithm
- Used for: Complex answers, descriptions

### 3. **Numerical Accuracy**
- Percentage-based accuracy for numbers
- Used for: Statistics, rankings, scores

### 4. **Partial Match**
- Keyword overlap analysis
- Used for: Multi-part answers

### 5. **Keyword Match**
- Important term extraction and comparison
- Used for: Technical tennis terms

## 💾 Database Schema

### Test Sessions Table
```sql
CREATE TABLE test_sessions (
    id INTEGER PRIMARY KEY,
    session_name TEXT,
    start_time DATETIME,
    end_time DATETIME,
    total_tests INTEGER,
    passed_tests INTEGER,
    failed_tests INTEGER,
    average_accuracy REAL,
    average_execution_time REAL,
    status TEXT
);
```

### Test Results Table
```sql
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    test_id INTEGER,
    question TEXT,
    generated_sql TEXT,
    ai_answer TEXT,
    expected_answer TEXT,
    accuracy_score REAL,
    execution_time REAL,
    status TEXT,
    category TEXT,
    difficulty TEXT
);
```

## 🔧 Configuration

### Test Intervals
- **Default**: 2 seconds between tests
- **Quick tests**: 1 second intervals
- **Custom**: Specify with `--interval` parameter

### Test Selection
- **Full suite**: All 100 tests
- **Quick tests**: Random subset (default 10)
- **Category tests**: Specific category only
- **Custom subset**: Specify test IDs

## 📊 Reporting

### Basic Metrics
- Total tests executed
- Pass/fail/error counts
- Pass rate percentage
- Average accuracy score
- Average execution time

### Category Analysis
- Performance by test category
- Accuracy breakdown by category
- Execution time by category

### Difficulty Analysis
- Performance by difficulty level
- Accuracy by difficulty
- Recommendations for improvement

## 🎪 Demo

Run the demo script to see the framework in action:

```bash
python testing/demo_test.py
```

The demo includes:
- Test data structure examples
- Quick test execution
- Category-specific testing
- Database operations

## 🛠️ Development

### Adding New Test Cases

1. **Edit the dataset** in `testing/test_data/tennis_qa_dataset.py`
2. **Add test case** with proper structure:
```python
{
    "id": 101,
    "question": "Your new question?",
    "expected_answer": "Expected answer",
    "expected_sql": "SELECT ...",
    "category": TestCategory.YOUR_CATEGORY,
    "difficulty": "easy|medium|hard",
    "keywords": ["keyword1", "keyword2"]
}
```

### Adding New Categories

1. **Update categories** in `testing/test_data/test_categories.py`
2. **Add validation method** if needed
3. **Update category enum** and mappings

### Custom Validation Methods

Add new validation methods in `testing/result_analyzer.py`:

```python
def _custom_validation(self, ai_answer: str, expected_answer: str) -> float:
    """Custom validation logic."""
    # Your validation logic here
    return accuracy_score
```

## 📝 Example Usage

### Python API

```python
from testing.test_runner import TennisTestRunner

# Initialize test runner
runner = TennisTestRunner()

# Run quick test
results = runner.run_quick_test(num_tests=10)

# Run category test
results = runner.run_category_test('tournament_winner')

# Get session results
session_data = runner.get_session_results(session_id=1)

# Export data
json_data = runner.export_session_data(session_id=1, format='json')
```

### Command Line

```bash
# Full test suite with custom interval
python run_automated_tests.py --full --interval 3

# Quick test with more tests
python run_automated_tests.py --quick --num-tests 50

# Export specific session
python run_automated_tests.py --export 5 --output my_results.json
```

## 🔍 Troubleshooting

### Common Issues

1. **Agent initialization fails**
   - Check if the main AskTennis AI system is properly configured
   - Verify database connection and API keys

2. **Tests fail with errors**
   - Check test case format and expected answers
   - Verify SQL query syntax in expected_sql field

3. **Database connection issues**
   - Ensure SQLite is available
   - Check file permissions for database directory

4. **Low accuracy scores**
   - Review expected answers for accuracy
   - Check if AI responses are being parsed correctly
   - Consider adjusting validation thresholds

### Debug Mode

Enable verbose output for debugging:

```bash
python run_automated_tests.py --full --verbose
```

## 📚 API Reference

### TennisTestRunner

Main test orchestrator class.

#### Methods

- `run_automated_tests(interval_seconds, test_subset, progress_callback)`
- `run_quick_test(num_tests)`
- `run_category_test(category, interval_seconds)`
- `get_session_results(session_id)`
- `export_session_data(session_id, format)`
- `list_all_sessions()`

### TestExecutor

Individual test execution engine.

#### Methods

- `execute_single_test(test_case)`
- `batch_execute_tests(test_cases, progress_callback)`

### ResultAnalyzer

Response analysis and accuracy calculation.

#### Methods

- `calculate_accuracy(ai_answer, expected_answer, category)`
- `analyze_test_results(results)`
- `identify_problematic_tests(results)`
- `generate_improvement_suggestions(results)`

## 🤝 Contributing

1. **Add new test cases** to the dataset
2. **Improve validation methods** for better accuracy
3. **Add new test categories** for specialized testing
4. **Enhance reporting** with additional metrics
5. **Optimize performance** for faster execution

## 📄 License

This testing framework is part of the AskTennis AI project and follows the same licensing terms.

---

**🎾 Happy Testing!** 🎾
