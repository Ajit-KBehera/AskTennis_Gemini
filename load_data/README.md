# AskTennis Modular Data Loading System

A comprehensive, modular data loading system for tennis data that replaces the original monolithic `load_data.py` with a clean, maintainable architecture.

## 📁 Project Structure

```
load_data/
├── __init__.py                    # Package initialization and exports
├── load_data.py                   # Original monolithic file (preserved)
├── load_data_main_tour_singles_open_era.py  # Original specialized file (preserved)
├── load_data_new.py               # New modular implementation
├── config/                        # Configuration management
│   ├── __init__.py
│   ├── settings.py               # Configuration constants
│   └── paths.py                  # File path management
├── core/                         # Core orchestration classes
│   ├── __init__.py
│   ├── data_loader.py            # Main orchestration class
│   └── progress_tracker.py       # Progress tracking utilities
├── loaders/                      # Data loading classes
│   ├── __init__.py
│   ├── players_loader.py         # ATP/WTA players loading
│   ├── rankings_loader.py        # Rankings data loading
│   ├── matches_loader.py         # Match data loading
│   └── doubles_loader.py         # Doubles data loading
├── processors/                    # Data processing classes
│   ├── __init__.py
│   ├── date_processor.py         # Date component parsing
│   ├── score_processor.py        # Score parsing into sets
│   ├── surface_processor.py      # Surface data inference
│   └── level_processor.py        # Tournament level standardization
└── database/                     # Database operations
    ├── __init__.py
    ├── creator.py                # Database creation and population
    ├── verifier.py               # Database verification and analysis
    └── manager.py                # Database management utilities
```

## 🚀 Quick Start

### Creating a Database File

#### Method 1: Using the New Modular System (Recommended)

```python
from load_data import DataLoader

# Initialize the data loader
loader = DataLoader(verbose=True)

# Load all data and create database
results = loader.load_all_data(recent_only=False)

# Process and create database
processed_matches = loader._process_matches_data()
processed_doubles = loader._process_doubles_data()
loader._create_database()
loader._verify_database()
```

#### Method 2: Using the New Implementation File

```bash
# Run the complete data loading process
python load_data_new.py

# Choose option 1 for full data loading
```

#### Method 3: Using Individual Components

```python
from load_data import (
    PlayersLoader, RankingsLoader, MatchesLoader, DoublesLoader,
    DateProcessor, ScoreProcessor, SurfaceProcessor, LevelProcessor,
    DatabaseCreator, DatabaseVerifier
)

# Load data
players_loader = PlayersLoader(verbose=True)
players_df = players_loader.load_all_players()

rankings_loader = RankingsLoader(verbose=True)
rankings_df = rankings_loader.load_all_rankings()

matches_loader = MatchesLoader(verbose=True)
matches_df = matches_loader.load_all_matches([2020, 2021, 2022])

# Process data
surface_processor = SurfaceProcessor(verbose=True)
processed_matches = surface_processor.fix_missing_surface_data(matches_df)

date_processor = DateProcessor(verbose=True)
processed_matches = date_processor.parse_date_components(processed_matches)

score_processor = ScoreProcessor(verbose=True)
processed_matches = score_processor.parse_score_data(processed_matches)

level_processor = LevelProcessor(verbose=True)
processed_matches = level_processor.standardize_tourney_levels(processed_matches, 'Mixed')

# Create database
creator = DatabaseCreator(verbose=True)
success = creator.create_database_with_players(
    players_df=players_df,
    rankings_df=rankings_df,
    matches_df=processed_matches,
    doubles_df=pd.DataFrame()  # Add doubles data if available
)

# Verify database
verifier = DatabaseVerifier(verbose=True)
verification_results = verifier.verify_enhancement()
```

## 📚 Detailed Documentation

### Package Initialization (`__init__.py`)

**Purpose**: Main package entry point that exports all modular components.

