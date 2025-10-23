"""
Enhanced Feedback-Driven Improvements for AskTennis AI
Uses user feedback to improve SQL queries, AI prompts, and system performance.
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any
import re
import logging
from dataclasses import dataclass
from pathlib import Path
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ImprovementRecommendation:
    """Data class for improvement recommendations."""
    type: str
    issue: str
    solution: str
    priority: str
    confidence: float = 0.0
    impact_score: float = 0.0

@dataclass
class FeedbackMetrics:
    """Data class for feedback metrics."""
    total_feedback: int
    positive_count: int
    negative_count: int
    positive_rate: float
    avg_processing_time: float
    avg_response_length: float

class FeedbackImprovements:
    """
    Analyze feedback data to improve AI/LLM performance and SQL queries.
    """
    
    def __init__(self, feedback_dir: str = "logs/feedback", cache_enabled: bool = True):
        """Initialize the feedback improvements analyzer.
        
        Args:
            feedback_dir: Directory containing feedback files
            cache_enabled: Whether to enable caching for performance
        """
        self.feedback_dir = Path(feedback_dir)
        self.improvements_log = "logs/feedback_improvements.json"
        self.cache_enabled = cache_enabled
        self._cache = {} if cache_enabled else None
        
        # Ensure directories exist
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        # Suppress pandas warnings
        warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
    
    def load_feedback_data(self, days_back: int = 30) -> pd.DataFrame:
        """Load feedback data from the last N days with caching and error handling.
        
        Args:
            days_back: Number of days to look back for feedback data
            
        Returns:
            DataFrame containing feedback data
        """
        cache_key = f"feedback_data_{days_back}"
        
        # Check cache first
        if self.cache_enabled and cache_key in self._cache:
            logger.info("Using cached feedback data")
            return self._cache[cache_key]
        
        feedback_files = []
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            file_path = self.feedback_dir / f"feedback_{date.strftime('%Y%m%d')}.jsonl"
            if file_path.exists():
                feedback_files.append(file_path)
        
        if not feedback_files:
            logger.warning(f"No feedback files found in {self.feedback_dir}")
            return pd.DataFrame()
        
        all_feedback = []
        for file_path in feedback_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():
                            try:
                                feedback_entry = json.loads(line.strip())
                                # Validate required fields
                                if self._validate_feedback_entry(feedback_entry):
                                    all_feedback.append(feedback_entry)
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error in {file_path}:{line_num}: {e}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        if not all_feedback:
            logger.warning("No valid feedback entries found")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_feedback)
        
        # Cache the result
        if self.cache_enabled:
            self._cache[cache_key] = df
        
        logger.info(f"Loaded {len(df)} feedback entries from {len(feedback_files)} files")
        return df
    
    def _validate_feedback_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate a feedback entry has required fields.
        
        Args:
            entry: Feedback entry dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['feedback_type', 'user_question', 'timestamp']
        return all(field in entry for field in required_fields)
    
    def analyze_sql_improvements(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze feedback to identify SQL query improvements with advanced pattern detection.
        
        Args:
            feedback_data: DataFrame containing feedback data
            
        Returns:
            Dictionary containing SQL improvement analysis
        """
        if feedback_data.empty:
            logger.warning("No feedback data available for SQL analysis")
            return {}
        
        # Group by feedback type
        negative_feedback = feedback_data[feedback_data['feedback_type'] == 'negative']
        positive_feedback = feedback_data[feedback_data['feedback_type'] == 'positive']
        
        improvements = {
            'sql_issues': {},
            'successful_patterns': {},
            'recommendations': [],
            'query_complexity_analysis': {},
            'performance_metrics': {}
        }
        
        # Enhanced SQL issue detection with confidence scoring
        if not negative_feedback.empty:
            negative_queries = negative_feedback['user_question'].tolist()
            
            # Advanced pattern matching with regex
            sql_issues = self._detect_sql_issues(negative_queries)
            improvements['sql_issues'] = sql_issues
            
            # Generate recommendations with confidence scores
            recommendations = self._generate_sql_recommendations(sql_issues, negative_feedback)
            improvements['recommendations'].extend(recommendations)
        
        # Analyze successful patterns
        if not positive_feedback.empty:
            positive_queries = positive_feedback['user_question'].tolist()
            successful_patterns = self._analyze_successful_patterns(positive_queries)
            improvements['successful_patterns'] = successful_patterns
        
        # Query complexity analysis
        improvements['query_complexity_analysis'] = self._analyze_query_complexity(feedback_data)
        
        # Performance metrics
        improvements['performance_metrics'] = self._calculate_performance_metrics(feedback_data)
        
        return improvements
    
    def _detect_sql_issues(self, queries: List[str]) -> Dict[str, List[str]]:
        """Detect SQL-related issues in queries with advanced pattern matching."""
        sql_issues = defaultdict(list)
        
        # Enhanced pattern matching
        patterns = {
            'head_to_head_issues': [
                r'\b(head\s*to\s*head|h2h|head-to-head)\b',
                r'\b(versus|vs\.?|against)\b.*\b(versus|vs\.?|against)\b'
            ],
            'date_filtering_issues': [
                r'\b(20\d{2})\b',  # Years 2000-2099
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
                r'\b(spring|summer|fall|winter|autumn)\b'
            ],
            'ranking_issues': [
                r'\b(top\s*\d+|ranking|rank|position|#\d+)\b',
                r'\b(world\s*number|atp\s*rank|wta\s*rank)\b'
            ],
            'tournament_issues': [
                r'\b(wimbledon|french\s*open|us\s*open|australian\s*open|roland\s*garros)\b',
                r'\b(grand\s*slam|masters|atp\s*finals|wta\s*finals)\b'
            ],
            'player_name_issues': [
                r'\b(player|players)\b.*\b(name|names)\b',
                r'\b(who\s*is|who\s*are)\b'
            ]
        }
        
        for query in queries:
            query_lower = query.lower()
            for issue_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, query_lower, re.IGNORECASE):
                        sql_issues[issue_type].append(query)
                        break
        
        return dict(sql_issues)
    
    def _generate_sql_recommendations(self, sql_issues: Dict[str, List[str]], 
                                    negative_feedback: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate SQL improvement recommendations with confidence scoring."""
        recommendations = []
        
        for issue_type, queries in sql_issues.items():
            if queries:
                confidence = min(len(queries) / 10.0, 1.0)  # Confidence based on frequency
                impact_score = len(queries) * 0.1  # Impact based on number of affected queries
                
                recommendation = {
                    'type': 'sql_improvement',
                    'issue': f"{issue_type.replace('_', ' ').title()} detected",
                    'solution': self._get_sql_solution(issue_type),
                    'priority': 'high' if confidence > 0.5 else 'medium',
                    'confidence': confidence,
                    'impact_score': impact_score,
                    'affected_queries': len(queries)
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _get_sql_solution(self, issue_type: str) -> str:
        """Get specific solution for SQL issue type."""
        solutions = {
            'head_to_head_issues': 'Enhance head-to-head SQL to include all match types, proper date filtering, and comprehensive player matching',
            'date_filtering_issues': 'Improve date filtering in SQL queries for year-specific searches and seasonal queries',
            'ranking_issues': 'Optimize ranking queries with proper indexing and efficient aggregation',
            'tournament_issues': 'Enhance tournament-specific SQL with proper tournament name matching and surface filtering',
            'player_name_issues': 'Improve player name matching with fuzzy search and alias handling'
        }
        return solutions.get(issue_type, 'Review and optimize SQL query structure')
    
    def _analyze_successful_patterns(self, queries: List[str]) -> Dict[str, List[str]]:
        """Analyze successful query patterns."""
        patterns = {
            'head_to_head_success': [q for q in queries if re.search(r'\b(head\s*to\s*head|h2h)\b', q.lower())],
            'season_success': [q for q in queries if 'season' in q.lower()],
            'tournament_success': [q for q in queries if any(word in q.lower() for word in ['wimbledon', 'french open', 'us open', 'australian open'])],
            'ranking_success': [q for q in queries if any(word in q.lower() for word in ['top', 'ranking', 'rank'])],
            'player_success': [q for q in queries if any(word in q.lower() for word in ['player', 'tennis player'])]
        }
        return {k: v for k, v in patterns.items() if v}
    
    def _analyze_query_complexity(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze query complexity patterns."""
        if feedback_data.empty:
            return {}
        
        # Calculate complexity metrics
        feedback_data['query_length'] = feedback_data['user_question'].str.len()
        feedback_data['word_count'] = feedback_data['user_question'].str.split().str.len()
        
        complexity_analysis = {
            'avg_query_length': feedback_data['query_length'].mean(),
            'avg_word_count': feedback_data['word_count'].mean(),
            'complexity_by_feedback': feedback_data.groupby('feedback_type').agg({
                'query_length': 'mean',
                'word_count': 'mean'
            }).to_dict()
        }
        
        return complexity_analysis
    
    def _calculate_performance_metrics(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics from feedback data."""
        if feedback_data.empty:
            return {}
        
        metrics = {}
        
        # Processing time analysis
        if 'processing_time' in feedback_data.columns:
            metrics['avg_processing_time'] = feedback_data['processing_time'].mean()
            metrics['processing_time_by_feedback'] = feedback_data.groupby('feedback_type')['processing_time'].mean().to_dict()
        
        # Response length analysis
        if 'response_length' in feedback_data.columns:
            metrics['avg_response_length'] = feedback_data['response_length'].mean()
            metrics['response_length_by_feedback'] = feedback_data.groupby('feedback_type')['response_length'].mean().to_dict()
        
        return metrics
    
    def analyze_ai_prompt_improvements(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze feedback to improve AI prompts with advanced metrics.
        
        Args:
            feedback_data: DataFrame containing feedback data
            
        Returns:
            Dictionary containing AI prompt improvement analysis
        """
        if feedback_data.empty:
            logger.warning("No feedback data available for AI prompt analysis")
            return {}
        
        prompt_improvements = {
            'response_length_analysis': {},
            'processing_time_analysis': {},
            'prompt_recommendations': [],
            'sentiment_analysis': {},
            'query_pattern_analysis': {},
            'performance_correlations': {}
        }
        
        # Analyze response quality based on feedback
        negative_feedback = feedback_data[feedback_data['feedback_type'] == 'negative']
        positive_feedback = feedback_data[feedback_data['feedback_type'] == 'positive']
        
        if not negative_feedback.empty and not positive_feedback.empty:
            # Enhanced response length analysis
            prompt_improvements['response_length_analysis'] = self._analyze_response_lengths(
                negative_feedback, positive_feedback
            )
            
            # Enhanced processing time analysis
            prompt_improvements['processing_time_analysis'] = self._analyze_processing_times(
                negative_feedback, positive_feedback
            )
            
            # Sentiment analysis of queries
            prompt_improvements['sentiment_analysis'] = self._analyze_query_sentiment(feedback_data)
            
            # Query pattern analysis
            prompt_improvements['query_pattern_analysis'] = self._analyze_query_patterns(feedback_data)
            
            # Performance correlations
            prompt_improvements['performance_correlations'] = self._analyze_performance_correlations(feedback_data)
            
            # Generate enhanced recommendations
            recommendations = self._generate_prompt_recommendations(
                prompt_improvements, negative_feedback, positive_feedback
            )
            prompt_improvements['prompt_recommendations'] = recommendations
        
        return prompt_improvements
    
    def _analyze_response_lengths(self, negative_feedback: pd.DataFrame, 
                                positive_feedback: pd.DataFrame) -> Dict[str, Any]:
        """Analyze response length patterns."""
        if 'response_length' not in negative_feedback.columns or 'response_length' not in positive_feedback.columns:
            return {}
        
        neg_avg_length = negative_feedback['response_length'].mean()
        pos_avg_length = positive_feedback['response_length'].mean()
        
        return {
            'negative_avg_length': neg_avg_length,
            'positive_avg_length': pos_avg_length,
            'length_difference': pos_avg_length - neg_avg_length,
            'length_ratio': pos_avg_length / neg_avg_length if neg_avg_length > 0 else 0,
            'negative_std': negative_feedback['response_length'].std(),
            'positive_std': positive_feedback['response_length'].std()
        }
    
    def _analyze_processing_times(self, negative_feedback: pd.DataFrame, 
                                positive_feedback: pd.DataFrame) -> Dict[str, Any]:
        """Analyze processing time patterns."""
        if 'processing_time' not in negative_feedback.columns or 'processing_time' not in positive_feedback.columns:
            return {}
        
        neg_avg_time = negative_feedback['processing_time'].mean()
        pos_avg_time = positive_feedback['processing_time'].mean()
        
        return {
            'negative_avg_time': neg_avg_time,
            'positive_avg_time': pos_avg_time,
            'time_difference': pos_avg_time - neg_avg_time,
            'time_ratio': pos_avg_time / neg_avg_time if neg_avg_time > 0 else 0,
            'negative_std': negative_feedback['processing_time'].std(),
            'positive_std': positive_feedback['processing_time'].std()
        }
    
    def _analyze_query_sentiment(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment patterns in queries."""
        # Simple sentiment analysis based on query content
        sentiment_indicators = {
            'positive_words': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'],
            'negative_words': ['bad', 'terrible', 'awful', 'horrible', 'worst', 'disappointing'],
            'question_words': ['what', 'how', 'when', 'where', 'why', 'who', 'which'],
            'comparison_words': ['better', 'worse', 'best', 'worst', 'compare', 'versus']
        }
        
        sentiment_analysis = {}
        for sentiment_type, words in sentiment_indicators.items():
            count = 0
            for query in feedback_data['user_question']:
                if any(word in query.lower() for word in words):
                    count += 1
            sentiment_analysis[sentiment_type] = count
        
        return sentiment_analysis
    
    def _analyze_query_patterns(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze query patterns and complexity."""
        patterns = {
            'question_marks': feedback_data['user_question'].str.count('\?').sum(),
            'exclamation_marks': feedback_data['user_question'].str.count('\!').sum(),
            'avg_sentence_length': feedback_data['user_question'].str.split('.').str.len().mean(),
            'complex_queries': len(feedback_data[feedback_data['user_question'].str.len() > 100]),
            'simple_queries': len(feedback_data[feedback_data['user_question'].str.len() <= 50])
        }
        
        return patterns
    
    def _analyze_performance_correlations(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between different metrics."""
        correlations = {}
        
        numeric_columns = feedback_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 1:
            correlation_matrix = feedback_data[numeric_columns].corr()
            correlations['correlation_matrix'] = correlation_matrix.to_dict()
        
        return correlations
    
    def _generate_prompt_recommendations(self, prompt_improvements: Dict[str, Any],
                                       negative_feedback: pd.DataFrame,
                                       positive_feedback: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate AI prompt improvement recommendations."""
        recommendations = []
        
        # Response length recommendations
        length_analysis = prompt_improvements.get('response_length_analysis', {})
        if length_analysis.get('length_ratio', 0) < 0.8:
            recommendations.append({
                'type': 'prompt_improvement',
                'issue': 'Negative feedback responses are significantly shorter',
                'solution': 'Enhance prompts to generate more comprehensive and detailed responses for complex queries',
                'priority': 'high',
                'confidence': 0.8,
                'impact_score': 0.7
            })
        
        # Processing time recommendations
        time_analysis = prompt_improvements.get('processing_time_analysis', {})
        if time_analysis.get('time_ratio', 0) > 1.5:
            recommendations.append({
                'type': 'prompt_optimization',
                'issue': 'Negative feedback queries take significantly longer to process',
                'solution': 'Optimize prompts for faster processing and add query complexity detection',
                'priority': 'medium',
                'confidence': 0.6,
                'impact_score': 0.5
            })
        
        # Query pattern recommendations
        pattern_analysis = prompt_improvements.get('query_pattern_analysis', {})
        if pattern_analysis.get('complex_queries', 0) > pattern_analysis.get('simple_queries', 0):
            recommendations.append({
                'type': 'prompt_enhancement',
                'issue': 'High ratio of complex queries with negative feedback',
                'solution': 'Enhance prompts to better handle complex, multi-part queries',
                'priority': 'high',
                'confidence': 0.7,
                'impact_score': 0.8
            })
        
        return recommendations
    
    def generate_improvement_plan(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate a comprehensive improvement plan based on feedback with advanced analytics.
        
        Args:
            feedback_data: DataFrame containing feedback data
            
        Returns:
            Dictionary containing comprehensive improvement plan
        """
        if feedback_data.empty:
            logger.warning("No feedback data available for analysis")
            return {"message": "No feedback data available for analysis"}
        
        # Calculate comprehensive metrics
        metrics = self._calculate_feedback_metrics(feedback_data)
        
        improvement_plan = {
            'timestamp': datetime.now().isoformat(),
            'analysis_version': '2.0',
            'metrics': metrics,
            'sql_improvements': self.analyze_sql_improvements(feedback_data),
            'prompt_improvements': self.analyze_ai_prompt_improvements(feedback_data),
            'action_items': [],
            'priority_matrix': {},
            'success_indicators': {},
            'risk_assessment': {}
        }
        
        # Generate prioritized action items
        action_items = self._generate_prioritized_actions(improvement_plan)
        improvement_plan['action_items'] = action_items
        
        # Generate priority matrix
        improvement_plan['priority_matrix'] = self._create_priority_matrix(improvement_plan)
        
        # Generate success indicators
        improvement_plan['success_indicators'] = self._generate_success_indicators(feedback_data)
        
        # Generate risk assessment
        improvement_plan['risk_assessment'] = self._assess_improvement_risks(improvement_plan)
        
        return improvement_plan
    
    def _calculate_feedback_metrics(self, feedback_data: pd.DataFrame) -> FeedbackMetrics:
        """Calculate comprehensive feedback metrics."""
        positive_count = len(feedback_data[feedback_data['feedback_type'] == 'positive'])
        negative_count = len(feedback_data[feedback_data['feedback_type'] == 'negative'])
        total_feedback = len(feedback_data)
        
        return FeedbackMetrics(
            total_feedback=total_feedback,
            positive_count=positive_count,
            negative_count=negative_count,
            positive_rate=(positive_count / total_feedback * 100) if total_feedback > 0 else 0,
            avg_processing_time=feedback_data.get('processing_time', pd.Series([0])).mean(),
            avg_response_length=feedback_data.get('response_length', pd.Series([0])).mean()
        )
    
    def _generate_prioritized_actions(self, improvement_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized action items based on analysis."""
        action_items = []
        
        # SQL improvements
        sql_improvements = improvement_plan.get('sql_improvements', {})
        sql_issues = sql_improvements.get('sql_issues', {})
        
        for issue_type, queries in sql_issues.items():
            if queries:
                priority = 'high' if len(queries) >= 3 else 'medium'
                action_items.append({
                    'id': f"sql_{issue_type}",
                    'priority': priority,
                    'action': f"Fix {issue_type.replace('_', ' ').title()}",
                    'description': f"Improve {len(queries)} failing {issue_type.replace('_', ' ')} queries",
                    'estimated_effort': 'medium',
                    'impact_score': min(len(queries) / 5.0, 1.0),
                    'category': 'sql_optimization'
                })
        
        # Prompt improvements
        prompt_improvements = improvement_plan.get('prompt_improvements', {})
        prompt_recommendations = prompt_improvements.get('prompt_recommendations', [])
        
        for rec in prompt_recommendations:
            action_items.append({
                'id': f"prompt_{rec['type']}",
                'priority': rec.get('priority', 'medium'),
                'action': rec['issue'],
                'description': rec['solution'],
                'estimated_effort': 'low',
                'impact_score': rec.get('impact_score', 0.5),
                'category': 'prompt_optimization'
            })
        
        # Sort by priority and impact
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        action_items.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['impact_score']), reverse=True)
        
        return action_items
    
    def _create_priority_matrix(self, improvement_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create a priority matrix for improvement actions."""
        matrix = {
            'high_impact_high_effort': [],
            'high_impact_low_effort': [],
            'low_impact_high_effort': [],
            'low_impact_low_effort': []
        }
        
        action_items = improvement_plan.get('action_items', [])
        for item in action_items:
            impact = item.get('impact_score', 0)
            effort = item.get('estimated_effort', 'medium')
            effort_score = {'low': 1, 'medium': 2, 'high': 3}.get(effort, 2)
            
            if impact >= 0.7 and effort_score >= 2:
                matrix['high_impact_high_effort'].append(item)
            elif impact >= 0.7 and effort_score < 2:
                matrix['high_impact_low_effort'].append(item)
            elif impact < 0.7 and effort_score >= 2:
                matrix['low_impact_high_effort'].append(item)
            else:
                matrix['low_impact_low_effort'].append(item)
        
        return matrix
    
    def _generate_success_indicators(self, feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate success indicators for improvement tracking."""
        indicators = {
            'baseline_metrics': {
                'current_positive_rate': len(feedback_data[feedback_data['feedback_type'] == 'positive']) / len(feedback_data) * 100,
                'avg_processing_time': feedback_data.get('processing_time', pd.Series([0])).mean(),
                'avg_response_length': feedback_data.get('response_length', pd.Series([0])).mean()
            },
            'target_metrics': {
                'target_positive_rate': 85.0,  # Target 85% positive feedback
                'target_processing_time': 2.0,  # Target 2 seconds
                'target_response_length': 500   # Target 500 characters
            },
            'improvement_tracking': {
                'positive_rate_trend': 'stable',  # Would be calculated from historical data
                'processing_time_trend': 'stable',
                'response_quality_trend': 'stable'
            }
        }
        
        return indicators
    
    def _assess_improvement_risks(self, improvement_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with implementing improvements."""
        risks = {
            'high_risk_actions': [],
            'medium_risk_actions': [],
            'low_risk_actions': [],
            'risk_mitigation': []
        }
        
        action_items = improvement_plan.get('action_items', [])
        for item in action_items:
            category = item.get('category', '')
            impact = item.get('impact_score', 0)
            
            if category == 'sql_optimization' and impact > 0.7:
                risks['high_risk_actions'].append({
                    'action': item['action'],
                    'risk': 'Database performance impact',
                    'mitigation': 'Test on staging environment first'
                })
            elif category == 'prompt_optimization':
                risks['low_risk_actions'].append({
                    'action': item['action'],
                    'risk': 'Minimal system impact',
                    'mitigation': 'A/B test with small user group'
                })
        
        return risks
    
    def save_improvements(self, improvement_plan: Dict[str, Any]) -> bool:
        """Save improvement plan to file with enhanced error handling.
        
        Args:
            improvement_plan: Dictionary containing improvement plan
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create backup of existing file
            if Path(self.improvements_log).exists():
                backup_path = f"{self.improvements_log}.backup"
                Path(self.improvements_log).rename(backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Save new improvement plan
            with open(self.improvements_log, 'w', encoding='utf-8') as f:
                json.dump(improvement_plan, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Improvement plan saved to {self.improvements_log}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving improvement plan: {e}")
            return False
    
    def run_analysis(self, days_back: int = 30, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """Run complete feedback analysis and generate improvement plan with enhanced reporting.
        
        Args:
            days_back: Number of days to look back for feedback data
            verbose: Whether to print detailed output
            
        Returns:
            Dictionary containing improvement plan or None if analysis fails
        """
        if verbose:
            print("🚀 Enhanced Feedback-Driven Improvements Analysis v2.0")
            print("=" * 60)
        
        try:
            # Load feedback data
            feedback_data = self.load_feedback_data(days_back)
            
            if feedback_data.empty:
                if verbose:
                    print("❌ No feedback data found for analysis")
                return None
            
            if verbose:
                print(f"📊 Analyzing {len(feedback_data)} feedback entries from last {days_back} days")
            
            # Generate improvement plan
            improvement_plan = self.generate_improvement_plan(feedback_data)
            
            if verbose:
                self._display_analysis_results(improvement_plan)
            
            # Save improvements
            if self.save_improvements(improvement_plan):
                if verbose:
                    print(f"\n💾 Improvement plan saved successfully")
            
            return improvement_plan
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            if verbose:
                print(f"❌ Analysis failed: {e}")
            return None
    
    def _display_analysis_results(self, improvement_plan: Dict[str, Any]) -> None:
        """Display comprehensive analysis results."""
        metrics = improvement_plan.get('metrics', {})
        
        print(f"\n📈 Feedback Summary:")
        print(f"  Total feedback: {metrics.total_feedback}")
        print(f"  Positive rate: {metrics.positive_rate:.1f}%")
        print(f"  Avg processing time: {metrics.avg_processing_time:.2f}s")
        print(f"  Avg response length: {metrics.avg_response_length:.0f} chars")
        
        # Display SQL improvements
        sql_improvements = improvement_plan.get('sql_improvements', {})
        sql_issues = sql_improvements.get('sql_issues', {})
        if sql_issues:
            print(f"\n🔧 SQL Issues Identified:")
            for issue_type, queries in sql_issues.items():
                if queries:
                    print(f"  {issue_type.replace('_', ' ').title()}: {len(queries)} queries")
        
        # Display prompt improvements
        prompt_improvements = improvement_plan.get('prompt_improvements', {})
        prompt_recs = prompt_improvements.get('prompt_recommendations', [])
        if prompt_recs:
            print(f"\n🤖 AI Prompt Improvements:")
            for rec in prompt_recs:
                print(f"  {rec['priority'].upper()}: {rec['issue']}")
        
        # Display action items
        action_items = improvement_plan.get('action_items', [])
        if action_items:
            print(f"\n🎯 Prioritized Action Items:")
            for i, item in enumerate(action_items[:5], 1):  # Show top 5
                print(f"  {i}. {item['priority'].upper()}: {item['action']}")
                print(f"     Impact: {item['impact_score']:.2f} | Category: {item['category']}")
        
        # Display priority matrix
        priority_matrix = improvement_plan.get('priority_matrix', {})
        if priority_matrix:
            print(f"\n📊 Priority Matrix:")
            for category, items in priority_matrix.items():
                if items:
                    print(f"  {category.replace('_', ' ').title()}: {len(items)} items")
        
        # Display success indicators
        success_indicators = improvement_plan.get('success_indicators', {})
        if success_indicators:
            baseline = success_indicators.get('baseline_metrics', {})
            targets = success_indicators.get('target_metrics', {})
            print(f"\n🎯 Success Indicators:")
            print(f"  Current positive rate: {baseline.get('current_positive_rate', 0):.1f}%")
            print(f"  Target positive rate: {targets.get('target_positive_rate', 0):.1f}%")
    
    def generate_report(self, improvement_plan: Dict[str, Any], output_file: str = "feedback_improvement_report.md") -> bool:
        """Generate a comprehensive markdown report from improvement plan.
        
        Args:
            improvement_plan: Dictionary containing improvement plan
            output_file: Path to output markdown file
            
        Returns:
            True if report generated successfully, False otherwise
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# 🎾 AskTennis AI Feedback Improvement Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Executive Summary
                metrics = improvement_plan.get('metrics', {})
                f.write("## 📊 Executive Summary\n\n")
                f.write(f"- **Total Feedback Analyzed:** {metrics.total_feedback}\n")
                f.write(f"- **Positive Feedback Rate:** {metrics.positive_rate:.1f}%\n")
                f.write(f"- **Average Processing Time:** {metrics.avg_processing_time:.2f}s\n")
                f.write(f"- **Average Response Length:** {metrics.avg_response_length:.0f} characters\n\n")
                
                # Action Items
                action_items = improvement_plan.get('action_items', [])
                if action_items:
                    f.write("## 🎯 Recommended Actions\n\n")
                    for i, item in enumerate(action_items, 1):
                        f.write(f"### {i}. {item['action']}\n")
                        f.write(f"- **Priority:** {item['priority'].upper()}\n")
                        f.write(f"- **Impact Score:** {item['impact_score']:.2f}\n")
                        f.write(f"- **Category:** {item['category']}\n")
                        f.write(f"- **Description:** {item['description']}\n\n")
                
                # Risk Assessment
                risk_assessment = improvement_plan.get('risk_assessment', {})
                if risk_assessment:
                    f.write("## ⚠️ Risk Assessment\n\n")
                    for risk_level, risks in risk_assessment.items():
                        if risks and risk_level != 'risk_mitigation':
                            f.write(f"### {risk_level.replace('_', ' ').title()}\n")
                            for risk in risks:
                                f.write(f"- **Action:** {risk['action']}\n")
                                f.write(f"- **Risk:** {risk['risk']}\n")
                                f.write(f"- **Mitigation:** {risk['mitigation']}\n\n")
            
            logger.info(f"✅ Report generated: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        if self.cache_enabled:
            self._cache.clear()
            logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache_enabled:
            return {"cache_enabled": False}
        
        return {
            "cache_enabled": True,
            "cache_size": len(self._cache),
            "cached_keys": list(self._cache.keys())
        }


def main():
    """Run enhanced feedback-driven improvements analysis with advanced features."""
    print("🎾 AskTennis AI Enhanced Feedback-Driven Improvements v2.0")
    print("=" * 70)
    print()
    
    try:
        # Initialize analyzer with enhanced features
        analyzer = FeedbackImprovements(cache_enabled=True)
        
        # Run comprehensive analysis
        improvement_plan = analyzer.run_analysis(days_back=30, verbose=True)
        
        if improvement_plan:
            # Generate markdown report
            report_generated = analyzer.generate_report(improvement_plan)
            
            if report_generated:
                print(f"\n📄 Comprehensive report generated: feedback_improvement_report.md")
            
            # Display cache statistics
            cache_stats = analyzer.get_cache_stats()
            if cache_stats.get('cache_enabled'):
                print(f"\n💾 Cache Statistics:")
                print(f"  Cache size: {cache_stats['cache_size']} items")
                print(f"  Cached keys: {', '.join(cache_stats['cached_keys'])}")
            
            print("\n✅ Enhanced feedback analysis completed!")
            print("💡 Use the generated improvement plan and report to enhance AI/LLM performance")
            print("📊 Check the priority matrix for optimal implementation order")
            
        else:
            print("❌ No improvement plan generated")
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
