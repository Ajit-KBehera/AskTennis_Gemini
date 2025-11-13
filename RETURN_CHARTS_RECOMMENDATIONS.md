# 🏓 Return Tab - Chart Recommendations & Visualizations

## Overview
This document outlines 15+ recommended chart types for the Return tab, each with pseudo-chart visualizations, use cases, data requirements, and implementation complexity ratings.

**Current Implementation**: Return tab is a placeholder (coming soon)

**Available Data Fields**:
- `w_bpConverted`, `l_bpConverted`: Break points converted (when returning)
- `w_SvGms`, `l_SvGms`: Service games won
- Return Points Won %: Calculated from opponent's serve stats (100 - opponent's serve points won %)
- Return Games Won: Calculated from opponent's service games lost
- Opponent serve stats: `opponent_1stIn`, `opponent_1stWon`, `opponent_2ndWon` (from serve_stats.py)

**Note**: Return statistics are calculated from the opponent's serve perspective (opposite of serve stats).

---

## Chart Recommendations

### 1. 📈 Return Points Won % Timeline Chart
**Type**: Line Chart with Markers  
**Complexity**: ⭐⭐ (Medium)  
**Priority**: 🔥🔥 High

**Description**: Shows return points won percentage over time, tracking return performance progression.

**Use Cases**:
- Track return performance trends
- Identify periods of strong/weak return performance
- Compare return performance across different periods
- Show return consistency over time

**Data Requirements**: `tourney_date`, return points won % (calculated from opponent serve stats)

**Pseudo Chart**:
```
Return Points Won % Over Time
─────────────────────────────────────────────────────────
Return % │
   50% │
       │
   45% │                    ╱╲
       │                   ╱  ╲
   40% │              ╱╱      ╲╲
       │            ╱╱          ╲╲
   35% │         ╱╱              ╲╲
       │       ╱╱                  ╲╲
   30% │    ╱╱                      ╲╲
       │  ╱╱                          ╲╲
   25% └──────────────────────────────────────────────────
      2020          2021          2022          2023
```

**Visual Style**: 
- Line chart with markers for each match
- Trend line showing overall progression
- Hover tooltips showing match details
- Color coding: Green (above average), Red (below average)

---

### 2. 🎯 Break Point Conversion Timeline Chart
**Type**: Line Chart with Markers  
**Complexity**: ⭐⭐ (Medium)  
**Priority**: 🔥🔥 High

**Description**: Shows break point conversion percentage over time, highlighting clutch return performance.

**Use Cases**:
- Track break point conversion trends
- Identify clutch performance periods
- Show improvement in break point conversion
- Compare conversion rates across different periods

**Data Requirements**: `tourney_date`, `w_bpConverted`, `l_bpConverted`, break points faced (calculated)

**Pseudo Chart**:
```
Break Point Conversion % Over Time
─────────────────────────────────────────────────────────
Conversion % │
      60% │
          │
      50% │                    ╱╲
          │                   ╱  ╲
      40% │              ╱╱      ╲╲
          │            ╱╱          ╲╲
      30% │         ╱╱              ╲╲
          │       ╱╱                  ╲╲
      20% │    ╱╱                      ╲╲
          │  ╱╱                          ╲╲
      10% └──────────────────────────────────────────────────
         2020          2021          2022          2023
     ● = Match Data Points  |  ─── = Trend Line
```

**Visual Style**:
- Line chart with markers
- Reference line at average conversion rate
- Annotations for high/low conversion matches
- Tooltips showing break points faced/converted

---

### 3. 🛡️ Break Point Save % Timeline Chart
**Type**: Line Chart with Markers  
**Complexity**: ⭐⭐ (Medium)  
**Priority**: 🔥🔥 High

**Description**: Shows break point save percentage when serving (defensive return perspective), tracking ability to save break points.

**Use Cases**:
- Track break point defense trends
- Show ability to save break points when serving
- Identify periods of strong/weak break point defense
- Compare save rates across periods

