# AskTennis - Phase 2: Natural Language Processing

🎾 **AskTennis** is an AI-powered tennis statistics application that allows users to query tennis data through natural language questions. This is Phase 2, introducing advanced natural language processing capabilities powered by AI/LLM integration.

## 🚀 Features

### Phase 2: Natural Language Processing Capabilities
- **🤖 AI-Powered Queries**: Ask questions in natural language and get intelligent responses
- **🧠 Smart Data Analysis**: Advanced AI analysis of tennis statistics and trends
- **💬 Conversational Interface**: Interactive chat-based query system
- **📊 Dynamic Insights**: AI-generated insights and statistical analysis
- **🔍 Context-Aware Responses**: Understanding of tennis terminology and context

### Enhanced Data Coverage
- **ATP & WTA Data**: Both men's and women's professional tennis matches
- **Extended Time Period**: 2005-2025 (comprehensive historical data)
- **Multiple Data Sources**: ATP, WTA, and Grand Slam point-by-point data
- **Advanced Database**: Optimized SQLite with enhanced querying capabilities


## 🛠️ Technical Stack

- **Frontend**: Streamlit with AI Chat Interface
- **Backend**: Python with AI/LLM Integration
- **AI/LLM**: Google Gemini API for natural language processing
- **Database**: SQLite with advanced querying
- **Data Processing**: Pandas, NumPy for statistical analysis
- **Data Sources**: ATP, WTA, and Grand Slam CSV files
- **Natural Language**: Advanced NLP for tennis terminology understanding

## 📁 Project Structure

```
AskTennis_Gemini/
├── app.py                 # Main Streamlit application with AI chat interface
├── load_data.py          # Data loading and database creation script
├── tennis_data.db        # SQLite database (ignored by git)
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── data/                 # Tennis data files (ignored by git)
    ├── tennis_atp/       # ATP match data
    ├── tennis_wta/       # WTA match data
    ├── tennis_MatchChartingProject/  # Detailed match charting data
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
   pip install streamlit pandas sqlite3 google-generativeai python-dotenv
   ```

3. **Set up API credentials**
   ```bash
   # Create a .env file with your Google Gemini API key
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

4. **Load the data** (First time only)
   ```bash
   python load_data.py
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 🤖 Natural Language Query Examples

### Example Questions You Can Ask:
- **"Who won the most matches in 2024?"**
- **"Show me the head-to-head record between Novak Djokovic and Rafael Nadal"**
- **"Which players have won the most Grand Slams in the last 5 years?"**
- **"What's the win percentage of Serena Williams on clay courts?"**
- **"Who are the top 5 players with the best serve statistics?"**
- **"Show me all the finals that went to 5 sets in 2023"**
- **"Which country has produced the most tennis champions?"**
- **"What's the average match duration for women's tennis matches?"**

### AI-Powered Features:
- **🧠 Intelligent Analysis**: AI understands tennis terminology and context
- **📊 Dynamic Insights**: Get statistical insights and trends automatically
- **💬 Conversational Interface**: Ask follow-up questions naturally
- **🔍 Smart Filtering**: AI automatically filters and processes relevant data
- **📈 Trend Analysis**: AI identifies patterns and trends in tennis data

## 🔧 Configuration

### AI/LLM Setup
- **API Key**: Set your Google Gemini API key in the `.env` file
- **Model Configuration**: Adjust AI model parameters in the application
- **Response Customization**: Modify AI response templates and prompts

### Data Loading
Edit `load_data.py` to modify:
- **Years**: Change the `YEARS` list to include different years
- **Data Directories**: Modify `DATA_DIRS` to include additional data sources
- **Database Name**: Change `DB_FILE` to use a different database name

### Natural Language Processing
- **Tennis Terminology**: AI understands tennis-specific terms and context
- **Query Processing**: Advanced NLP for understanding user intent
- **Response Generation**: AI generates human-readable statistical insights

## 📈 Data Schema

The application uses a comprehensive `matches` table with the following key columns:
- `tourney_date`: Match date
- `tourney_name`: Tournament name
- `winner_name`: Winner's name
- `loser_name`: Loser's name
- `round`: Match round (F, SF, QF, etc.)
- `score`: Match score
- `surface`: Court surface (Hard, Clay, Grass, Carpet)
- `tourney_level`: Tournament level (G, M, A, etc.)
- `winner_rank`: Winner's ranking at time of match
- `loser_rank`: Loser's ranking at time of match
- `winner_hand`: Winner's playing hand
- `loser_hand`: Loser's playing hand

## 🎯 Phase 2 Goals

- ✅ **Natural Language Processing**: AI-powered query understanding and response generation
- ✅ **Enhanced Data Integration**: ATP, WTA, and Grand Slam data integration
- ✅ **AI Chat Interface**: Conversational interface for tennis statistics
- ✅ **Advanced Analytics**: AI-driven insights and trend analysis
- ✅ **Comprehensive Coverage**: Extended historical data (2005-2025)
- ✅ **Smart Query Processing**: Understanding of tennis terminology and context

## 🔮 Future Phases

### Phase 3: Enhanced Features
- **Point-by-Point Analysis**: Detailed match analysis with shot-by-shot data
- **Advanced Visualizations**: Interactive charts and graphs
- **Player Rankings**: Dynamic ranking systems and trend analysis
- **Match Predictions**: AI-powered match outcome predictions
- **Performance Analytics**: Advanced player performance metrics

### Phase 4: Advanced Analytics
- **Machine Learning Models**: Predictive analytics for tennis outcomes
- **Custom Dashboards**: Personalized analytics dashboards
- **Real-time Data**: Live match data integration
- **Social Features**: Community insights and sharing capabilities
- **Mobile Application**: Cross-platform mobile access

## 🤝 Contributing

This is Phase 2 of the AskTennis project with advanced natural language processing capabilities. For questions or contributions, please refer to the project documentation.

## 📝 License

[Add your license information here]

## 🐛 Known Issues

- Database file (`tennis_data.db`) is not included in version control
- Data loading is required on first run
- API key setup required for AI functionality
- Some complex queries may require specific tennis terminology

## 📞 Support

For issues or questions about Phase 2, please check the documentation or create an issue in the repository.

---

**Phase 2 Status**: ✅ Complete - Natural Language Processing Active
