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
- **Intelligent Responses**: Context-aware tennis insights
- **Historical Analysis**: AI-powered tennis history exploration

### 📊 **Comprehensive Analytics**
- **Player Metadata**: Handedness, nationality, height, birth dates
- **Surface Analysis**: Performance on Hard, Clay, Grass, Carpet
- **Era Classification**: Amateur (1877-1967) vs Professional (1968-2024)
- **Tournament Types**: Main Tour, Qualifying, Challenger, Futures, ITF
- **Ranking Context**: Historical ranking analysis with match context
- **Head-to-Head**: Complete player matchup analysis

## 🛠️ Technical Stack

- **Frontend**: Streamlit with modern UI
- **Backend**: Python with advanced data processing
- **AI/LLM**: Google Gemini API + LangChain + LangGraph
- **Database**: SQLite with 15 optimized indexes
- **Data Processing**: Pandas, NumPy for statistical analysis
- **Visualization**: Plotly for interactive charts
- **Data Sources**: ATP, WTA, Grand Slam, and historical tennis data

## 📁 Project Structure

```
AskTennis_Gemini/
├── app.py                          # 🚀 Main Streamlit application
├── load_data.py                    # 🗄️ Enhanced database creation
├── requirements.txt               # 📦 Unified dependencies
├── tennis_data.db                 # 🗃️ SQLite database (created after setup)
├── docs/
│   └── database/                  # 📚 Database documentation
│       ├── README.md              # Documentation overview
│       ├── Data-Enhancement.md    # Enhancement roadmap
│       ├── Database-Analysis.md   # Database analysis
│       └── Data-Validation_REQUIRED.md # Validation requirements
├── data/                          # 📊 Tennis data files
│   ├── tennis_atp/               # ATP match data
│   ├── tennis_wta/               # WTA match data
│   ├── tennis_MatchChartingProject/ # Detailed match data
│   └── tennis_slam_pointbypoint/ # Grand Slam data
└── README.md                      # This file
```

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
   git clone https://github.com/your-username/AskTennis_Gemini.git
   cd AskTennis_Gemini
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
   streamlit run app.py
   ```

7. **Open your browser** to `http://localhost:8501`

#### Option 2: Direct Installation

```bash
# Clone and navigate
git clone https://github.com/your-username/AskTennis_Gemini.git
cd AskTennis_Gemini

# Install dependencies
pip install -r requirements.txt

# Set up API key (create .streamlit/secrets.toml as above)
# Create database
python load_data.py

# Run application
streamlit run app.py
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
- **Query Speed**: <2 seconds for complex queries
- **Memory Usage**: Optimized for large datasets
- **Indexing**: 15 optimized indexes for fast lookups

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

## 📚 Documentation

- **Database Analysis**: `docs/database/Database-Analysis.md`
- **Enhancement History**: `docs/database/Data-Enhancement.md`
- **Validation Requirements**: `docs/database/Data-Validation_REQUIRED.md`

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
1. Check the documentation in `docs/database/`
2. Review the troubleshooting section above
3. Create an issue in the repository

---

**Status**: ✅ Production Ready - Complete Tennis Database with AI Integration

**Database Coverage**: 147 years (1877-2024) | 1.7M+ matches | 136K+ players | 5.3M+ rankings

**AI Capabilities**: Natural language queries | Historical analysis | Player insights | Tournament analytics