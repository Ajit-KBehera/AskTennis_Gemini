# 🎾 AskTennis - Advanced AI Tennis Analytics Platform

**AskTennis** is a comprehensive AI-powered tennis statistics application that provides natural language querying of the most complete tennis database in existence, covering 147 years of tennis history (1877-2024) with advanced analytics, player metadata, and intelligent insights.

## ✨ Key Features

### 🏆 **Complete Tennis Database**
- **147 Years of History**: Complete tennis coverage from 1877 to 2024
- **1.7M+ Singles Matches**: Every recorded tennis match
- **26K+ Doubles Matches**: Complete doubles coverage (2000-2020)
- **136K+ Players**: Complete player database with metadata
- **5.3M+ Rankings**: Historical ranking data (1973-2024)
- **All Tournament Levels**: Grand Slams, Masters, Challengers, Futures, ITF

### 🤖 **Advanced AI Integration**
- **Natural Language Queries**: Ask questions in plain English
- **Google Gemini AI**: Powered by Gemini 2.5 Flash Lite
- **LangGraph Framework**: Stateful AI agent architecture
- **Intelligent Responses**: Context-aware tennis insights with player names
- **Historical Analysis**: AI-powered tennis history exploration
- **Performance Optimized**: 6% faster responses with cached mappings

### 🚀 **Performance Optimizations** (Latest Update)
- **Cached Mapping Tools**: 4x speedup for repeated terminology conversions
- **Performance Monitoring**: Real-time system performance tracking
- **Enhanced Response Quality**: Player names and context in all responses
- **Eliminated Duplicate Calls**: No more redundant tool executions
- **Optimized Prompts**: Better instructions for improved query efficiency
- **Stable Architecture**: No infinite loops or recursion errors

### 📊 **Comprehensive Analytics**
- **Player Metadata**: Handedness, nationality, height, birth dates
- **Surface Analysis**: Performance on Hard, Clay, Grass, Carpet
- **Era Classification**: Amateur (1877-1967) vs Professional (1968-2024)
- **Tournament Types**: Main Tour, Qualifying, Challenger, Futures, ITF
- **Ranking Context**: Historical ranking analysis with match context
- **Head-to-Head**: Complete player matchup analysis

### 🏗️ **Modern Architecture**
- **Modular Design**: Clean separation of concerns across 9 core modules
- **Performance Optimized**: Cached mappings and monitoring systems
- **Clean Code**: Two focused applications (45-line basic, 45-line enhanced UI) with modular components
- **Testable Components**: Individual module testing capabilities
- **Team Collaboration**: Parallel development on different modules
- **Code Reusability**: Components can be reused across projects
- **Production Ready**: Stable system with comprehensive error handling

## 🛠️ Technical Stack

- **Frontend**: Streamlit with modern UI
- **Backend**: Python with advanced data processing
- **AI/LLM**: Google Gemini API + LangChain + LangGraph
- **Database**: SQLite with 15 optimized indexes
- **Data Processing**: Pandas, NumPy for statistical analysis
- **Visualization**: Plotly for interactive charts
- **Data Sources**: ATP, WTA, Grand Slam, and historical tennis data

## 🏗️ Modular Architecture

AskTennis features a clean, modular architecture designed for maintainability, testability, and scalability:

### 🧩 **Core Modules**
- **`app_basic.py`** (45 lines) - Basic AI query interface
- **`app_ui.py`** (45 lines) - Enhanced UI with filters and database service
- **`ui/display/ui_display.py`** (276 lines) - UI display components and layout
- **`agent/`** - AI agent configuration and factory patterns
- **`llm/`** - LLM setup and configuration management
- **`config/`** - Modular configuration (AgentConfig, DatabaseConfig, Config)
- **`constants.py`** - Application-wide constants (root level)
- **`tennis/`** - Tennis-specific tools, mappings, and performance optimizations
- **`tennis_logging/`** - Comprehensive logging system with handlers
- **`ui/`** - User interface components
- **`graph/`** - LangGraph builder and state management
- **`services/`** - Database service layer for enhanced UI
- **`testing/`** - Automated testing framework with 100 curated tennis questions

### 🎯 **Benefits of Modular Design**
- **Single Responsibility**: Each module has a focused purpose
- **Easy Testing**: Individual modules can be unit tested
- **Code Reusability**: Components can be reused across projects
- **Maintainability**: Changes are isolated to specific modules
- **Collaboration**: Multiple developers can work on different modules
- **Readability**: Two focused applications (45-line basic, 45-line enhanced UI) with modular components

## 📁 Project Structure