**Data Requirements**: `tourney_date`, `w_bpSaved`, `l_bpSaved`, `w_bpFaced`, `l_bpFaced`

**Pseudo Chart**:
```
Break Point Save % Over Time
─────────────────────────────────────────────────────────
Save % │
  100% │
       │
   80% │                    ╱╲
       │                   ╱  ╲
   60% │              ╱╱      ╲╲
       │            ╱╱          ╲╲
   40% │         ╱╱              ╲╲
       │       ╱╱                  ╲╲
   20% │    ╱╱                      ╲╲
       │  ╱╱                          ╲╲
    0% └──────────────────────────────────────────────────
      2020          2021          2022          2023
     Higher = Better Defense  |  Lower = More Breaks Against
```

**Visual Style**:
- Line chart with markers
- Reference line at average save rate
- Color coding: Green (high save %), Red (low save %)
- Tooltips showing break points faced/saved

---

### 4. 📊 Combined Break Point Performance Chart
**Type**: Dual-Axis Line Chart  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥🔥 High

**Description**: Shows both break point conversion (when returning) and break point save % (when serving) on the same chart.

**Use Cases**:
- Compare offensive vs defensive break point performance
- Show overall break point game strength
- Identify balance between conversion and save rates
- Track comprehensive break point performance

**Data Requirements**: `tourney_date`, break point conversion %, break point save %

**Pseudo Chart**:
```
Break Point Performance: Conversion vs Save %
─────────────────────────────────────────────────────────
Percentage │
     100% │
          │
      80% │                    ╱╲  Save %
          │                   ╱  ╲
      60% │              ╱╱      ╲╲
          │            ╱╱          ╲╲
      40% │         ╱╱              ╲╲  Conversion %
          │       ╱╱                  ╲╲
      20% │    ╱╱                      ╲╲
          │  ╱╱                          ╲╲
       0% └──────────────────────────────────────────────────
         2020          2021          2022          2023
     ─── = Conversion %  |  ─── = Save %
```

**Visual Style**:
- Dual y-axis chart
- Two lines: Conversion % (left axis), Save % (right axis)
- Different colors for each metric
- Legend distinguishing the two metrics

---

### 5. 🎲 Return Performance Radar Chart
**Type**: Radar/Spider Chart  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥🔥 Medium-High

**Description**: Multi-dimensional view of return performance including return points won %, break point conversion, return games won %, etc.

**Use Cases**:
- Comprehensive return performance overview
- Compare return stats across different dimensions
- Show return strengths and weaknesses
- Compare player vs opponent return stats

**Data Requirements**: Multiple return metrics (return points won %, break point conversion %, return games won %, etc.)

**Pseudo Chart**:
```
Return Performance Radar Chart
─────────────────────────────────────────────────────────
                    Return Points Won %
                         ╱╲
                        ╱  ╲
                       ╱    ╲
                      ╱      ╲
Break Point         ╱          ╲         Return Games Won %
Conversion %       ╱            ╲
                  ╱              ╲
                 ╱                ╲
                ╱                  ╲
               ╱                    ╲
              ╱                      ╲
             ╱                        ╲
            ╱                          ╲
           ╱                            ╲
          ╱                              ╲
         ╱                                ╲
        ╱                                  ╲
       ╱                                    ╲
      ╱                                      ╲
     ╱                                        ╲
    ╱                                          ╲
   ╱                                            ╲
  ╱                                              ╲
 ╱                                                ╲
╱                                                  ╲
Opponent 1st Serve Return %    Opponent 2nd Serve Return %
```

**Visual Style**:
- Radar chart with multiple axes
- Player stats as filled polygon
- Optional: Opponent stats as outline polygon
- Color coding by performance level

---

### 6. 🏆 Return Performance by Surface Chart
**Type**: Grouped Bar Chart  
**Complexity**: ⭐⭐ (Medium)  
**Priority**: 🔥🔥 Medium-High

