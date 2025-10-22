"""
ML Dashboard utilities for AskTennis AI application.
Handles Streamlit display components for ML analytics.
Extracted from ml_analytics.py for better modularity.
"""

import streamlit as st
from typing import Dict, Any


class MLDashboard:
    """
    Centralized ML dashboard class for tennis application.
    Handles Streamlit display components for ML analytics.
    """
    
    def __init__(self):
        """Initialize the ML dashboard."""
        pass
    
    def display_ml_analytics(self, analyzer):
        """Display ML analytics in Streamlit."""
        st.subheader("🤖 ML Analytics Dashboard")
        
        if st.button("🔍 Analyze Log Files"):
            with st.spinner("Analyzing log files..."):
                report = analyzer.generate_insights_report()
                
                if 'error' in report:
                    st.error(report['error'])
                    return
                
                # Display insights
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Log Entries", report['total_log_entries'])
                    
                    if 'query_analysis' in report and 'total_queries' in report['query_analysis']:
                        st.metric("Total User Queries", report['query_analysis']['total_queries'])
                        st.metric("Unique Sessions", report['query_analysis']['unique_sessions'])
                
                with col2:
                    if 'performance_analysis' in report and 'avg_execution_time' in report['performance_analysis']:
                        st.metric("Avg Query Time", f"{report['performance_analysis']['avg_execution_time']}s")
                        st.metric("Total DB Queries", report['performance_analysis']['total_db_queries'])
                
                # Query patterns
                self._display_query_patterns(report)
                
                # Performance insights
                self._display_performance_insights(report)
                
                # Error analysis
                self._display_error_analysis(report)
    
    def _display_query_patterns(self, report: Dict[str, Any]):
        """Display query pattern analysis."""
        if 'query_analysis' in report:
            st.subheader("📊 Query Patterns")
            query_analysis = report['query_analysis']
            
            if 'query_categories' in query_analysis:
                st.write("**Query Categories:**")
                for category, count in query_analysis['query_categories'].items():
                    st.write(f"- {category.replace('_', ' ').title()}: {count}")
            
            if 'most_common_words' in query_analysis:
                st.write("**Most Common Words:**")
                for word, count in list(query_analysis['most_common_words'].items())[:5]:
                    st.write(f"- {word}: {count}")
            
            # Tennis terminology analysis
            self._display_tennis_terminology(query_analysis)
            
            # Coverage issues analysis
            self._display_coverage_issues(query_analysis)
    
    def _display_tennis_terminology(self, query_analysis: Dict[str, Any]):
        """Display tennis terminology analysis."""
        if 'tennis_terminology' in query_analysis:
            st.subheader("🎾 Tennis Terminology Analysis")
            terminology = query_analysis['tennis_terminology']
            
            if 'terminology_coverage' in terminology:
                coverage = terminology['terminology_coverage']
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Surface Queries", coverage.get('surface_queries', 0))
                with col2:
                    st.metric("Tour Queries", coverage.get('tour_queries', 0))
                with col3:
                    st.metric("Hand Queries", coverage.get('hand_queries', 0))
                with col4:
                    st.metric("Round Queries", coverage.get('round_queries', 0))
                
                st.metric("Terminology Usage", f"{coverage.get('terminology_usage_percentage', 0)}%")
                st.metric("Colloquial Terms Found", coverage.get('colloquial_terms_found', 0))
            
            # Surface terminology breakdown
            if 'surface_usage' in terminology:
                st.write("**Surface Terminology Usage:**")
                for surface, count in terminology['surface_usage'].items():
                    if count > 0:
                        st.write(f"- {surface.title()}: {count} queries")
            
            # Tour terminology breakdown
            if 'tour_usage' in terminology:
                st.write("**Tour Terminology Usage:**")
                for tour, count in terminology['tour_usage'].items():
                    if count > 0:
                        st.write(f"- {tour.upper()}: {count} queries")
            
            # Hand terminology breakdown
            if 'hand_usage' in terminology:
                st.write("**Hand Terminology Usage:**")
                for hand, count in terminology['hand_usage'].items():
                    if count > 0:
                        st.write(f"- {hand.title()}-handed: {count} queries")
            
            # Round terminology breakdown
            if 'round_usage' in terminology:
                st.write("**Round Terminology Usage:**")
                for round_type, count in terminology['round_usage'].items():
                    if count > 0:
                        st.write(f"- {round_type.replace('_', ' ').title()}: {count} queries")
            
            # Colloquial terms detected
            if 'colloquial_terms_detected' in terminology and terminology['colloquial_terms_detected']:
                st.write("**Colloquial Tennis Terms Detected:**")
                for term in terminology['colloquial_terms_detected'][:10]:  # Show first 10
                    st.write(f"- {term}")
                if len(terminology['colloquial_terms_detected']) > 10:
                    st.write(f"... and {len(terminology['colloquial_terms_detected']) - 10} more")
            
            # Mapping opportunities
            if 'mapping_opportunities' in terminology and terminology['mapping_opportunities']:
                st.write("**Terminology Improvement Opportunities:**")
                for opportunity in terminology['mapping_opportunities']:
                    st.write(f"💡 {opportunity}")
    
    def _display_coverage_issues(self, query_analysis: Dict[str, Any]):
        """Display coverage issues analysis."""
        if 'coverage_issues' in query_analysis:
            st.subheader("🚨 Coverage Issues Detected")
            coverage = query_analysis['coverage_issues']
            
            if 'total_incomplete_queries' in coverage:
                st.warning(f"⚠️ Found {coverage['total_incomplete_queries']} queries with incomplete coverage")
            
            if 'basel_queries' in coverage and coverage['basel_queries']:
                st.write("**Basel Tournament Queries:**")
                for query in coverage['basel_queries']:
                    st.write(f"- {query}")
            
            if 'rome_queries' in coverage and coverage['rome_queries']:
                st.write("**Rome Tournament Queries:**")
                for query in coverage['rome_queries']:
                    st.write(f"- {query}")
            
            if 'recommendations' in coverage:
                st.write("**ML Recommendations:**")
                for rec in coverage['recommendations']:
                    st.write(f"✅ {rec}")
            
            if 'sql_improvements' in coverage:
                st.write("**SQL Improvements:**")
                for imp in coverage['sql_improvements']:
                    st.write(f"🔧 {imp}")
    
    def _display_performance_insights(self, report: Dict[str, Any]):
        """Display performance insights."""
        if 'performance_analysis' in report:
            st.subheader("⚡ Performance Insights")
            perf_analysis = report['performance_analysis']
            
            if 'performance_distribution' in perf_analysis:
                dist = perf_analysis['performance_distribution']
                st.write(f"**Query Performance:**")
                st.write(f"- Fast queries (<1s): {dist.get('fast_queries', 0)}")
                st.write(f"- Medium queries (1-5s): {dist.get('medium_queries', 0)}")
                st.write(f"- Slow queries (>5s): {dist.get('slow_queries', 0)}")
            
            if 'performance_recommendations' in perf_analysis:
                st.write("**Recommendations:**")
                for rec in perf_analysis['performance_recommendations']:
                    st.write(f"- {rec}")
    
    def _display_error_analysis(self, report: Dict[str, Any]):
        """Display error analysis."""
        if 'error_analysis' in report:
            st.subheader("🚨 Error Analysis")
            error_analysis = report['error_analysis']
            
            if 'total_errors' in error_analysis:
                st.metric("Total Errors", error_analysis['total_errors'])
            
            if 'error_recommendations' in error_analysis:
                st.write("**Error Prevention:**")
                for rec in error_analysis['error_recommendations']:
                    st.write(f"- {rec}")
