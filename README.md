# AskTennis - Phase 3: Beautiful Visualization

🎾 **AskTennis** is an AI-powered tennis statistics application that allows users to query tennis data through natural language questions. This is Phase 3, introducing stunning interactive visualizations and beautiful data representations powered by advanced charting libraries.

## 🚀 Features

### Phase 3: Beautiful Visualization Capabilities
- **📊 Interactive Charts**: Stunning interactive charts and graphs for tennis statistics
- **🎨 Beautiful Dashboards**: Modern, responsive dashboard designs
- **📈 Dynamic Visualizations**: Real-time data visualization with smooth animations
- **🎯 Player Performance Charts**: Comprehensive player performance visualizations
- **🏆 Tournament Analytics**: Beautiful tournament and match analysis charts
- **📱 Responsive Design**: Mobile-friendly visualization components

### Advanced Visualization Features
- **🎨 Interactive Dashboards**: Beautiful, responsive dashboards with real-time updates
- **📊 Multi-Chart Support**: Line charts, bar charts, pie charts, heatmaps, and more
- **🎯 Player Comparison Tools**: Side-by-side player performance comparisons
- **📈 Trend Analysis Charts**: Historical performance trends and patterns
- **🏆 Tournament Visualization**: Tournament brackets and match progression charts
- **📱 Mobile-Optimized**: Responsive design that works perfectly on all devices


## 🛠️ Technical Stack

- **Frontend**: Streamlit with Beautiful Visualization Interface
- **Backend**: Python with AI/LLM Integration
- **Visualization**: Plotly, Matplotlib, Seaborn, Altair for stunning charts
- **AI/LLM**: Google Gemini API for natural language processing
- **Database**: SQLite with advanced querying
- **Data Processing**: Pandas, NumPy for statistical analysis
- **Interactive Charts**: Plotly Dash components for dynamic visualizations
- **Styling**: Custom CSS and Streamlit theming for beautiful UI
- **Data Sources**: ATP, WTA, and Grand Slam CSV files

## 📁 Project Structure

```
AskTennis_Gemini/
├── app.py                 # Main Streamlit application with beautiful visualizations
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
   pip install streamlit pandas sqlite3 google-generativeai python-dotenv plotly matplotlib seaborn altair
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

## 📊 Beautiful Visualization Examples

### Interactive Chart Types:
- **📈 Player Performance Trends**: Beautiful line charts showing player rankings over time
- **🏆 Tournament Winners**: Stunning pie charts and bar charts for tournament victories
- **🎯 Head-to-Head Comparisons**: Interactive comparison charts between players
- **📊 Surface Performance**: Heatmaps showing performance on different court surfaces
- **📈 Match Statistics**: Dynamic charts for serve statistics, return games, and more
- **🏅 Ranking Evolution**: Beautiful timeline charts showing ranking changes
- **📱 Mobile Dashboards**: Responsive charts that work perfectly on mobile devices

### Visualization Features:
- **🎨 Beautiful Design**: Modern, clean, and professional chart designs
- **📊 Interactive Elements**: Hover effects, zoom, pan, and click interactions
- **📱 Responsive Layout**: Charts automatically adapt to different screen sizes
- **🎯 Real-time Updates**: Dynamic charts that update with new data
- **📈 Multiple Chart Types**: Line, bar, pie, scatter, heatmap, and more
- **🎨 Custom Styling**: Beautiful color schemes and professional theming

## 🔧 Configuration

### Visualization Setup
- **Chart Libraries**: Configure Plotly, Matplotlib, Seaborn, and Altair settings
- **Theme Customization**: Modify color schemes and chart styling
- **Interactive Features**: Enable/disable hover effects, zoom, and pan features
- **Responsive Design**: Configure mobile and desktop layout settings

### AI/LLM Setup
- **API Key**: Set your Google Gemini API key in the `.env` file
- **Model Configuration**: Adjust AI model parameters in the application
- **Response Customization**: Modify AI response templates and prompts

### Data Loading
Edit `load_data.py` to modify:
- **Years**: Change the `YEARS` list to include different years
- **Data Directories**: Modify `DATA_DIRS` to include additional data sources
- **Database Name**: Change `DB_FILE` to use a different database name

### Beautiful Visualization Features
- **Chart Customization**: Customize colors, fonts, and styling for all charts
- **Interactive Elements**: Configure hover effects, tooltips, and animations
- **Mobile Optimization**: Ensure charts work perfectly on all device sizes
- **Performance**: Optimize chart rendering for large datasets

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

## 🎯 Phase 3 Goals

- ✅ **Beautiful Visualizations**: Stunning interactive charts and graphs
- ✅ **Interactive Dashboards**: Modern, responsive dashboard designs
- ✅ **Player Performance Charts**: Comprehensive player performance visualizations
- ✅ **Tournament Analytics**: Beautiful tournament and match analysis charts
- ✅ **Mobile Optimization**: Responsive design that works on all devices
- ✅ **Advanced Chart Types**: Multiple chart types with beautiful styling

## 🔮 Future Phases

### Phase 4: Advanced Analytics
- **Point-by-Point Analysis**: Detailed match analysis with shot-by-shot data
- **Machine Learning Models**: Predictive analytics for tennis outcomes
- **Real-time Data**: Live match data integration
- **Advanced Predictions**: AI-powered match outcome predictions
- **Performance Analytics**: Advanced player performance metrics

### Phase 5: Enterprise Features
- **Custom Dashboards**: Personalized analytics dashboards
- **Social Features**: Community insights and sharing capabilities
- **Mobile Application**: Cross-platform mobile access
- **API Integration**: RESTful API for third-party integrations
- **Advanced Security**: Enterprise-grade security and authentication

## 🤝 Contributing

This is Phase 3 of the AskTennis project with beautiful visualization capabilities. For questions or contributions, please refer to the project documentation.

## 📝 License

[Add your license information here]

## 🐛 Known Issues

- Database file (`tennis_data.db`) is not included in version control
- Data loading is required on first run
- API key setup required for AI functionality
- Large datasets may require optimization for smooth chart rendering
- Some complex visualizations may need additional memory for processing

## 📞 Support

For issues or questions about Phase 3, please check the documentation or create an issue in the repository.

---

**Phase 3 Status**: ✅ Complete - Beautiful Visualization Active