**Description**: Shows return performance metrics (return points won %, break point conversion) across different surfaces.

**Use Cases**:
- Compare return performance on different surfaces
- Identify surface-specific return strengths
- Show return consistency across surfaces
- Highlight best/worst return surfaces

**Data Requirements**: `surface`, return performance metrics

**Pseudo Chart**:
```
Return Performance by Surface
─────────────────────────────────────────────────────────
Performance % │
       50% │
           │
       40% │     ████        ████        ████
           │     ████        ████        ████
       30% │     ████        ████        ████
           │     ████        ████        ████
       20% │     ████        ████        ████
           │     ████        ████        ████
       10% │     ████        ████        ████
           │     ████        ████        ████
        0% └──────────────────────────────────────────────────
          Hard          Clay         Grass       Carpet
     ████ = Return Points Won %  |  ████ = Break Point Conversion %
```

**Visual Style**:
- Grouped bar chart
- Multiple metrics per surface
- Color coding by metric type
- Tooltips showing exact percentages

---

### 7. 📉 Break Point Opportunities vs Conversion Scatter
**Type**: Scatter Plot  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥🔥 Medium

**Description**: Scatter plot showing relationship between break point opportunities created and conversion rate.

**Use Cases**:
- Understand break point creation vs conversion relationship
- Identify players who create many opportunities but convert poorly
- Show efficiency in break point conversion
- Compare opportunity creation with conversion success

**Data Requirements**: Break points created (calculated), break point conversion %

**Pseudo Chart**:
```
Break Point Opportunities vs Conversion Rate
─────────────────────────────────────────────────────────
Conversion % │
      60% │
          │                    ●
      50% │              ●     ●
          │         ●    ●     ●
      40% │    ●    ●    ●     ●
          │    ●    ●    ●     ●
      30% │    ●    ●    ●     ●
          │    ●    ●
      20% │    ●
          │
      10% │
          │
       0% └──────────────────────────────────────────────────
          0    2    4    6    8   10   12   14   16
                  Break Points Created per Match
     ● = Match Data Point  |  ─── = Trend Line
```

**Visual Style**:
- Scatter plot with trend line
- Color coding by match result (win/loss)
- Size by total break points
- Tooltips showing match details

---

### 8. 🔄 Return Points Won % vs Opponent Serve Quality
**Type**: Scatter Plot  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥 Medium

**Description**: Shows relationship between opponent's serve quality (1st serve %, ace rate) and return points won %.

**Use Cases**:
- Understand how opponent serve quality affects return performance
- Show return performance against strong servers
- Identify return consistency vs different serve types
- Analyze return adaptability

**Data Requirements**: Opponent serve stats, return points won %

**Pseudo Chart**:
```
Return Points Won % vs Opponent 1st Serve %
─────────────────────────────────────────────────────────
Return % │
   50% │
       │                    ●
   40% │              ●     ●
       │         ●    ●     ●
   30% │    ●    ●    ●     ●
       │    ●    ●    ●     ●
   20% │    ●    ●    ●     ●
       │    ●    ●
   10% │    ●
       │
    0% └──────────────────────────────────────────────────
       50%   55%   60%   65%   70%   75%   80%
              Opponent 1st Serve %
     ● = Match Data Point  |  ─── = Trend Line
```

**Visual Style**:
- Scatter plot with trend line
- Color coding by surface
- Size by match importance
- Tooltips showing opponent and match details

---

### 9. 📊 Return Games Won % Timeline Chart
**Type**: Line Chart  
**Complexity**: ⭐⭐ (Medium)  
**Priority**: 🔥🔥 Medium-High

**Description**: Shows percentage of return games won over time, tracking ability to break serve.

**Use Cases**:
- Track break game performance over time
- Show return game consistency
- Identify periods of strong return game
- Compare return game performance across periods

**Data Requirements**: `tourney_date`, return games won % (calculated from opponent service games)