**Exports**:
- `DataLoader`: Main orchestration class
- `ProgressTracker`: Progress tracking utilities
- `DataPaths`: File path management
- `YEARS`, `RECENT_YEARS`, `LOAD_RECENT_ONLY`: Configuration constants
- All loader classes: `PlayersLoader`, `RankingsLoader`, `MatchesLoader`, `DoublesLoader`
- All processor classes: `DateProcessor`, `ScoreProcessor`, `SurfaceProcessor`, `LevelProcessor`
- All database classes: `DatabaseCreator`, `DatabaseVerifier`, `DatabaseManager`

### Configuration Module (`config/`)

#### `config/settings.py`
**Purpose**: Centralized configuration constants.

**Constants**:
- `PROJECT_ROOT`: Project root directory path
- `DATA_DIRS`: List of data directories (ATP and WTA)
- `YEARS`: Complete year range (1968-2025)
- `RECENT_YEARS`: Recent years for testing (2020-2025)
- `LOAD_RECENT_ONLY`: Flag to load only recent years
- `DB_FILE`: Main database file path
- `BATCH_SIZE`: Database insert batch size
- `PROGRESS_DISPLAY_INTERVAL`: Progress update interval
- `VERBOSE_LOGGING`: Enable/disable verbose output

#### `config/paths.py`
**Purpose**: File path management and utilities.

**Class**: `DataPaths`

**Methods**:
- `project_root`: Get project root directory
- `data_dirs`: Get list of data directories
- `tennis_atp_dir`: Get ATP data directory path
- `tennis_wta_dir`: Get WTA data directory path
- `main_database_file`: Get main database file path
- `atp_players_file`: Get ATP players file path
- `wta_players_file`: Get WTA players file path
- `get_atp_ranking_files()`: Get list of ATP ranking files
- `get_wta_ranking_files()`: Get list of WTA ranking files
- `get_all_ranking_files()`: Get all ranking files
- `get_match_files_for_year(year, tour)`: Get match files for specific year/tour
- `get_amateur_match_file()`: Get amateur matches file path
- `get_atp_qual_files()`: Get ATP qualifying files
- `get_wta_qual_files()`: Get WTA qualifying files
- `get_atp_challenger_files()`: Get ATP Challenger files
- `get_wta_challenger_files()`: Get WTA Challenger files
- `get_atp_futures_files()`: Get ATP Futures files
- `get_wta_futures_files()`: Get WTA Futures files
- `get_fed_cup_files()`: Get Fed Cup files
- `get_doubles_files()`: Get doubles files
- `file_exists(file_path)`: Check if file exists
- `dir_exists(dir_path)`: Check if directory exists
- `get_file_size(file_path)`: Get file size in bytes

### Core Module (`core/`)

#### `core/progress_tracker.py`
**Purpose**: Progress tracking with time estimates and status updates.

**Class**: `ProgressTracker`

**Methods**:
- `__init__(total_steps, step_name="Loading", verbose=True)`: Initialize tracker
- `update(step_increment=1, message="")`: Update progress
- `complete(message="")`: Mark as complete
- `percentage`: Property - current progress percentage
- `elapsed_time`: Property - elapsed time in seconds
- `estimated_total_time`: Property - estimated total time
- `estimated_remaining_time`: Property - estimated remaining time

#### `core/data_loader.py`
**Purpose**: Main orchestration class that coordinates the entire data loading process.

**Class**: `DataLoader`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize data loader
- `load_all_data(recent_only=None)`: Load all tennis data
- `_load_players_data()`: Load player data using PlayersLoader
- `_load_rankings_data(years)`: Load rankings data using RankingsLoader
- `_load_matches_data(years)`: Load match data using MatchesLoader
- `_load_doubles_data(years)`: Load doubles data using DoublesLoader
- `_process_matches_data()`: Process match data using all processors
- `_process_doubles_data()`: Process doubles data using all processors
- `_create_database()`: Create database using DatabaseCreator
- `_verify_database()`: Verify database using DatabaseVerifier
- `_get_results_summary()`: Get summary of loaded data

