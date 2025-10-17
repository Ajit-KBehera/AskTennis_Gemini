# AskTennis - Phase 1: MVP (Minimum Viable Product)

🎾 **AskTennis** is an AI-powered tennis statistics application that allows users to query tennis data through natural language questions. This is Phase 1, focusing on delivering a working MVP with pre-defined queries.

## 🚀 Features

### Current MVP Capabilities
- **Top Players Analysis**: View the top 10 players with the most wins in 2024
- **Head-to-Head Records**: Compare match history between any two players
- **Tournament Winners**: Find all tournament champions for specific years
- **Interactive Web Interface**: Clean, user-friendly Streamlit interface

### Data Coverage
- **ATP Tour Data**: Professional men's tennis matches
- **Time Period**: 2023-2025 (configurable)
- **Data Sources**: ATP official match data
- **Database**: SQLite for fast querying

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite
- **Data Processing**: Pandas
- **Data Sources**: ATP CSV files

## 📁 Project Structure

```
AskTennis_Gemini/
├── app.py                 # Main Streamlit application
├── load_data.py          # Data loading and database creation script
├── tennis_data.db        # SQLite database (ignored by git)
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── data/                 # Tennis data files (ignored by git)
    ├── tennis_atp/       # ATP match data
    ├── tennis_wta/       # WTA match data
    └── tennis_slam_pointbypoint/  # Grand Slam point-by-point data
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AskTennis_Gemini
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit pandas sqlite3
   ```

3. **Load the data** (First time only)
   ```bash
   python load_data.py
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 📊 Available Queries

### 1. Top 10 Players by Wins (2024)
- Shows the most successful players of 2024
- Displays player names and win counts
- Automatically sorted by number of wins

### 2. Head-to-Head Records
- Compare any two players' match history
- Shows tournament, date, round, winner, and score
- Displays win/loss summary
- Interactive player name input

### 3. Tournament Winners by Year
- Find all tournament champions for a specific year
- Shows tournament name and champion
- Supports years 2023-2025

## 🔧 Configuration

### Data Loading
Edit `load_data.py` to modify:
- **Years**: Change the `YEARS` list to include different years
- **Data Directory**: Modify `DATA_DIR` to point to different data sources
- **Database Name**: Change `DB_FILE` to use a different database name

### Adding New Queries
1. Add your question to the `question_options` list in `app.py`
2. Create a new function to handle the query
3. Add the logic in the main app section

## 📈 Data Schema

The application uses a `matches` table with the following key columns:
- `tourney_date`: Match date
- `tourney_name`: Tournament name
- `winner_name`: Winner's name
- `loser_name`: Loser's name
- `round`: Match round (F, SF, QF, etc.)
- `score`: Match score

## 🎯 Phase 1 Goals

- ✅ **Working MVP**: Basic functionality with pre-defined queries
- ✅ **Data Integration**: ATP data loading and database creation
- ✅ **User Interface**: Clean, intuitive web interface
- ✅ **Core Queries**: Essential tennis statistics queries
- ✅ **Documentation**: Clear setup and usage instructions

## 🔮 Future Phases

### Phase 2: Natural Language Processing
- Integration with AI/LLM for natural language queries
- Dynamic query generation from user questions
- Advanced statistical analysis

### Phase 3: Enhanced Features
- WTA (women's) tennis data integration
- Point-by-point analysis
- Advanced visualizations and charts
- Player rankings and trends

### Phase 4: Advanced Analytics
- Machine learning predictions
- Performance analytics
- Historical trend analysis
- Custom dashboard creation

## 🤝 Contributing

This is Phase 1 of the AskTennis project. For questions or contributions, please refer to the project documentation.

## 📝 License

[Add your license information here]

## 🐛 Known Issues

- Database file (`tennis_data.db`) is not included in version control
- Data loading is required on first run
- Limited to ATP men's tennis data only
- Pre-defined queries only (no natural language processing yet)

## 📞 Support

For issues or questions about Phase 1, please check the documentation or create an issue in the repository.

---

**Phase 1 Status**: ✅ Complete - MVP Working