**Pseudo Chart**:
```
Return Games Won % Over Time
─────────────────────────────────────────────────────────
Games Won % │
      40% │
          │
      30% │                    ╱╲
          │                   ╱  ╲
      20% │              ╱╱      ╲╲
          │            ╱╱          ╲╲
      10% │         ╱╱              ╲╲
          │       ╱╱                  ╲╲
       0% │    ╱╱                      ╲╲
          │  ╱╱                          ╲╲
     -10% └──────────────────────────────────────────────────
         2020          2021          2022          2023
     Higher = More Breaks  |  Lower = Fewer Breaks
```

**Visual Style**:
- Line chart with markers
- Reference line at average
- Color coding: Green (above average), Red (below average)
- Tooltips showing break games won/lost

---

### 10. 🎯 Break Point Conversion Heatmap
**Type**: Heatmap  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥 Medium

**Description**: Heatmap showing break point conversion rates by surface and tournament level.

**Use Cases**:
- Visualize break point conversion patterns
- Identify surface-specific conversion strengths
- Show conversion consistency across tournament levels
- Highlight best/worst conversion scenarios

**Data Requirements**: `surface`, `tourney_level`, break point conversion %

**Pseudo Chart**:
```
Break Point Conversion Heatmap
─────────────────────────────────────────────────────────
Surface │ Grand Slam  Masters  ATP Tour  Challenger
────────┼─────────────────────────────────────────────
Hard    │   45%       42%      38%       35%
Clay    │   48%       45%      40%       37%
Grass   │   42%       40%      36%       33%
Carpet  │   40%       38%      35%       32%

Color Scale: Dark Green (50%+) → Light Green (40-50%) 
           → Yellow (30-40%) → Orange (20-30%) → Red (<20%)
```

**Visual Style**:
- Heatmap with color gradient
- Rows: Surfaces, Columns: Tournament levels
- Tooltips showing exact conversion rates
- Color intensity by performance level

---

### 11. 📈 Return Performance Comparison Chart
**Type**: Multi-line Chart  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥🔥 Medium-High

**Description**: Compares return performance metrics (return points won %, break point conversion) over time.

**Use Cases**:
- Compare multiple return metrics simultaneously
- Show correlation between different return stats
- Track comprehensive return performance
- Identify trends across return dimensions

**Data Requirements**: `tourney_date`, multiple return metrics

**Pseudo Chart**:
```
Return Performance Comparison
─────────────────────────────────────────────────────────
Performance % │
       50% │
           │
       40% │                    ╱╲  Return Points Won %
           │                   ╱  ╲
       30% │              ╱╱      ╲╲
           │            ╱╱          ╲╲
       20% │         ╱╱              ╲╲  Break Point Conversion %
           │       ╱╱                  ╲╲
       10% │    ╱╱                      ╲╲
           │  ╱╱                          ╲╲
        0% └──────────────────────────────────────────────────
          2020          2021          2022          2023
     ─── = Return Points Won %  |  ─── = Break Point Conversion %
```

**Visual Style**:
- Multi-line chart with different colors
- Legend distinguishing metrics
- Tooltips showing all metrics at each point
- Optional: Dual y-axis if scales differ significantly

---

### 12. 🎲 Return Performance Distribution Histogram
**Type**: Histogram  
**Complexity**: ⭐ (Low)  
**Priority**: 🔥 Medium

**Description**: Shows distribution of return points won % across matches, revealing consistency.

**Use Cases**:
- Understand return performance distribution
- Identify most common return performance levels
- Show return consistency (narrow vs wide distribution)
- Compare distribution across different periods

**Data Requirements**: Return points won % (frequency distribution)

**Pseudo Chart**:
```
Return Points Won % Distribution
─────────────────────────────────────────────────────────
Count │
  200 │
      │
  150 │     ████
      │     ████
  100 │     ████        ████
      │     ████        ████
   50 │     ████        ████        ████
      │     ████        ████        ████
    0 └──────────────────────────────────────────────────
      20-25%  25-30%  30-35%  35-40%  40-45%  45-50%
              Return Points Won % Ranges
```