```
AskTennis_Streamlit/
├── app_basic.py                       # 🚀 Basic AI query interface (45 lines)
├── app_ui.py                          # 🎨 Enhanced UI with filters (45 lines)
├── run_automated_tests.py             # 🧪 Automated testing framework CLI
├── requirements.txt                   # 📦 Unified dependencies
├── tennis_data.db                     # 🗃️ SQLite database (created after setup)
├── agent/                             # 🤖 AI Agent Configuration
│   ├── agent_factory.py              # Agent factory with performance optimizations
│   └── agent_state.py                # Agent state management
├── llm/                              # 🧠 LLM Setup and Configuration
│   └── llm_setup.py                  # LLM factory and configuration
├── tennis/                           # 🎾 Tennis-Specific Tools
│   ├── tennis_core.py                # Core tennis functionality
│   ├── tennis_mappings.py            # Tennis terminology mappings
│   ├── tennis_prompts.py             # Tennis-specific prompts
│   └── ranking_analysis.py           # Ranking analysis tools
├── tennis_logging/                   # 📝 Comprehensive Logging System
│   ├── base_logger.py                # Base logging functionality
│   ├── logging_factory.py            # Logging factory
│   ├── simplified_factory.py         # Simplified logging setup
│   ├── handlers/                     # Specialized logging handlers
│   └── setup/                        # Logging configuration
├── ui/                              # 🎨 User Interface Components
│   ├── display/                     # UI display components
│   │   └── ui_display.py           # Main UI display class (276 lines)
│   ├── formatting/                  # Data formatting utilities
│   │   └── consolidated_formatter.py # Consolidated formatter
│   ├── processing/                  # Query processing
│   │   └── query_processor.py      # Query processing logic
│   ├── styles/                     # UI styles
│   │   └── styles.css              # Custom CSS
│   └── utils/                      # UI utilities
│       └── style_loader.py         # Style loader utilities
├── graph/                           # 🔗 LangGraph Builder
│   └── langgraph_builder.py         # Graph construction and management
├── services/                        # 🔧 Services Layer
│   └── database_service.py          # Database service for enhanced UI
├── testing/                        # 🧪 Automated Testing Framework
│   ├── test_runner.py               # Main test orchestrator
│   ├── test_executor.py             # Individual test execution
│   ├── result_analyzer.py           # Result analysis and reporting
│   ├── test_data/                   # Test datasets and categories
│   ├── database/                    # Test database management
│   └── README.md                    # Testing framework documentation
├── load_data/                      # 📊 Data Loading
│   └── load_data.py                # Main data loading script
├── config/                         # ⚙️ Configuration Management
│   ├── agent_config.py             # Agent/LLM configuration
│   ├── database_config.py          # Database configuration
│   └── config.py                   # Main unified configuration class
├── constants.py                    # 📋 Application-wide constants (root level)
├── docs/                          # 📚 Documentation
│   ├── 01_System_Architecture.md   # System architecture documentation
│   ├── 02_Data_Flow.md             # Data flow documentation
│   ├── 03_Data_Model.md            # Data model documentation
│   ├── 04_Software_Process_Model.md # Software process documentation
│   ├── 05_Use_Case_Diagram.md     # Use case documentation
│   ├── 06_State_Diagram.md         # State diagram documentation
│   └── 07_UI_UX_Design.md          # UI/UX design documentation
├── data/                          # 📊 Tennis data files (not in repo)
│   ├── tennis_atp/               # ATP match data
│   ├── tennis_wta/               # WTA match data
│   ├── tennis_MatchChartingProject/ # Detailed match data
│   └── tennis_slam_pointbypoint/ # Grand Slam data
└── README.md                      # This file
```

## 🎯 Application Interfaces

AskTennis provides two different user interfaces to suit different needs:

### 🚀 **Basic AI Interface** (`app_basic.py`)
- **Purpose**: Simple AI-powered tennis querying
- **Features**: 
  - Natural language queries
  - AI-powered responses with context
  - Clean, minimal interface
  - Perfect for quick tennis questions
- **Best for**: Casual users, quick queries, AI-focused interactions

### 🎨 **Enhanced UI Interface** (`app_ui.py`)
- **Purpose**: Comprehensive tennis data analysis with AI integration
- **Features**:
  - Advanced filtering system (player, opponent, tournament, year, surface)
  - Interactive data tables
  - AI query integration
  - Database service integration
  - Real-time data analysis
- **Best for**: Data analysts, researchers, detailed tennis analysis

