"""
Feedback-Driven Improvements for AskTennis AI
Uses user feedback to improve SQL queries, AI prompts, and system performance.
"""

import json
import os
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import re


class FeedbackImprovements:
    """
    Analyze feedback data to improve AI/LLM performance and SQL queries.
    """
    
    def __init__(self):
        self.feedback_dir = "logs/feedback"
        self.improvements_log = "logs/feedback_improvements.json"
    
    def load_feedback_data(self, days_back=30):
        """Load feedback data from the last N days."""
        feedback_files = []
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            file_path = os.path.join(self.feedback_dir, f"feedback_{date.strftime('%Y%m%d')}.jsonl")
            if os.path.exists(file_path):
                feedback_files.append(file_path)
        
        all_feedback = []
        for file_path in feedback_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            all_feedback.append(json.loads(line.strip()))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return pd.DataFrame(all_feedback) if all_feedback else pd.DataFrame()
    
    def analyze_sql_improvements(self, feedback_data):
        """Analyze feedback to identify SQL query improvements."""
        if feedback_data.empty:
            return {}
        
        # Group by feedback type
        negative_feedback = feedback_data[feedback_data['feedback_type'] == 'negative']
        positive_feedback = feedback_data[feedback_data['feedback_type'] == 'positive']
        
        improvements = {
            'sql_issues': {},
            'successful_patterns': {},
            'recommendations': []
        }
        
        # Analyze negative feedback for SQL issues
        if not negative_feedback.empty:
            # Identify common negative feedback patterns
            negative_queries = negative_feedback['user_question'].tolist()
            
            # SQL-related issue detection
            sql_issues = {
                'head_to_head_issues': [q for q in negative_queries if 'head to head' in q.lower() or 'h2h' in q.lower()],
                'date_filtering_issues': [q for q in negative_queries if any(year in q for year in ['2023', '2024', '2022'])],
                'ranking_issues': [q for q in negative_queries if any(word in q.lower() for word in ['top', 'ranking', 'rank'])],
                'tournament_issues': [q for q in negative_queries if any(word in q.lower() for word in ['wimbledon', 'french open', 'us open', 'australian open'])]
            }
            
            improvements['sql_issues'] = sql_issues
            
            # Generate SQL improvement recommendations
            if sql_issues['head_to_head_issues']:
                improvements['recommendations'].append({
                    'type': 'sql_improvement',
                    'issue': 'Head-to-head queries failing',
                    'solution': 'Enhance head-to-head SQL to include all match types and proper date filtering',
                    'priority': 'high'
                })
            
            if sql_issues['date_filtering_issues']:
                improvements['recommendations'].append({
                    'type': 'sql_improvement',
                    'issue': 'Date filtering problems',
                    'solution': 'Improve date filtering in SQL queries for year-specific searches',
                    'priority': 'high'
                })
        
        # Analyze positive feedback for successful patterns
        if not positive_feedback.empty:
            positive_queries = positive_feedback['user_question'].tolist()
            
            successful_patterns = {
                'head_to_head_success': [q for q in positive_queries if 'head to head' in q.lower()],
                'season_success': [q for q in positive_queries if 'season' in q.lower()],
                'tournament_success': [q for q in positive_queries if any(word in q.lower() for word in ['wimbledon', 'french open', 'us open', 'australian open'])]
            }
            
            improvements['successful_patterns'] = successful_patterns
        
        return improvements
    
    def analyze_ai_prompt_improvements(self, feedback_data):
        """Analyze feedback to improve AI prompts."""
        if feedback_data.empty:
            return {}
        
        # Analyze response quality based on feedback
        prompt_improvements = {
            'response_length_analysis': {},
            'processing_time_analysis': {},
            'prompt_recommendations': []
        }
        
        # Analyze response length vs feedback
        negative_feedback = feedback_data[feedback_data['feedback_type'] == 'negative']
        positive_feedback = feedback_data[feedback_data['feedback_type'] == 'positive']
        
        if not negative_feedback.empty and not positive_feedback.empty:
            # Response length analysis
            neg_avg_length = negative_feedback['response_length'].mean()
            pos_avg_length = positive_feedback['response_length'].mean()
            
            prompt_improvements['response_length_analysis'] = {
                'negative_avg_length': neg_avg_length,
                'positive_avg_length': pos_avg_length,
                'length_difference': pos_avg_length - neg_avg_length
            }
            
            # Processing time analysis
            neg_avg_time = negative_feedback['processing_time'].mean()
            pos_avg_time = positive_feedback['processing_time'].mean()
            
            prompt_improvements['processing_time_analysis'] = {
                'negative_avg_time': neg_avg_time,
                'positive_avg_time': pos_avg_time,
                'time_difference': pos_avg_time - neg_avg_time
            }
            
            # Generate prompt improvement recommendations
            if neg_avg_length < pos_avg_length:
                prompt_improvements['prompt_recommendations'].append({
                    'type': 'prompt_improvement',
                    'issue': 'Negative feedback responses are too short',
                    'solution': 'Enhance prompts to generate more comprehensive responses',
                    'priority': 'medium'
                })
            
            if neg_avg_time > pos_avg_time:
                prompt_improvements['prompt_recommendations'].append({
                    'type': 'prompt_improvement',
                    'issue': 'Negative feedback queries take longer to process',
                    'solution': 'Optimize prompts for faster processing of complex queries',
                    'priority': 'medium'
                })
        
        return prompt_improvements
    
    def generate_improvement_plan(self, feedback_data):
        """Generate a comprehensive improvement plan based on feedback."""
        if feedback_data.empty:
            return {"message": "No feedback data available for analysis"}
        
        improvement_plan = {
            'timestamp': datetime.now().isoformat(),
            'total_feedback': len(feedback_data),
            'positive_rate': len(feedback_data[feedback_data['feedback_type'] == 'positive']) / len(feedback_data) * 100,
            'sql_improvements': self.analyze_sql_improvements(feedback_data),
            'prompt_improvements': self.analyze_ai_prompt_improvements(feedback_data),
            'action_items': []
        }
        
        # Generate action items based on analysis
        sql_issues = improvement_plan['sql_improvements'].get('sql_issues', {})
        if sql_issues.get('head_to_head_issues'):
            improvement_plan['action_items'].append({
                'priority': 'high',
                'action': 'Fix head-to-head SQL queries',
                'description': f"Improve {len(sql_issues['head_to_head_issues'])} failing head-to-head queries"
            })
        
        if sql_issues.get('date_filtering_issues'):
            improvement_plan['action_items'].append({
                'priority': 'high',
                'action': 'Fix date filtering in SQL',
                'description': f"Improve {len(sql_issues['date_filtering_issues'])} date-related queries"
            })
        
        return improvement_plan
    
    def save_improvements(self, improvement_plan):
        """Save improvement plan to file."""
        try:
            with open(self.improvements_log, 'w', encoding='utf-8') as f:
                json.dump(improvement_plan, f, indent=2, ensure_ascii=False)
            print(f"✅ Improvement plan saved to {self.improvements_log}")
        except Exception as e:
            print(f"❌ Error saving improvement plan: {e}")
    
    def run_analysis(self, days_back=30):
        """Run complete feedback analysis and generate improvement plan."""
        print("🚀 Feedback-Driven Improvements Analysis")
        print("=" * 50)
        
        # Load feedback data
        feedback_data = self.load_feedback_data(days_back)
        
        if feedback_data.empty:
            print("❌ No feedback data found for analysis")
            return
        
        print(f"📊 Analyzing {len(feedback_data)} feedback entries")
        
        # Generate improvement plan
        improvement_plan = self.generate_improvement_plan(feedback_data)
        
        # Display results
        print(f"\n📈 Feedback Summary:")
        print(f"  Total feedback: {improvement_plan['total_feedback']}")
        print(f"  Positive rate: {improvement_plan['positive_rate']:.1f}%")
        
        # Display SQL improvements
        sql_issues = improvement_plan['sql_improvements'].get('sql_issues', {})
        if sql_issues:
            print(f"\n🔧 SQL Issues Identified:")
            for issue_type, queries in sql_issues.items():
                if queries:
                    print(f"  {issue_type}: {len(queries)} queries")
        
        # Display action items
        action_items = improvement_plan.get('action_items', [])
        if action_items:
            print(f"\n🎯 Action Items:")
            for item in action_items:
                print(f"  {item['priority'].upper()}: {item['action']} - {item['description']}")
        
        # Save improvements
        self.save_improvements(improvement_plan)
        
        return improvement_plan


def main():
    """Run feedback-driven improvements analysis."""
    print("🎾 AskTennis AI Feedback-Driven Improvements")
    print("=" * 60)
    print()
    
    try:
        analyzer = FeedbackImprovements()
        improvement_plan = analyzer.run_analysis(30)
        
        print("\n✅ Feedback analysis completed!")
        print("💡 Use the generated improvement plan to enhance AI/LLM performance")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