**Visual Style**:
- Histogram with return % ranges
- Frequency count on y-axis
- Color gradient from low to high frequency
- Tooltips showing exact count and percentage

---

### 13. 🛡️ Break Point Save vs Conversion Balance Chart
**Type**: Scatter Plot  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥 Medium

**Description**: Shows balance between break point conversion (offensive) and break point save % (defensive).

**Use Cases**:
- Understand break point game balance
- Identify players strong in both conversion and saving
- Show offensive vs defensive break point strength
- Compare balance across different players/periods

**Data Requirements**: Break point conversion %, break point save %

**Pseudo Chart**:
```
Break Point Game Balance
─────────────────────────────────────────────────────────
Break Point Save % │
           100% │
               │
            80% │                    ●
               │              ●     ●
            60% │         ●    ●     ●
               │    ●    ●    ●     ●
            40% │    ●    ●    ●     ●
               │    ●    ●    ●
            20% │    ●    ●
               │    ●
             0% └──────────────────────────────────────────────────
                0%   10%   20%   30%   40%   50%   60%
                    Break Point Conversion %
     ● = Match Data Point  |  ─── = Ideal Balance Line
```

**Visual Style**:
- Scatter plot with diagonal reference line
- Color coding by match result
- Size by total break points
- Quadrants showing different balance types

---

### 14. 📊 Return Performance by Opponent Rank Chart
**Type**: Scatter Plot or Grouped Bar Chart  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥 Medium

**Description**: Shows return performance metrics against opponents of different ranking tiers.

**Use Cases**:
- Understand return performance vs different opponent levels
- Show return consistency across opponent ranks
- Identify return performance patterns
- Compare return effectiveness vs top players

**Data Requirements**: Opponent rank, return performance metrics

**Pseudo Chart**:
```
Return Performance vs Opponent Rank
─────────────────────────────────────────────────────────
Return % │
   50% │
       │                    ●
   40% │              ●     ●
       │         ●    ●     ●
   30% │    ●    ●    ●     ●
       │    ●    ●    ●     ●
   20% │    ●    ●    ●     ●
       │    ●    ●
   10% │    ●
       │
    0% └──────────────────────────────────────────────────
       1-10   11-20   21-50   51-100   100+
              Opponent Rank Range
     ● = Return Points Won %  |  ─── = Trend Line
```

**Visual Style**:
- Scatter plot or grouped bar chart
- Rank ranges on x-axis
- Return metrics on y-axis
- Color coding by surface
- Tooltips showing match count per rank range

---

### 15. 🔥 Return Performance Consistency Chart
**Type**: Box Plot or Violin Plot  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥 Low-Medium

**Description**: Shows return performance consistency using box plots or violin plots across different periods/surfaces.

**Use Cases**:
- Visualize return performance variability
- Compare consistency across periods
- Show return performance distribution
- Identify periods of high/low consistency

**Data Requirements**: Return performance metrics grouped by period/surface

**Pseudo Chart**:
```
Return Performance Consistency (Box Plot)
─────────────────────────────────────────────────────────
Return % │
   50% │
       │
   40% │     ┌─┐        ┌─┐        ┌─┐
       │     │ │        │ │        │ │
   30% │     │ │        │ │        │ │
       │     │ │        │ │        │ │
   20% │     │ │        │ │        │ │
       │     └─┘        └─┘        └─┘
   10% │
       │
    0% └──────────────────────────────────────────────────
      2020          2021          2022
     ┌─┐ = Interquartile Range  |  ─ = Median  |  • = Outliers
```

**Visual Style**:
- Box plot showing quartiles and outliers
- Optional: Violin plot for distribution shape
- Color coding by period/surface
- Tooltips showing statistical summary