### Loaders Module (`loaders/`)

#### `loaders/players_loader.py`
**Purpose**: Load and process ATP and WTA player data.

**Class**: `PlayersLoader`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize loader
- `load_all_players()`: Load and combine ATP and WTA player data
- `_load_atp_players()`: Load ATP player data
- `_load_wta_players()`: Load WTA player data
- `search_players(df, search_term)`: Search players by name
- `get_player_stats(df, player_id)`: Get player statistics

#### `loaders/rankings_loader.py`
**Purpose**: Load and process ATP and WTA ranking data.

**Class**: `RankingsLoader`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize loader
- `load_all_rankings()`: Load and combine all rankings data
- `get_rankings_by_year(df, year)`: Filter rankings by year
- `get_top_rankings(df, date=None, top_n=10)`: Get top N ranked players

#### `loaders/matches_loader.py`
**Purpose**: Load and process various types of tennis match data.

**Class**: `MatchesLoader`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize loader
- `load_all_matches(years)`: Load all types of match data
- `_load_main_tour_matches(years)`: Load main tour ATP and WTA matches
- `_load_amateur_matches()`: Load amateur tennis data (pre-Open Era)
- `_load_other_tour_matches(years)`: Load qualifying, challenger, futures, Fed Cup data
- `_filter_files_by_years(files, years)`: Filter files by year range
- `get_matches_by_player(df, player_id)`: Filter matches by player
- `get_matches_stats(df)`: Get match statistics

#### `loaders/doubles_loader.py`
**Purpose**: Load and process ATP doubles match data.

**Class**: `DoublesLoader`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize loader
- `load_all_doubles()`: Load and combine all doubles data
- `get_doubles_matches_by_player(df, player_id)`: Filter doubles by player
- `get_doubles_matches_by_year(df, year)`: Filter doubles by year
- `get_doubles_stats(df)`: Get doubles statistics

### Processors Module (`processors/`)

#### `processors/date_processor.py`
**Purpose**: Process date data by parsing tournament dates into components.

**Class**: `DateProcessor`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize processor
- `parse_date_components(df)`: Parse tourney_date into year, month, day
- `validate_dates(df)`: Validate date data and return statistics
- `filter_by_year(df, year)`: Filter DataFrame by year
- `filter_by_year_range(df, start_year, end_year)`: Filter by year range
- `filter_by_month(df, month)`: Filter by month
- `get_season_stats(df)`: Get statistics by season
- `get_monthly_stats(df)`: Get monthly statistics

#### `processors/score_processor.py`
**Purpose**: Process score data by parsing tennis match scores into individual sets.

**Class**: `ScoreProcessor`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize processor
- `parse_score_data(df)`: Parse score column into set1-set5 columns
- `validate_scores(df)`: Validate score data and return statistics
- `get_set_statistics(df)`: Get statistics about sets played
- `filter_by_match_length(df, min_sets=None, max_sets=None)`: Filter by match length
- `_parse_score(score_str)`: Parse single score string
- `_parse_walkover_score(score_str)`: Parse walkover score
- `_parse_default_score(score_str)`: Parse default score
- `_parse_retirement_score(score_str)`: Parse retirement score

#### `processors/surface_processor.py`
**Purpose**: Process surface data by fixing missing surface information.

**Class**: `SurfaceProcessor`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize processor
- `fix_missing_surface_data(matches_df)`: Fix missing surface data
- `get_surface_statistics(df)`: Get surface distribution statistics
- `get_surface_by_era(df)`: Get surface distribution by era
- `get_surface_by_year(df, year)`: Get surface distribution for year
- `filter_by_surface(df, surface)`: Filter matches by surface
- `validate_surface_data(df)`: Validate surface data
- `get_most_common_surface(df)`: Get most common surface type
- `_infer_surface(row)`: Infer surface from tournament name and date

