"""
Result analyzer for automated testing framework.
Handles accuracy calculation and response analysis.
"""

import re
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher


class ResultAnalyzer:
    """
    Analyzes test results and calculates accuracy metrics.
    Provides various methods for comparing AI responses with expected answers.
    """
    
    def __init__(self):
        """Initialize the result analyzer."""
        self.similarity_threshold = 0.7
        self.partial_match_threshold = 0.5
    
    def calculate_accuracy(self, ai_answer: str, expected_answer: str, category: str = '') -> float:
        """
        Calculate accuracy score for AI answer.
        
        Args:
            ai_answer: Answer provided by AI
            expected_answer: Expected correct answer
            category: Test category for specialized validation
            
        Returns:
            Accuracy score between 0.0 and 1.0
        """
        if not ai_answer or not expected_answer:
            return 0.0
        
        # Clean and normalize answers
        ai_clean = self._clean_answer(ai_answer)
        expected_clean = self._clean_answer(expected_answer)
        
        # Try different accuracy methods in order of preference
        methods = [
            self._exact_match_accuracy,
            self._numerical_accuracy,
            self._semantic_similarity_accuracy,
            self._keyword_match_accuracy,
            self._partial_match_accuracy
        ]
        
        # For numerical answers, prioritize numerical accuracy
        ai_numbers = self._extract_numbers(ai_clean)
        expected_numbers = self._extract_numbers(expected_clean)
        
        if ai_numbers and expected_numbers:
            # For numerical answers, use numerical accuracy only
            try:
                return min(self._numerical_accuracy(ai_clean, expected_clean), 1.0)
            except Exception:
                return 0.0
        
        # For non-numerical answers, try all methods and take the best
        max_accuracy = 0.0
        for method in methods:
            try:
                accuracy = method(ai_clean, expected_clean)
                max_accuracy = max(max_accuracy, accuracy)
            except Exception:
                continue
        
        return min(max_accuracy, 1.0)
    
    def _clean_answer(self, answer: str) -> str:
        """
        Clean and normalize answer text.
        
        Args:
            answer: Raw answer text
            
        Returns:
            Cleaned answer text
        """
        if not answer:
            return ''
        
        # Convert to lowercase
        cleaned = answer.lower().strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            'the answer is', 'the winner is', 'the result is',
            'the champion is', 'the player is', 'answer:',
            'winner:', 'result:', 'champion:', 'player:'
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _exact_match_accuracy(self, ai_answer: str, expected_answer: str) -> float:
        """
        Calculate exact match accuracy.
        
        Args:
            ai_answer: AI answer
            expected_answer: Expected answer
            
        Returns:
            Accuracy score (1.0 for exact match, 0.0 otherwise)
        """
        if ai_answer == expected_answer:
            return 1.0
        return 0.0
    
    def _semantic_similarity_accuracy(self, ai_answer: str, expected_answer: str) -> float:
        """
        Calculate semantic similarity accuracy using sequence matching.
        
        Args:
            ai_answer: AI answer
            expected_answer: Expected answer
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        similarity = SequenceMatcher(None, ai_answer, expected_answer).ratio()
        return similarity if similarity >= self.similarity_threshold else 0.0
    
    def _numerical_accuracy(self, ai_answer: str, expected_answer: str) -> float:
        """
        Calculate numerical accuracy for numeric answers.
        
        Args:
            ai_answer: AI answer
            expected_answer: Expected answer
            
        Returns:
            Numerical accuracy score
        """
        try:
            # Extract numbers from answers
            ai_numbers = self._extract_numbers(ai_answer)
            expected_numbers = self._extract_numbers(expected_answer)
            
            if not ai_numbers or not expected_numbers:
                return 0.0
            
            # Compare numbers
            if len(ai_numbers) == 1 and len(expected_numbers) == 1:
                ai_num = ai_numbers[0]
                expected_num = expected_numbers[0]
                
                # Exact match gets perfect score
                if ai_num == expected_num:
                    return 1.0
                
                # For non-zero expected numbers, use percentage-based accuracy
                if expected_num == 0:
                    return 1.0 if ai_num == 0 else 0.0
                
                # Calculate percentage difference
                percentage_diff = abs(ai_num - expected_num) / abs(expected_num)
                
                # Use exponential decay for accuracy (more forgiving for small differences)
                if percentage_diff <= 0.1:  # Within 10%
                    return 0.9
                elif percentage_diff <= 0.2:  # Within 20%
                    return 0.7
                elif percentage_diff <= 0.5:  # Within 50%
                    return 0.4
                else:  # More than 50% difference
                    return 0.0
            
            # For multiple numbers, calculate average accuracy
            total_accuracy = 0.0
            min_length = min(len(ai_numbers), len(expected_numbers))
            
            for i in range(min_length):
                if ai_numbers[i] == expected_numbers[i]:
                    accuracy = 1.0
                elif expected_numbers[i] == 0:
                    accuracy = 1.0 if ai_numbers[i] == 0 else 0.0
                else:
                    percentage_diff = abs(ai_numbers[i] - expected_numbers[i]) / abs(expected_numbers[i])
                    if percentage_diff <= 0.1:
                        accuracy = 0.9
                    elif percentage_diff <= 0.2:
                        accuracy = 0.7
                    elif percentage_diff <= 0.5:
                        accuracy = 0.4
                    else:
                        accuracy = 0.0
                total_accuracy += accuracy
            
            return total_accuracy / min_length if min_length > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _extract_numbers(self, text: str) -> List[float]:
        """
        Extract numbers from text.
        
        Args:
            text: Text to extract numbers from
            
        Returns:
            List of extracted numbers
        """
        # Find all numbers in the text
        number_pattern = r'-?\d+\.?\d*'
        matches = re.findall(number_pattern, text)
        
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        
        return numbers
    
    def _partial_match_accuracy(self, ai_answer: str, expected_answer: str) -> float:
        """
        Calculate partial match accuracy.
        
        Args:
            ai_answer: AI answer
            expected_answer: Expected answer
            
        Returns:
            Partial match accuracy score
        """
        # If both answers contain numbers, use numerical accuracy instead
        ai_numbers = self._extract_numbers(ai_answer)
        expected_numbers = self._extract_numbers(expected_answer)
        
        if ai_numbers and expected_numbers:
            # For numerical answers, be more strict
            return 0.0  # Let numerical_accuracy handle this
        
        ai_words = set(ai_answer.split())
        expected_words = set(expected_answer.split())
        
        if not expected_words:
            return 1.0
        
        intersection = ai_words.intersection(expected_words)
        accuracy = len(intersection) / len(expected_words)
        
        return accuracy if accuracy >= self.partial_match_threshold else 0.0
    
    def _keyword_match_accuracy(self, ai_answer: str, expected_answer: str) -> float:
        """
        Calculate keyword match accuracy.
        
        Args:
            ai_answer: AI answer
            expected_answer: Expected answer
            
        Returns:
            Keyword match accuracy score
        """
        # Extract key terms (names, numbers, important words)
        ai_keywords = self._extract_keywords(ai_answer)
        expected_keywords = self._extract_keywords(expected_answer)
        
        if not expected_keywords:
            return 1.0
        
        # Calculate keyword overlap
        intersection = ai_keywords.intersection(expected_keywords)
        accuracy = len(intersection) / len(expected_keywords)
        
        return accuracy if accuracy >= self.partial_match_threshold else 0.0
    
    def _extract_keywords(self, text: str) -> set:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            Set of extracted keywords
        """
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'must', 'shall', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        words = text.lower().split()
        keywords = set()
        
        for word in words:
            # Remove punctuation and check if it's not a stop word
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word and clean_word not in stop_words and len(clean_word) > 2:
                keywords.add(clean_word)
        
        return keywords
    
    def analyze_test_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a list of test results and provide comprehensive metrics.
        
        Args:
            results: List of test result dictionaries
            
        Returns:
            Dictionary containing analysis metrics
        """
        if not results:
            return {}
        
        # Basic statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('status') == 'passed')
        failed_tests = sum(1 for r in results if r.get('status') == 'failed')
        error_tests = sum(1 for r in results if r.get('status') == 'error')
        
        # Accuracy statistics
        accuracy_scores = [r.get('accuracy_score', 0.0) for r in results]
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        max_accuracy = max(accuracy_scores) if accuracy_scores else 0.0
        min_accuracy = min(accuracy_scores) if accuracy_scores else 0.0
        
        # Execution time statistics
        execution_times = [r.get('execution_time', 0.0) for r in results]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        max_execution_time = max(execution_times) if execution_times else 0.0
        min_execution_time = min(execution_times) if execution_times else 0.0
        
        # Category analysis
        category_stats = {}
        for result in results:
            category = result.get('category', 'unknown')
            if category not in category_stats:
                category_stats[category] = {
                    'total': 0,
                    'passed': 0,
                    'avg_accuracy': 0.0,
                    'avg_execution_time': 0.0
                }
            
            category_stats[category]['total'] += 1
            if result.get('status') == 'passed':
                category_stats[category]['passed'] += 1
        
        # Calculate category averages
        for category, stats in category_stats.items():
            category_results = [r for r in results if r.get('category') == category]
            if category_results:
                stats['avg_accuracy'] = sum(r.get('accuracy_score', 0.0) for r in category_results) / len(category_results)
                stats['avg_execution_time'] = sum(r.get('execution_time', 0.0) for r in category_results) / len(category_results)
        
        # Difficulty analysis
        difficulty_stats = {}
        for result in results:
            difficulty = result.get('difficulty', 'unknown')
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {
                    'total': 0,
                    'passed': 0,
                    'avg_accuracy': 0.0
                }
            
            difficulty_stats[difficulty]['total'] += 1
            if result.get('status') == 'passed':
                difficulty_stats[difficulty]['passed'] += 1
        
        # Calculate difficulty averages
        for difficulty, stats in difficulty_stats.items():
            difficulty_results = [r for r in results if r.get('difficulty') == difficulty]
            if difficulty_results:
                stats['avg_accuracy'] = sum(r.get('accuracy_score', 0.0) for r in difficulty_results) / len(difficulty_results)
        
        return {
            'basic_metrics': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'error_tests': error_tests,
                'pass_rate': passed_tests / total_tests if total_tests > 0 else 0.0
            },
            'accuracy_metrics': {
                'average_accuracy': avg_accuracy,
                'max_accuracy': max_accuracy,
                'min_accuracy': min_accuracy,
                'accuracy_distribution': self._calculate_accuracy_distribution(accuracy_scores)
            },
            'performance_metrics': {
                'average_execution_time': avg_execution_time,
                'max_execution_time': max_execution_time,
                'min_execution_time': min_execution_time
            },
            'category_analysis': category_stats,
            'difficulty_analysis': difficulty_stats
        }
    
    def _calculate_accuracy_distribution(self, accuracy_scores: List[float]) -> Dict[str, int]:
        """
        Calculate accuracy score distribution.
        
        Args:
            accuracy_scores: List of accuracy scores
            
        Returns:
            Dictionary with accuracy ranges and counts
        """
        distribution = {
            'excellent (0.9-1.0)': 0,
            'good (0.7-0.9)': 0,
            'fair (0.5-0.7)': 0,
            'poor (0.0-0.5)': 0
        }
        
        for score in accuracy_scores:
            if score >= 0.9:
                distribution['excellent (0.9-1.0)'] += 1
            elif score >= 0.7:
                distribution['good (0.7-0.9)'] += 1
            elif score >= 0.5:
                distribution['fair (0.5-0.7)'] += 1
            else:
                distribution['poor (0.0-0.5)'] += 1
        
        return distribution
    
    def identify_problematic_tests(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify tests that consistently fail or have low accuracy.
        
        Args:
            results: List of test result dictionaries
            
        Returns:
            List of problematic test results
        """
        problematic = []
        
        for result in results:
            accuracy = result.get('accuracy_score', 0.0)
            status = result.get('status', 'failed')
            
            # Identify problematic tests
            if (accuracy < 0.3 or 
                status == 'error' or 
                result.get('execution_time', 0) > 30.0):
                problematic.append(result)
        
        return problematic
    
    def generate_improvement_suggestions(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Generate suggestions for improving test performance.
        
        Args:
            results: List of test result dictionaries
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Analyze results
        analysis = self.analyze_test_results(results)
        
        # Check overall performance
        pass_rate = analysis['basic_metrics']['pass_rate']
        avg_accuracy = analysis['accuracy_metrics']['average_accuracy']
        
        if pass_rate < 0.7:
            suggestions.append("Overall pass rate is low. Consider reviewing the AI system's understanding of tennis queries.")
        
        if avg_accuracy < 0.6:
            suggestions.append("Average accuracy is below 60%. The AI may need better training on tennis terminology and data interpretation.")
        
        # Check category performance
        category_stats = analysis['category_analysis']
        for category, stats in category_stats.items():
            if stats['total'] > 0:
                category_pass_rate = stats['passed'] / stats['total']
                if category_pass_rate < 0.5:
                    suggestions.append(f"Category '{category}' has low performance ({category_pass_rate:.1%}). Consider improving handling of this query type.")
        
        # Check difficulty performance
        difficulty_stats = analysis['difficulty_analysis']
        for difficulty, stats in difficulty_stats.items():
            if stats['total'] > 0:
                difficulty_pass_rate = stats['passed'] / stats['total']
                if difficulty_pass_rate < 0.3:
                    suggestions.append(f"'{difficulty}' difficulty tests are struggling. Consider simplifying these queries or improving AI capabilities.")
        
        # Check execution time
        avg_execution_time = analysis['performance_metrics']['average_execution_time']
        if avg_execution_time > 10.0:
            suggestions.append("Average execution time is high. Consider optimizing the AI system for faster responses.")
        
        return suggestions