---

### 16. 📈 Return Performance Trend Analysis Chart
**Type**: Line Chart with Moving Average  
**Complexity**: ⭐⭐⭐ (Medium-High)  
**Priority**: 🔥🔥 Medium

**Description**: Shows return performance with moving average trend lines to smooth out match-to-match variability.

**Use Cases**:
- Identify long-term return trends
- Smooth out match-to-match variability
- Show return performance trajectory
- Compare short-term vs long-term trends

**Data Requirements**: `tourney_date`, return performance metrics

**Pseudo Chart**:
```
Return Performance with Moving Average
─────────────────────────────────────────────────────────
Return % │
   50% │
       │                    ╱╲
   40% │              ╱╱      ╲╲  ──── Moving Avg
       │            ╱╱          ╲╲
   30% │         ╱╱              ╲╲
       │       ╱╱                  ╲╲
   20% │    ╱╱                      ╲╲
       │  ╱╱                          ╲╲
   10% └──────────────────────────────────────────────────
      2020          2021          2022          2023
     ─── = Match Data  |  ──── = 10-Match Moving Average
```

**Visual Style**:
- Line chart with markers for matches
- Smoothed trend line (moving average)
- Optional: Multiple moving average windows
- Tooltips showing both raw and smoothed values

---

### 17. 🎯 Clutch Return Performance Chart
**Type**: Bar Chart or Line Chart  
**Complexity**: ⭐⭐⭐⭐ (High)  
**Priority**: 🔥 Low-Medium

**Description**: Shows return performance in clutch situations (break points, deciding sets, tiebreaks).

**Use Cases**:
- Identify clutch return performance
- Show return performance under pressure
- Compare regular vs clutch return stats
- Highlight mental strength in return game

**Data Requirements**: Clutch situation indicators, return performance in clutch situations

**Pseudo Chart**:
```
Clutch Return Performance
─────────────────────────────────────────────────────────
Performance % │
       50% │
           │
       40% │     ████        ████
           │     ████        ████
       30% │     ████        ████
           │     ████        ████
       20% │     ████        ████
           │     ████        ████
       10% │     ████        ████
           │     ████        ████
        0% └──────────────────────────────────────────────────
          Regular    Break Points  Deciding Set  Tiebreak
     ████ = Return Points Won %  |  ████ = Break Point Conversion %
```

**Visual Style**:
- Grouped bar chart
- Comparison of regular vs clutch performance
- Color coding by situation type
- Tooltips showing sample sizes

---

## Implementation Priority Matrix

### High Priority (Implement First)
1. **Return Points Won % Timeline** - Core return metric, similar to serve timeline
2. **Break Point Conversion Timeline** - Critical return performance indicator
3. **Break Point Save % Timeline** - Important defensive metric
4. **Combined Break Point Performance Chart** - Comprehensive break point view
5. **Return Performance Radar Chart** - Multi-dimensional overview

### Medium Priority (Implement Second)
6. **Return Performance by Surface Chart** - Surface-specific insights
7. **Return Games Won % Timeline** - Break game performance
8. **Return Performance Comparison Chart** - Multi-metric comparison
9. **Break Point Opportunities vs Conversion Scatter** - Efficiency analysis
10. **Return Performance Trend Analysis Chart** - Long-term trends

### Low Priority (Consider Later)
11. **Return Performance Distribution Histogram** - Consistency visualization
12. **Break Point Conversion Heatmap** - Pattern identification
13. **Return Points Won % vs Opponent Serve Quality** - Advanced analysis
14. **Break Point Save vs Conversion Balance Chart** - Balance analysis
15. **Return Performance by Opponent Rank Chart** - Rank-based analysis
16. **Return Performance Consistency Chart** - Variability visualization
17. **Clutch Return Performance Chart** - Advanced pressure analysis

---

## Technical Considerations

