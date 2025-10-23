"""
Export Service for Enhanced UI
Provides data export and visualization capabilities
"""

import pandas as pd
import io
import base64
from typing import Dict, Any, Optional
import streamlit as st

class ExportService:
    """Service for data export and visualization."""
    
    def __init__(self):
        """Initialize export service."""
        pass
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = "tennis_analysis.csv") -> bytes:
        """Export DataFrame to CSV."""
        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            return csv_data.encode('utf-8')
        except Exception as e:
            st.error(f"Error exporting to CSV: {e}")
            return b""
    
    def export_to_excel(self, df: pd.DataFrame, filename: str = "tennis_analysis.xlsx") -> bytes:
        """Export DataFrame to Excel."""
        try:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Match Results', index=False)
            return excel_buffer.getvalue()
        except Exception as e:
            st.error(f"Error exporting to Excel: {e}")
            return b""
    
    def create_download_link(self, data: bytes, filename: str, file_type: str) -> str:
        """Create download link for file."""
        try:
            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/{file_type};base64,{b64}" download="{filename}">Download {filename}</a>'
            return href
        except Exception as e:
            st.error(f"Error creating download link: {e}")
            return ""
    
    def generate_summary_report(self, df: pd.DataFrame, context: Dict[str, Any]) -> str:
        """Generate a summary report of the analysis."""
        if df.empty:
            return "No data available for analysis."
        
        report = []
        report.append("# Tennis Analysis Report\n")
        
        # Basic statistics
        report.append(f"**Total Matches:** {len(df)}")
        
        if 'winner_name' in df.columns and 'loser_name' in df.columns:
            unique_players = set(df['winner_name'].tolist() + df['loser_name'].tolist())
            report.append(f"**Unique Players:** {len(unique_players)}")
        
        if 'tourney_name' in df.columns:
            unique_tournaments = df['tourney_name'].nunique()
            report.append(f"**Unique Tournaments:** {unique_tournaments}")
        
        if 'event_year' in df.columns:
            year_range = f"{df['event_year'].min()}-{df['event_year'].max()}"
            report.append(f"**Year Range:** {year_range}")
        
        # Player-specific analysis
        if context.get('filters', {}).get('player') and context['filters']['player'] != "All Players":
            player = context['filters']['player']
            wins = len(df[df['winner_name'] == player])
            total = len(df)
            win_rate = (wins / total * 100) if total > 0 else 0
            
            report.append(f"\n## {player} Analysis")
            report.append(f"**Win Rate:** {win_rate:.1f}% ({wins}/{total})")
            
            # Surface breakdown
            if 'surface' in df.columns:
                surface_stats = df[df['winner_name'] == player]['surface'].value_counts()
                if not surface_stats.empty:
                    report.append(f"\n**Surface Performance:**")
                    for surface, count in surface_stats.items():
                        report.append(f"- {surface}: {count} wins")
        
        # Tournament analysis
        if 'tourney_name' in df.columns:
            tournament_stats = df['tourney_name'].value_counts()
            if not tournament_stats.empty:
                report.append(f"\n**Tournament Breakdown:**")
                for tournament, count in tournament_stats.head(5).items():
                    report.append(f"- {tournament}: {count} matches")
        
        return "\n".join(report)
    
    def create_visualization_data(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for visualizations."""
        viz_data = {}
        
        if df.empty:
            return viz_data
        
        # Win rate by surface
        if 'surface' in df.columns and 'winner_name' in df.columns:
            player = context.get('filters', {}).get('player')
            if player and player != "All Players":
                surface_data = df[df['winner_name'] == player]['surface'].value_counts()
                viz_data['surface_wins'] = surface_data.to_dict()
        
        # Matches by year
        if 'event_year' in df.columns:
            year_data = df['event_year'].value_counts().sort_index()
            viz_data['matches_by_year'] = year_data.to_dict()
        
        # Tournament performance
        if 'tourney_name' in df.columns:
            tournament_data = df['tourney_name'].value_counts()
            viz_data['tournament_matches'] = tournament_data.head(10).to_dict()
        
        return viz_data
