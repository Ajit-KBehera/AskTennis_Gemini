"""
Analysis Service for Enhanced UI
Provides intelligent analysis and context for chat integration
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import streamlit as st  # pyright: ignore[reportMissingImports]

class AnalysisService:
    """Service for analysis and context generation."""
    
    def __init__(self, db_service):
        """Initialize analysis service."""
        self.db_service = db_service
    
    def generate_analysis_context(self, filters: Dict[str, Any], results_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate context for chat based on analysis results."""
        context = {
            'filters': filters,
            'total_matches': len(results_df),
            'insights': [],
            'suggestions': [],
            'summary': ""
        }
        
        if results_df.empty:
            context['summary'] = "No matches found for the selected criteria."
            context['suggestions'] = [
                "Try selecting a different player",
                "Expand the year range",
                "Remove some filters to see more results"
            ]
            return context
        
        # Generate insights based on data
        insights = []
        
        if filters.get('player') and filters['player'] != "All Players":
            player = filters['player']
            
            # Win rate analysis
            wins = len(results_df[results_df['winner_name'] == player])
            total = len(results_df)
            win_rate = (wins / total * 100) if total > 0 else 0
            insights.append(f"{player} has a {win_rate:.1f}% win rate in these matches")
            
            # Surface analysis
            if 'surface' in results_df.columns:
                surface_stats = results_df[results_df['winner_name'] == player]['surface'].value_counts()
                if not surface_stats.empty:
                    best_surface = surface_stats.index[0]
                    insights.append(f"Best surface: {best_surface} ({surface_stats.iloc[0]} wins)")
            
            # Recent form
            if 'event_date' in results_df.columns:
                recent_matches = results_df.head(5)
                recent_wins = len(recent_matches[recent_matches['winner_name'] == player])
                insights.append(f"Recent form: {recent_wins}/5 wins in last 5 matches")
        
        # Tournament analysis
        if filters.get('tournament') and filters['tournament'] != "All Tournaments":
            tournament = filters['tournament']
            tournament_matches = results_df[results_df['tourney_name'] == tournament]
            if not tournament_matches.empty:
                insights.append(f"Found {len(tournament_matches)} matches at {tournament}")
        
        # Year analysis
        if filters.get('year') and filters['year'] != "All Years":
            year = filters['year']
            year_matches = results_df[results_df['event_year'] == int(year)]
            if not year_matches.empty:
                insights.append(f"Found {len(year_matches)} matches in {year}")
        
        context['insights'] = insights
        
        # Generate smart suggestions
        suggestions = []
        
        if filters.get('player') and filters['player'] != "All Players":
            player = filters['player']
            suggestions.extend([
                f"Show me {player}'s head-to-head record",
                f"What's {player}'s best tournament?",
                f"Show me {player}'s performance by surface",
                f"Who are {player}'s toughest opponents?",
                f"Show me {player}'s recent form"
            ])
        
        if filters.get('opponent') and filters['opponent'] != "All Opponents":
            opponent = filters['opponent']
            suggestions.extend([
                f"Compare {filters.get('player', 'players')} vs {opponent}",
                f"Show me their head-to-head history",
                f"Who has the advantage in their rivalry?"
            ])
        
        if filters.get('tournament') and filters['tournament'] != "All Tournaments":
            tournament = filters['tournament']
            suggestions.extend([
                f"Show me {tournament} winners",
                f"Who performs best at {tournament}?",
                f"Show me {tournament} statistics"
            ])
        
        context['suggestions'] = suggestions[:5]  # Limit to 5 suggestions
        
        # Generate summary
        summary_parts = []
        if filters.get('player') and filters['player'] != "All Players":
            summary_parts.append(f"Analysis for {filters['player']}")
        if filters.get('opponent') and filters['opponent'] != "All Opponents":
            summary_parts.append(f"vs {filters['opponent']}")
        if filters.get('tournament') and filters['tournament'] != "All Tournaments":
            summary_parts.append(f"at {filters['tournament']}")
        if filters.get('year') and filters['year'] != "All Years":
            summary_parts.append(f"in {filters['year']}")
        if filters.get('surface') and filters['surface'] != "All Surfaces":
            summary_parts.append(f"on {filters['surface']}")
        
        context['summary'] = " ".join(summary_parts) if summary_parts else "General analysis"
        
        return context
    
    def get_smart_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get smart suggestions based on current context."""
        suggestions = []
        
        if context.get('total_matches', 0) > 0:
            suggestions.extend([
                "Show me the match details",
                "What's the win rate?",
                "Show me performance by surface",
                "Who are the top performers?",
                "Show me recent trends"
            ])
        
        if context.get('filters', {}).get('player') and context['filters']['player'] != "All Players":
            player = context['filters']['player']
            suggestions.extend([
                f"Show me {player}'s career statistics",
                f"What's {player}'s best year?",
                f"Show me {player}'s tournament wins",
                f"Compare {player} with other players"
            ])
        
        return suggestions[:8]  # Limit to 8 suggestions
    
    def generate_enhanced_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """Enhance user query with context information."""
        enhanced_query = user_query
        
        # Add context if relevant
        if context.get('filters', {}).get('player') and context['filters']['player'] != "All Players":
            player = context['filters']['player']
            if player.lower() not in user_query.lower():
                enhanced_query = f"{user_query} for {player}"
        
        if context.get('filters', {}).get('tournament') and context['filters']['tournament'] != "All Tournaments":
            tournament = context['filters']['tournament']
            if tournament.lower() not in user_query.lower():
                enhanced_query = f"{enhanced_query} at {tournament}"
        
        return enhanced_query