### Data Availability
- ✅ `w_bpFaced`, `l_bpFaced`: Available
- ✅ `w_bpSaved`, `l_bpSaved`: Available
- ✅ `w_bpConverted`, `l_bpConverted`: Available
- ✅ `w_SvGms`, `l_SvGms`: Available
- ✅ Opponent serve stats: Available (from serve_stats.py)
- ✅ Return points won %: Calculated from opponent serve stats
- ✅ Return games won %: Calculated from opponent service games

### Calculation Notes
1. **Return Points Won %**: 
   - If player was winner: 100 - (l_1stWon + l_2ndWon) / l_svpt * 100
   - If player was loser: 100 - (w_1stWon + w_2ndWon) / w_svpt * 100

2. **Break Point Conversion %**:
   - If player was winner: l_bpConverted / (l_bpFaced) * 100
   - If player was loser: w_bpConverted / (w_bpFaced) * 100

3. **Break Point Save %**:
   - If player was winner: w_bpSaved / w_bpFaced * 100
   - If player was loser: l_bpSaved / l_bpFaced * 100

4. **Return Games Won %**:
   - Calculated from opponent's service games lost
   - If player was winner: (opponent_sv_gms - l_SvGms) / opponent_sv_gms * 100

### Implementation Notes
1. **Chart Library**: Use Plotly (consistent with serve charts)
2. **Code Structure**: Create `return/` directory similar to `serve/`
3. **Function Pattern**: Follow `serve_stats.py` pattern for return stats calculation
4. **Integration**: Add to `ui/display/ui_display.py` in `_render_return_tab()`
5. **Filtering**: Respect same filters as serve tab (year, opponent, tournament, surfaces)

### Code Structure Recommendations
```
return/
├── __init__.py
├── return_stats.py          # Calculation functions (similar to serve_stats.py)
├── return_timeline.py       # Return points won % timeline
├── break_point_timeline.py  # Break point conversion/save timeline
├── return_radar_chart.py    # Radar chart for return stats
├── return_surface_chart.py  # Surface performance chart
└── combined_return_charts.py # Combined chart creation
```

---

## User Experience Considerations

### Chart Selection
- Consider adding chart type selector dropdown (similar to serve tab)
- Allow users to switch between different return chart views
- Maintain filter state across chart changes

### Chart Combinations
- Some charts work well together (e.g., Timeline + Surface Chart)
- Consider multi-chart layouts for comprehensive view
- Allow side-by-side comparison of different return metrics

### Comparison Features
- Enable opponent comparison (similar to serve tab)
- Show player vs tour average
- Compare across different periods

### Accessibility
- Ensure charts are keyboard navigable
- Provide alt text for screen readers
- Use color-blind friendly palettes
- Include clear labels and legends

---

## Relationship to Serve Tab

### Complementary Metrics
- Serve tab focuses on serving performance
- Return tab focuses on return performance
- Together they provide complete match performance picture

### Shared Patterns
- Similar chart types (timeline, radar, surface)
- Similar calculation patterns (opponent perspective)
- Similar filtering and comparison features

### Integration Opportunities
- Combined serve/return performance dashboard
- Serve vs Return balance analysis
- Overall match performance metrics

---

## Next Steps

1. **Create Return Stats Module**: Build `return/return_stats.py` similar to `serve/serve_stats.py`
2. **Implement Core Charts**: Start with high-priority charts (timeline, break points)
3. **Test Calculations**: Validate return statistics calculations
4. **Integrate UI**: Add charts to `_render_return_tab()` method
5. **Add Filtering**: Ensure charts respect filter settings
6. **Document**: Update documentation with return chart capabilities

---

## Questions for Decision Making

1. **Which return metrics are most important for your use case?**
2. **Do you want opponent comparison features (like serve tab)?**
3. **Should return charts mirror serve chart structure?**
4. **What level of detail is needed for break point analysis?**
5. **Are there specific return insights you want to highlight?**

---

*Document Created: 2024*
*Last Updated: 2024*

