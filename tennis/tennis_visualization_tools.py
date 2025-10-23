"""
Tennis visualization tools for generating Plotly charts.
Provides specialized tools for creating tennis-specific visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
import json


class TennisVisualizationTools:
    """Tennis-specific visualization tools using Plotly."""
    
    @staticmethod
    def create_head_to_head_chart_tool():
        """Create head-to-head bar chart tool."""
        @tool
        def create_head_to_head_chart(data: str, player1: str, player2: str) -> str:
            """
            Create a head-to-head bar chart comparing two players.
            
            Args:
                data: JSON string containing match data with columns: winner_name, loser_name, surface, year, tournament
                player1: First player name
                player2: Second player name
                
            Returns:
                JSON string containing Plotly figure data
            """
            try:
                # Parse the data
                match_data = json.loads(data)
                df = pd.DataFrame(match_data)
                
                if df.empty:
                    return json.dumps({"error": "No data available for head-to-head comparison"})
                
                # Count wins for each player
                player1_wins = len(df[df['winner_name'] == player1])
                player2_wins = len(df[df['winner_name'] == player2])
                
                # Create the bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        name=player1,
                        x=[player1],
                        y=[player1_wins],
                        marker_color='#1f77b4'
                    ),
                    go.Bar(
                        name=player2,
                        x=[player2],
                        y=[player2_wins],
                        marker_color='#ff7f0e'
                    )
                ])
                
                fig.update_layout(
                    title=f"Head-to-Head: {player1} vs {player2}",
                    xaxis_title="Players",
                    yaxis_title="Wins",
                    barmode='group',
                    showlegend=True,
                    height=400
                )
                
                return json.dumps(fig.to_dict())
                
            except Exception as e:
                return json.dumps({"error": f"Failed to create head-to-head chart: {str(e)}"})
        
        return create_head_to_head_chart
    
    @staticmethod
    def create_surface_performance_chart_tool():
        """Create surface performance stacked bar chart tool."""
        @tool
        def create_surface_performance_chart(data: str, player_name: str) -> str:
            """
            Create a surface performance chart showing wins by surface for a player.
            
            Args:
                data: JSON string containing match data with columns: winner_name, loser_name, surface, year
                player_name: Player name to analyze
                
            Returns:
                JSON string containing Plotly figure data
            """
            try:
                # Parse the data
                match_data = json.loads(data)
                df = pd.DataFrame(match_data)
                
                if df.empty:
                    return json.dumps({"error": "No data available for surface performance analysis"})
                
                # Filter for the specific player
                player_matches = df[df['winner_name'] == player_name]
                
                if player_matches.empty:
                    return json.dumps({"error": f"No wins found for {player_name}"})
                
                # Count wins by surface
                surface_wins = player_matches['surface'].value_counts()
                
                # Create the bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=surface_wins.index,
                        y=surface_wins.values,
                        marker_color=['#2E8B57', '#8B4513', '#228B22', '#D2691E'],  # Different colors for each surface
                        text=surface_wins.values,
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title=f"{player_name}'s Performance by Surface",
                    xaxis_title="Surface",
                    yaxis_title="Number of Wins",
                    height=400
                )
                
                return json.dumps(fig.to_dict())
                
            except Exception as e:
                return json.dumps({"error": f"Failed to create surface performance chart: {str(e)}"})
        
        return create_surface_performance_chart
    
    @staticmethod
    def create_ranking_history_chart_tool():
        """Create ranking history line chart tool."""
        @tool
        def create_ranking_history_chart(data: str, player_name: str) -> str:
            """
            Create a ranking history line chart for a player over time.
            
            Args:
                data: JSON string containing ranking data with columns: ranking_date, rank, player
                player_name: Player name to analyze
                
            Returns:
                JSON string containing Plotly figure data
            """
            try:
                # Parse the data
                ranking_data = json.loads(data)
                df = pd.DataFrame(ranking_data)
                
                if df.empty:
                    return json.dumps({"error": "No ranking data available"})
                
                # Filter for the specific player
                player_rankings = df[df['player'] == player_name].copy()
                
                if player_rankings.empty:
                    return json.dumps({"error": f"No ranking data found for {player_name}"})
                
                # Convert ranking_date to datetime
                player_rankings['ranking_date'] = pd.to_datetime(player_rankings['ranking_date'])
                player_rankings = player_rankings.sort_values('ranking_date')
                
                # Create the line chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=player_rankings['ranking_date'],
                    y=player_rankings['rank'],
                    mode='lines+markers',
                    name=player_name,
                    line=dict(color='#1f77b4', width=2),
                    marker=dict(size=4)
                ))
                
                # Invert y-axis so rank 1 is at the top
                fig.update_layout(
                    title=f"{player_name}'s Ranking History",
                    xaxis_title="Date",
                    yaxis_title="Ranking",
                    yaxis=dict(autorange="reversed"),  # Lower rank numbers at top
                    height=400
                )
                
                return json.dumps(fig.to_dict())
                
            except Exception as e:
                return json.dumps({"error": f"Failed to create ranking history chart: {str(e)}"})
        
        return create_ranking_history_chart
    
    @staticmethod
    def create_tournament_performance_chart_tool():
        """Create tournament performance bar chart tool."""
        @tool
        def create_tournament_performance_chart(data: str, player_name: str) -> str:
            """
            Create a tournament performance chart showing wins by tournament for a player.
            
            Args:
                data: JSON string containing match data with columns: winner_name, loser_name, tourney_name, year
                player_name: Player name to analyze
                
            Returns:
                JSON string containing Plotly figure data
            """
            try:
                # Parse the data
                match_data = json.loads(data)
                df = pd.DataFrame(match_data)
                
                if df.empty:
                    return json.dumps({"error": "No data available for tournament performance analysis"})
                
                # Filter for the specific player
                player_matches = df[df['winner_name'] == player_name]
                
                if player_matches.empty:
                    return json.dumps({"error": f"No wins found for {player_name}"})
                
                # Count wins by tournament
                tournament_wins = player_matches['tourney_name'].value_counts().head(10)  # Top 10 tournaments
                
                # Create the bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=tournament_wins.values,
                        y=tournament_wins.index,
                        orientation='h',
                        marker_color='#2E8B57',
                        text=tournament_wins.values,
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title=f"{player_name}'s Performance by Tournament (Top 10)",
                    xaxis_title="Number of Wins",
                    yaxis_title="Tournament",
                    height=500
                )
                
                return json.dumps(fig.to_dict())
                
            except Exception as e:
                return json.dumps({"error": f"Failed to create tournament performance chart: {str(e)}"})
        
        return create_tournament_performance_chart
    
    @staticmethod
    def create_season_performance_chart_tool():
        """Create season performance line chart tool."""
        @tool
        def create_season_performance_chart(data: str, player_name: str) -> str:
            """
            Create a season performance chart showing wins by year for a player.
            
            Args:
                data: JSON string containing match data with columns: winner_name, loser_name, year
                player_name: Player name to analyze
                
            Returns:
                JSON string containing Plotly figure data
            """
            try:
                # Parse the data
                match_data = json.loads(data)
                df = pd.DataFrame(match_data)
                
                if df.empty:
                    return json.dumps({"error": "No data available for season performance analysis"})
                
                # Filter for the specific player
                player_matches = df[df['winner_name'] == player_name]
                
                if player_matches.empty:
                    return json.dumps({"error": f"No wins found for {player_name}"})
                
                # Count wins by year
                yearly_wins = player_matches['year'].value_counts().sort_index()
                
                # Create the line chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=yearly_wins.index,
                    y=yearly_wins.values,
                    mode='lines+markers',
                    name=player_name,
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=6)
                ))
                
                fig.update_layout(
                    title=f"{player_name}'s Performance by Year",
                    xaxis_title="Year",
                    yaxis_title="Number of Wins",
                    height=400
                )
                
                return json.dumps(fig.to_dict())
                
            except Exception as e:
                return json.dumps({"error": f"Failed to create season performance chart: {str(e)}"})
        
        return create_season_performance_chart
    
    @staticmethod
    def create_all_visualization_tools() -> List:
        """
        Create all tennis visualization tools.
        
        Returns:
            List of all visualization tools
        """
        return [
            TennisVisualizationTools.create_head_to_head_chart_tool(),
            TennisVisualizationTools.create_surface_performance_chart_tool(),
            TennisVisualizationTools.create_ranking_history_chart_tool(),
            TennisVisualizationTools.create_tournament_performance_chart_tool(),
            TennisVisualizationTools.create_season_performance_chart_tool()
        ]
