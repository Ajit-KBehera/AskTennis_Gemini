# Tennis Visualization Features

## Overview

The AskTennis application now includes powerful visualization tools that automatically generate charts and graphs when users request visual representations of tennis data. These tools use Plotly to create interactive, professional-quality visualizations.

## Available Visualization Tools

### 1. Head-to-Head Chart (`create_head_to_head_chart`)
**Purpose**: Compare two players' head-to-head record
**Example Queries**:
- "Show me Nadal vs Federer head-to-head"
- "Create a chart comparing Djokovic and Murray"
- "Visualize the rivalry between Serena and Venus"

**Data Requirements**:
- `winner_name`: Name of the winning player
- `loser_name`: Name of the losing player
- `surface`: Court surface (Clay, Hard, Grass, Carpet)
- `year`: Match year
- `tournament`: Tournament name

### 2. Surface Performance Chart (`create_surface_performance_chart`)
**Purpose**: Show a player's performance across different court surfaces
**Example Queries**:
- "Show me Djokovic's performance by surface"
- "Create a chart of Nadal's wins on different surfaces"
- "Visualize Federer's success on each surface type"

**Data Requirements**:
- `winner_name`: Player name
- `loser_name`: Opponent name
- `surface`: Court surface
- `year`: Match year

### 3. Ranking History Chart (`create_ranking_history_chart`)
**Purpose**: Display a player's ranking progression over time
**Example Queries**:
- "Show me Serena's ranking history"
- "Create a chart of Djokovic's ranking over time"
- "Visualize how Murray's ranking changed"

**Data Requirements**:
- `ranking_date`: Date of ranking
- `rank`: Player's ranking position
- `player`: Player name

### 4. Tournament Performance Chart (`create_tournament_performance_chart`)
**Purpose**: Show a player's wins by tournament
**Example Queries**:
- "Show me Federer's tournament wins"
- "Create a chart of Nadal's success by tournament"
- "Visualize which tournaments Djokovic dominates"

**Data Requirements**:
- `winner_name`: Player name
- `loser_name`: Opponent name
- `tourney_name`: Tournament name
- `year`: Match year

### 5. Season Performance Chart (`create_season_performance_chart`)
**Purpose**: Display a player's performance by year
**Example Queries**:
- "Show me Nadal's wins by year"
- "Create a chart of Serena's performance over the years"
- "Visualize Djokovic's yearly win totals"

**Data Requirements**:
- `winner_name`: Player name
- `loser_name`: Opponent name
- `year`: Match year

## How It Works

### 1. Query Recognition
The AI agent automatically recognizes when users request visualizations through keywords like:
- "Show me"
- "Visualize"
- "Chart"
- "Graph"
- "Plot"
- "Create a chart"

### 2. Data Retrieval
The agent first queries the database to retrieve the relevant data using standard SQL queries.

### 3. Data Formatting
The retrieved data is formatted as JSON with the required column names for the visualization tool.

### 4. Chart Generation
The appropriate visualization tool is called with the formatted data to generate a Plotly chart.

### 5. Display
The chart is returned as JSON data that can be rendered in the Streamlit interface.

## Example Usage Scenarios

### Scenario 1: Head-to-Head Analysis
**User Query**: "Show me the head-to-head between Nadal and Federer"

**Agent Process**:
1. Queries database for all matches between Nadal and Federer
2. Formats data with winner_name, loser_name, surface, year, tournament
3. Calls `create_head_to_head_chart` tool
4. Returns interactive bar chart showing wins for each player

### Scenario 2: Surface Performance Analysis
**User Query**: "Visualize Djokovic's performance by surface"

**Agent Process**:
1. Queries database for all Djokovic wins
2. Groups by surface type
3. Calls `create_surface_performance_chart` tool
4. Returns bar chart showing wins on Clay, Hard, Grass, Carpet

### Scenario 3: Career Progression
**User Query**: "Show me Serena's ranking history"

**Agent Process**:
1. Queries rankings table for Serena Williams
2. Orders by date
3. Calls `create_ranking_history_chart` tool
4. Returns line chart showing ranking progression over time

## Technical Implementation

### File Structure
```
tennis/
├── tennis_visualization_tools.py  # Visualization tools
├── tennis_core.py                 # Updated with visualization integration
└── __init__.py

agent/
├── agent_factory.py              # Updated to include visualization tools
└── ...

docs/
└── Visualization-Features.md    # This documentation
```

### Key Components

1. **TennisVisualizationTools Class**: Contains all visualization tool implementations
2. **Plotly Integration**: Uses plotly.express and plotly.graph_objects
3. **JSON Data Format**: Standardized data format for all tools
4. **Error Handling**: Comprehensive error handling for data issues
5. **Agent Integration**: Seamlessly integrated with existing tennis agent

## Benefits

### For Users
- **Visual Learning**: Charts make tennis statistics more accessible
- **Quick Insights**: Visual representations reveal patterns quickly
- **Interactive Charts**: Plotly charts are interactive and engaging
- **Professional Quality**: High-quality visualizations suitable for presentations

### For Developers
- **Modular Design**: Easy to add new visualization types
- **Consistent API**: All tools follow the same pattern
- **Error Handling**: Robust error handling prevents crashes
- **Extensible**: Simple to add new chart types

## Future Enhancements

### Potential New Visualizations
1. **Match Duration Analysis**: Charts showing match length trends
2. **Age Performance**: Player performance by age
3. **Nationality Analysis**: Performance by country
4. **Tournament Type Analysis**: Grand Slam vs Masters performance
5. **Seasonal Analysis**: Performance by month/season
6. **Injury Impact**: Performance before/after injuries

### Advanced Features
1. **Custom Styling**: User-defined colors and themes
2. **Export Options**: Save charts as images or PDFs
3. **Interactive Filters**: Filter data within charts
4. **Comparison Tools**: Side-by-side player comparisons
5. **Trend Analysis**: Statistical trend detection

## Troubleshooting

### Common Issues

1. **No Data Found**: Ensure database queries return valid data
2. **JSON Format Errors**: Verify data has required column names
3. **Chart Not Displaying**: Check Plotly installation and Streamlit configuration
4. **Performance Issues**: Large datasets may need pagination

### Debug Tips

1. **Check Data Format**: Verify JSON structure matches requirements
2. **Test with Sample Data**: Use provided test functions
3. **Monitor Logs**: Check application logs for error messages
4. **Validate Inputs**: Ensure player names match database exactly

## Conclusion

The visualization features transform the AskTennis application from a text-based query system into a comprehensive tennis analytics platform. Users can now explore tennis data through interactive charts and graphs, making complex statistics accessible and engaging.

The tool-based approach ensures reliability and consistency, while the modular design allows for easy expansion and customization. This implementation provides a solid foundation for advanced tennis analytics and visualization capabilities.
