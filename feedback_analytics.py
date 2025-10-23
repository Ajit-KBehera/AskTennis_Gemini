"""
Feedback Analytics Script for AskTennis AI
Analyzes user feedback data to improve ML analytics and system performance.
"""

import json
import os
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter


def analyze_feedback_data(days_back=7):
    """
    Analyze feedback data from the last N days.
    
    Args:
        days_back: Number of days to analyze (default: 7)
    """
    feedback_dir = "logs/feedback"
    
    if not os.path.exists(feedback_dir):
        print("❌ No feedback directory found. No feedback data to analyze.")
        return
    
    # Get all feedback files from the last N days
    feedback_files = []
    for i in range(days_back):
        date = datetime.now() - timedelta(days=i)
        file_path = os.path.join(feedback_dir, f"feedback_{date.strftime('%Y%m%d')}.jsonl")
        if os.path.exists(file_path):
            feedback_files.append(file_path)
    
    if not feedback_files:
        print(f"❌ No feedback files found for the last {days_back} days.")
        return
    
    # Load all feedback data
    all_feedback = []
    for file_path in feedback_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_feedback.append(json.loads(line.strip()))
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
    
    if not all_feedback:
        print("❌ No feedback data found in files.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_feedback)
    
    print("🚀 AskTennis AI Feedback Analytics")
    print("=" * 50)
    print(f"📊 Analyzing {len(df)} feedback entries from the last {days_back} days")
    print()
    
    # Basic statistics
    print("📈 Basic Statistics:")
    print(f"  Total feedback entries: {len(df)}")
    print(f"  Positive feedback: {len(df[df['feedback_type'] == 'positive'])}")
    print(f"  Negative feedback: {len(df[df['feedback_type'] == 'negative'])}")
    
    if len(df) > 0:
        positive_rate = len(df[df['feedback_type'] == 'positive']) / len(df) * 100
        print(f"  Positive feedback rate: {positive_rate:.1f}%")
    
    print()
    
    # Processing time analysis
    if 'processing_time' in df.columns:
        print("⏱️ Processing Time Analysis:")
        print(f"  Average processing time: {df['processing_time'].mean():.2f} seconds")
        print(f"  Median processing time: {df['processing_time'].median():.2f} seconds")
        print(f"  Fastest response: {df['processing_time'].min():.2f} seconds")
        print(f"  Slowest response: {df['processing_time'].max():.2f} seconds")
        print()
    
    # Response length analysis
    if 'response_length' in df.columns:
        print("📝 Response Length Analysis:")
        print(f"  Average response length: {df['response_length'].mean():.0f} characters")
        print(f"  Median response length: {df['response_length'].median():.0f} characters")
        print()
    
    # Query type analysis (basic keyword analysis)
    print("🔍 Query Analysis:")
    all_queries = df['user_question'].tolist()
    
    # Common keywords in queries
    all_words = []
    for query in all_queries:
        words = query.lower().split()
        all_words.extend(words)
    
    word_counts = Counter(all_words)
    common_words = word_counts.most_common(10)
    
    print("  Most common words in queries:")
    for word, count in common_words:
        if len(word) > 2:  # Filter out short words
            print(f"    '{word}': {count} times")
    
    print()
    
    # Feedback by time of day
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        print("🕐 Feedback by Hour of Day:")
        hourly_feedback = df.groupby('hour').size()
        for hour in sorted(hourly_feedback.index):
            count = hourly_feedback[hour]
            print(f"  {hour:02d}:00 - {count} feedback entries")
    
    print()
    print("✅ Feedback analysis complete!")
    print("💡 Use this data to improve query responses and system performance.")


def show_recent_feedback(limit=10):
    """
    Show recent feedback entries.
    
    Args:
        limit: Number of recent entries to show (default: 10)
    """
    feedback_dir = "logs/feedback"
    
    if not os.path.exists(feedback_dir):
        print("❌ No feedback directory found.")
        return
    
    # Get the most recent feedback file
    today = datetime.now()
    feedback_file = os.path.join(feedback_dir, f"feedback_{today.strftime('%Y%m%d')}.jsonl")
    
    if not os.path.exists(feedback_file):
        print("❌ No feedback file found for today.")
        return
    
    # Load recent feedback
    recent_feedback = []
    try:
        with open(feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    recent_feedback.append(json.loads(line.strip()))
    except Exception as e:
        print(f"⚠️ Error reading feedback file: {e}")
        return
    
    if not recent_feedback:
        print("❌ No feedback data found for today.")
        return
    
    print(f"📋 Recent Feedback (Last {min(limit, len(recent_feedback))} entries):")
    print("=" * 60)
    
    for i, feedback in enumerate(recent_feedback[-limit:], 1):
        timestamp = feedback.get('timestamp', 'Unknown')
        feedback_type = feedback.get('feedback_type', 'Unknown')
        query = feedback.get('user_question', 'Unknown')[:50] + "..." if len(feedback.get('user_question', '')) > 50 else feedback.get('user_question', 'Unknown')
        processing_time = feedback.get('processing_time', 0)
        
        emoji = "👍" if feedback_type == "positive" else "👎"
        print(f"{i:2d}. {emoji} {feedback_type.upper()} - {query}")
        print(f"    Time: {timestamp} | Processing: {processing_time:.2f}s")
        print()


if __name__ == "__main__":
    print("🎾 AskTennis AI Feedback Analytics")
    print("=" * 40)
    print()
    
    # Show recent feedback
    show_recent_feedback(5)
    print()
    
    # Analyze feedback data
    analyze_feedback_data(7)