### 🔄 **Choosing Your Interface**
- **Use `app_basic.py`** if you want simple AI-powered tennis queries
- **Use `app_ui.py`** if you need advanced filtering and data analysis capabilities

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+** (recommended: Python 3.9 or 3.10)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Google Gemini API Key** (for AI functionality)
- **Tennis Data** (from Jeff Sackmann's GitHub repositories)

### Data Setup (Required First Step)

**⚠️ Important**: The tennis data is not included in this repository due to size constraints. You must download it separately.

1. **Download Tennis Data from Jeff Sackmann's GitHub**
   ```bash
   # Create data directory
   mkdir -p data
   
   # Download ATP data
   git clone https://github.com/JeffSackmann/tennis_atp.git data/tennis_atp
   
   # Download WTA data  
   git clone https://github.com/JeffSackmann/tennis_wta.git data/tennis_wta
   
   # Download Grand Slam point-by-point data
   git clone https://github.com/JeffSackmann/tennis_slam_pointbypoint.git data/tennis_slam_pointbypoint
   
   # Download Match Charting Project data
   git clone https://github.com/JeffSackmann/tennis_MatchChartingProject.git data/tennis_MatchChartingProject
   ```

2. **Verify Data Structure**
   ```bash
   # Check that data directories exist
   ls -la data/
   # Should show: tennis_atp, tennis_wta, tennis_slam_pointbypoint, tennis_MatchChartingProject
   ```

**Note**: The `data/` folder is in `.gitignore` to keep the repository lightweight. Each data repository is ~100MB-500MB, so the total download will be 1-2GB.

### Environment Setup

#### Option 1: Virtual Environment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ajit-KBehera/AskTennis_Streamlit.git
   cd AskTennis_Streamlit
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

3. **Upgrade pip and install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up API credentials**
   ```bash
   # Create .streamlit/secrets.toml file
   mkdir -p .streamlit
   echo '[secrets]' > .streamlit/secrets.toml
   echo 'GOOGLE_API_KEY = "your_gemini_api_key_here"' >> .streamlit/secrets.toml
   ```

5. **Create the database** (First time only - takes 30-90 minutes)
   ```bash
   python load_data.py
   ```

6. **Run the application**
   ```bash
   # Basic AI query interface
   streamlit run app_basic.py
   
   # Enhanced UI with filters and database service
   streamlit run app_ui.py
   ```

7. **Open your browser** to `http://localhost:8501`

#### Option 2: Direct Installation

```bash
# Clone and navigate
git clone https://github.com/Ajit-KBehera/AskTennis_Streamlit.git
cd AskTennis_Streamlit

# Install dependencies
pip install -r requirements.txt

# Set up API key (create .streamlit/secrets.toml as above)
# Create database
python load_data.py

# Run application
# Basic AI query interface
streamlit run app_basic.py

# Enhanced UI with filters and database service
streamlit run app_ui.py
```

## 🔧 Configuration

### API Key Setup
Create `.streamlit/secrets.toml`:
```toml
[secrets]
GOOGLE_API_KEY = "your_gemini_api_key_here"
```

### Database Configuration
The `load_data.py` script will create a comprehensive database with:
- **Complete Historical Coverage**: 1877-2024
- **All Tournament Levels**: Grand Slams to Futures
- **Player Metadata**: Complete player information
- **Rankings Integration**: Historical ranking context
- **Optimized Performance**: 15 indexes for fast queries

### Customization Options
- **Data Range**: Modify `YEARS` in `load_data.py` for different time periods
- **Data Sources**: Add additional data directories in `DATA_DIRS`
- **Database Name**: Change `DB_FILE` for custom database names

## 📊 Database Schema

### Core Tables
- **`matches`**: 1.7M+ singles matches (1877-2024)
- **`doubles_matches`**: 26K+ doubles matches (2000-2020)
- **`players`**: 136K+ players with complete metadata
- **`rankings`**: 5.3M+ ranking records (1973-2024)

### Enhanced Views
- **`matches_with_full_info`**: Complete match data with player details
- **`matches_with_rankings`**: Match data with ranking context
- **`player_rankings_history`**: Complete player ranking trajectories

### Key Features
- **100% Surface Data**: Complete surface information for all matches
- **Era Classification**: Amateur vs Professional era analysis
- **Tournament Types**: Complete tournament level coverage
- **Player Metadata**: Handedness, nationality, height, birth dates
- **Historical Rankings**: Complete ranking history integration

## 🧪 Automated Testing Framework

AskTennis includes a comprehensive automated testing framework with **100 curated tennis questions** across 8 categories:

### **Testing Features**
- **100 Test Cases**: Curated questions covering all tennis aspects
- **8 Categories**: Tournament winners, head-to-head, surface performance, statistics, historical records, rankings, match details, and complex queries
- **Automated Execution**: Run tests with configurable intervals (minimum 75 seconds, configurable in `constants.py`)
- **SQLite Database**: Store test results and sessions
- **Performance Metrics**: Track execution times and completion rates
- **Command-Line Interface**: Easy test execution and management

### **Quick Testing Commands**
```bash
# Run all 100 tests
python run_automated_tests.py --full

# Run specific questions
python run_automated_tests.py --questions 28
python run_automated_tests.py --questions 1,5,10,15
python run_automated_tests.py --questions 80-100

# Run category-specific tests
python run_automated_tests.py --category tournament_winner

# Run with custom intervals
python run_automated_tests.py --full --interval 90
```

### **Test Categories**
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

For detailed testing documentation, see `testing/README.md`.

## 🎯 Example Queries

### Historical Analysis
- "Who won the first Wimbledon in 1877?"
- "How many matches were played in the 1980s?"
- "Compare amateur vs professional eras"

### Player Analysis
- "Which left-handed players won the most matches?"
- "Who are the tallest players in tennis?"
- "Show me Roger Federer's head-to-head record"

### Tournament Analysis
- "How many Grand Slam matches were played on grass?"
- "Which players dominated the 1990s?"
- "Show me the most successful doubles teams"

### Ranking Analysis
- "Who was ranked #1 in 2020?"
- "Which top 10 players won the most matches?"
- "How many upsets happened in Grand Slams?"

## 📈 Performance

- **Database Size**: ~2GB (1.7M+ matches, 5.3M+ rankings)
- **Query Speed**: <2 seconds for complex queries (6% improvement with optimizations)
- **Memory Usage**: Optimized for large datasets
- **Indexing**: 15 optimized indexes for fast lookups
- **Cached Mappings**: 4x speedup for repeated terminology conversions
- **Response Time**: 3.5 seconds average (down from 3.7s)
- **Performance Monitoring**: Real-time system performance tracking
- **Stable Architecture**: No infinite loops or recursion errors

## 🔍 Troubleshooting

### Common Issues

1. **Data Not Found Error**
   - Error: "No data found in any directory"
   - Solution: Download tennis data from Jeff Sackmann's GitHub repositories (see Data Setup section above)

2. **Database Creation Takes Long Time**
   - Normal: 30-90 minutes for complete database
   - Solution: Be patient, process includes 147 years of data

3. **API Key Not Found**
   - Error: "Google API key not found"
   - Solution: Create `.streamlit/secrets.toml` with your API key

4. **Memory Issues**
   - Error: Out of memory during database creation
   - Solution: Close other applications, ensure 4GB+ RAM available

5. **Dependencies Issues**
   - Error: Module not found
   - Solution: Ensure virtual environment is activated and run `pip install -r requirements.txt`

### Performance Optimization
- **Large Datasets**: Database is optimized with indexes
- **Memory Usage**: Close unnecessary applications during setup
- **Query Speed**: Use the provided views for faster queries

## 🤝 Contributing

This project represents the most comprehensive tennis database in existence. Contributions are welcome for:
- Additional data sources
- Performance optimizations
- New analytical features
- Documentation improvements

## 📝 License

[Add your license information here]

## 🐛 Known Issues

- Database creation requires significant time (30-90 minutes)
- Large memory usage during initial setup
- API key required for AI functionality
- Some complex queries may take longer with very large datasets

## 📞 Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review the troubleshooting section above
3. Create an issue in the repository

---

## 🚀 Recent Updates (Latest)

### ⚡ Performance Improvements
- **6% Faster Responses**: 3.7s → 3.5s average response time
- **Cached Mapping Tools**: 4x speedup for repeated terminology conversions
- **Performance Monitoring**: Real-time system performance tracking
- **Enhanced Response Quality**: Player names and context in all responses
- **Eliminated Duplicate Calls**: No more redundant tool executions
- **Stable Architecture**: No infinite loops or recursion errors

### 🏗️ Architectural Enhancements
- **Modular Design**: Clean separation across 9 core modules
- **Configuration Refactoring**: Split into modular AgentConfig, DatabaseConfig, and unified Config classes
- **Code Organization**: Methods organized chronologically by execution flow
- **Constants Management**: Moved constants to root level for easier access
- **Performance Optimizations**: Cached mappings and monitoring systems
- **Production Ready**: Stable system with comprehensive error handling
- **Team Collaboration**: Parallel development on different modules
- **Code Reusability**: Components can be reused across projects

---

**Status**: ✅ Production Ready - Complete Tennis Database with AI Integration

**Architecture**: 🏗️ Modular Design - 9 focused modules with performance optimizations

**Database Coverage**: 147 years (1877-2024) | 1.7M+ matches | 136K+ players | 5.3M+ rankings

**AI Capabilities**: Natural language queries | Historical analysis | Player insights | Tournament analytics

**Performance**: ⚡ 6% faster responses | 💾 Cached mappings | 📊 Real-time monitoring | 🎯 Enhanced quality

**Code Quality**: 🧩 Single Responsibility | 🧪 Testable Components | 🔄 Reusable Modules | 👥 Team Collaboration Ready