#### `processors/level_processor.py`
**Purpose**: Process tournament level data by standardizing levels across tours.

**Class**: `LevelProcessor`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize processor
- `standardize_tourney_levels(df, tour_name)`: Standardize tournament levels
- `get_level_statistics(df)`: Get tournament level distribution
- `get_level_by_tour(df)`: Get level distribution by tour
- `get_level_by_year(df, year)`: Get level distribution for year
- `filter_by_level(df, level)`: Filter by tournament level
- `filter_by_levels(df, levels)`: Filter by multiple levels
- `validate_level_data(df)`: Validate tournament level data
- `get_most_common_level(df)`: Get most common tournament level
- `get_level_hierarchy(df)`: Get level hierarchy by frequency

### Database Module (`database/`)

#### `database/creator.py`
**Purpose**: Create and populate SQLite database with tennis data.

**Class**: `DatabaseCreator`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize creator
- `create_database_with_players(players_df, rankings_df, matches_df, doubles_df, database_file=None)`: Create complete database
- `_create_tables(conn, players_df, rankings_df, matches_df, doubles_df)`: Create database tables
- `_create_indexes(conn, rankings_df, doubles_df)`: Create performance indexes
- `_create_views(conn, rankings_df)`: Create database views
- `get_database_info(database_file=None)`: Get database information

#### `database/verifier.py`
**Purpose**: Verify database integrity and data completeness.

**Class**: `DatabaseVerifier`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize verifier
- `verify_enhancement(database_file=None)`: Verify complete data integration
- `get_database_statistics(database_file=None)`: Get comprehensive statistics
- `_check_tables_exist(conn)`: Check if required tables exist
- `_get_data_counts(conn)`: Get data counts for each table
- `_get_historical_coverage(conn)`: Get historical coverage information
- `_get_era_distribution(conn)`: Get era distribution
- `_get_tournament_type_distribution(conn)`: Get tournament type distribution
- `_get_tourney_level_distribution(conn)`: Get tournament level distribution
- `_get_decade_distribution(conn)`: Get decade distribution
- `_check_player_match_integration(conn)`: Check player-match integration
- `_assess_data_quality(conn)`: Assess overall data quality
- `_print_verification_summary(results)`: Print verification summary

#### `database/manager.py`
**Purpose**: Manage database operations and provide utility functions.

**Class**: `DatabaseManager`

**Methods**:
- `__init__(verbose=VERBOSE_LOGGING)`: Initialize manager
- `connect(database_file=None)`: Create database connection
- `execute_query(query, database_file=None)`: Execute SQL query
- `execute_query_to_dataframe(query, database_file=None)`: Execute query to DataFrame
- `get_table_schema(table_name, database_file=None)`: Get table schema
- `get_all_tables(database_file=None)`: Get list of all tables
- `get_table_row_count(table_name, database_file=None)`: Get row count for table
- `backup_database(backup_file, database_file=None)`: Create database backup
- `restore_database(backup_file, database_file=None)`: Restore from backup
- `optimize_database(database_file=None)`: Optimize database (VACUUM, ANALYZE)
- `get_database_size(database_file=None)`: Get database file size
- `check_database_integrity(database_file=None)`: Check database integrity

### Implementation Files

#### `load_data_new.py`
**Purpose**: New modular implementation that replicates original functionality.

**Functions**:
- `main()`: Main orchestration function
- `load_players_data()`: Load player data (modular)
- `load_rankings_data()`: Load rankings data (modular)
- `load_matches_data()`: Load match data (modular)
- `load_doubles_data()`: Load doubles data (modular)
- `parse_date_components(df)`: Parse date components (modular)
- `parse_score_data(df)`: Parse score data (modular)
- `fix_missing_surface_data(df)`: Fix surface data (modular)
- `standardize_tourney_levels(df, tour_name)`: Standardize levels (modular)
- `create_database_with_players()`: Create database (modular)
- `verify_enhancement()`: Verify database (modular)
- `demonstrate_modular_usage()`: Demonstrate component usage
- `print_final_summary(verification_results)`: Print final summary

## 🗄️ Database Schema

The system creates a SQLite database with the following tables:

### Tables
- **`players`**: Player information (ATP and WTA)
- **`rankings`**: Historical rankings data
- **`matches`**: Match results with processed data
- **`doubles_matches`**: Doubles match results

### Views
- **`matches_with_winner_info`**: Matches with winner player details
- **`matches_with_loser_info`**: Matches with loser player details
- **`matches_with_full_info`**: Matches with both winner and loser details
- **`matches_with_rankings`**: Matches with ranking information at time of match

### Indexes
- Performance indexes on frequently queried columns
- Player ID indexes for fast lookups
- Date indexes for temporal queries
- Surface and level indexes for filtering

## 🔧 Configuration

### Environment Variables
- `VERBOSE_LOGGING`: Enable/disable verbose output
- `LOAD_RECENT_ONLY`: Load only recent years for testing

### File Paths
- Data directories: `data/tennis_atp/` and `data/tennis_wta/`
- Database file: `tennis_data.db` (in project root)
- Configuration: `config/settings.py`

## 📊 Data Sources

The system loads data from CSV files in the following structure:
```
data/
├── tennis_atp/
│   ├── atp_players.csv
│   ├── atp_rankings_*.csv
│   ├── atp_matches_*.csv
│   └── atp_matches_doubles_*.csv
└── tennis_wta/
    ├── wta_players.csv
    ├── wta_rankings_*.csv
    └── wta_matches_*.csv
```

## 🚀 Performance Features

- **Batch processing**: Efficient database inserts
- **Progress tracking**: Real-time progress monitoring
- **Indexing**: Optimized database queries
- **Memory management**: Efficient data processing
- **Error handling**: Robust error recovery

## 🧪 Testing

The system includes comprehensive testing capabilities:
- Individual component testing
- Integration testing
- Data validation
- Database integrity checks
- Performance monitoring

## 📈 Monitoring

- **Progress tracking**: Real-time progress updates
- **Statistics**: Comprehensive data statistics
- **Verification**: Data integrity verification
- **Quality assessment**: Data completeness analysis

## 🔄 Migration Guide

### From Original `load_data.py`

1. **Immediate replacement**: Use `load_data_new.py` as drop-in replacement
2. **Gradual adoption**: Use individual modular components
3. **Full integration**: Integrate with existing applications

### Benefits of Migration

- **Better maintainability**: Modular architecture
- **Easier testing**: Individual component testing
- **Better performance**: Optimized processing
- **Future-proof**: Extensible design
- **Professional quality**: Production-ready code

## 📝 Examples

### Basic Usage
```python
from load_data import DataLoader

loader = DataLoader(verbose=True)
results = loader.load_all_data()
```

### Advanced Usage
```python
from load_data import (
    PlayersLoader, DateProcessor, DatabaseCreator
)

# Load and process data
players_loader = PlayersLoader(verbose=True)
players_df = players_loader.load_all_players()

date_processor = DateProcessor(verbose=True)
processed_df = date_processor.parse_date_components(some_df)

# Create database
creator = DatabaseCreator(verbose=True)
success = creator.create_database_with_players(
    players_df=players_df,
    rankings_df=pd.DataFrame(),
    matches_df=pd.DataFrame(),
    doubles_df=pd.DataFrame()
)
```

## 🤝 Contributing

The modular architecture makes it easy to:
- Add new data loaders
- Add new processors
- Extend database operations
- Add new features
- Improve performance

## 📄 License

This project is part of the AskTennis AI system and follows the same licensing terms.

---

**Note**: This modular system maintains full compatibility with the original `load_data.py` while providing a modern, maintainable, and extensible architecture for tennis data processing.
