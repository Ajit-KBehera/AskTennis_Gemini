"""
Test executor for automated testing framework.
Handles individual test execution and response processing.
"""

import time
import ast
from datetime import datetime
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage

from .result_analyzer import ResultAnalyzer
from .test_data.test_categories import get_validation_function, ValidationMethod


class TestExecutor:
    """
    Executes individual test cases and processes AI responses.
    Handles test execution, response extraction, and accuracy calculation.
    """
    
    def __init__(self, agent_graph):
        """
        Initialize the test executor.
        
        Args:
            agent_graph: The LangGraph agent to use for testing
        """
        self.agent_graph = agent_graph
        self.result_analyzer = ResultAnalyzer()
    
    def execute_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test case.
        
        Args:
            test_case: Dictionary containing test case data
            
        Returns:
            Dictionary containing test execution results
        """
        start_time = time.time()
        
        try:
            # Execute the test
            result = self._run_test_case(test_case)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            
            # Determine test status
            result['status'] = self._determine_test_status(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'test_id': test_case.get('id', 0),
                'question': test_case.get('question', ''),
                'generated_sql': '',
                'ai_answer': '',
                'expected_answer': test_case.get('expected_answer', ''),
                'accuracy_score': 0.0,
                'execution_time': execution_time,
                'status': 'error',
                'error_message': str(e),
                'confidence_score': 0.0,
                'category': test_case.get('category', '').value if hasattr(test_case.get('category', ''), 'value') else str(test_case.get('category', '')),
                'difficulty': test_case.get('difficulty', '')
            }
    
    def _run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case through the AI system.
        
        Args:
            test_case: Test case data
            
        Returns:
            Test execution results
        """
        question = test_case['question']
        expected_answer = test_case['expected_answer']
        category = test_case.get('category', '')
        category_str = category.value if hasattr(category, 'value') else str(category)
        difficulty = test_case.get('difficulty', '')
        
        # Send question to AI system
        config = {"configurable": {"thread_id": f"test_session_{test_case.get('id', 0)}"}}
        
        response = self.agent_graph.invoke(
            {"messages": [HumanMessage(content=question)]},
            config=config
        )
        
        # Extract components from response
        generated_sql = self._extract_sql_query(response)
        ai_answer = self._extract_final_answer(response)
        
        # Calculate accuracy
        accuracy_score = self._calculate_accuracy(
            ai_answer, 
            expected_answer, 
            category
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(response)
        
        return {
            'test_id': test_case.get('id', 0),
            'question': question,
            'generated_sql': generated_sql,
            'ai_answer': ai_answer,
            'expected_answer': expected_answer,
            'accuracy_score': accuracy_score,
            'confidence_score': confidence_score,
            'category': category_str,
            'difficulty': difficulty
        }
    
    
    def _extract_sql_query(self, response: Dict[str, Any]) -> str:
        """
        Extract SQL query from agent response.
        
        Args:
            response: Agent response dictionary
            
        Returns:
            SQL query string or empty string if not found
        """
        try:
            messages = response.get('messages', [])
            
            for message in messages:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        if tool_call.get('name') == 'sql_db_query':
                            args = tool_call.get('args', {})
                            return args.get('query', '')
                
                # Also check for SQL in message content
                if hasattr(message, 'content'):
                    content = str(message.content)
                    if 'SELECT' in content.upper() or 'INSERT' in content.upper():
                        # Try to extract SQL from content
                        lines = content.split('\n')
                        for line in lines:
                            if 'SELECT' in line.upper():
                                return line.strip()
            
            return ''
        except Exception:
            return ''
    
    def _extract_final_answer(self, response: Dict[str, Any]) -> str:
        """
        Extract the final answer from the AI response.
        
        Args:
            response: Agent response dictionary
            
        Returns:
            Final answer string
        """
        try:
            messages = response.get('messages', [])
            if not messages:
                return ''
            
            # Get the last AI message
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                content = last_message.content
                
                if isinstance(content, list) and content:
                    # For Gemini, content is a list of dicts
                    text_content = content[0].get('text', '')
                else:
                    text_content = str(content)
                
                # Try to extract the most relevant answer
                return self._parse_final_answer(text_content)
            
            return ''
        except Exception:
            return ''
    
    def _parse_final_answer(self, content: str) -> str:
        """
        Parse the final answer from AI response content.
        
        Args:
            content: AI response content
            
        Returns:
            Parsed final answer
        """
        if not content:
            return ''
        
        # Look for common answer patterns
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for direct answers
            if any(phrase in line.lower() for phrase in [
                'the answer is', 'the winner is', 'the result is',
                'the champion is', 'the player is'
            ]):
                return line
            
            # Look for simple statements
            if len(line.split()) <= 10 and not line.startswith('#'):
                return line
        
        # If no clear answer found, return the first non-empty line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('*'):
                return line
        
        return content[:200]  # Return first 200 characters as fallback
    
    def _calculate_accuracy(self, ai_answer: str, expected_answer: str, category: str) -> float:
        """
        Calculate accuracy score for the AI answer.
        
        Args:
            ai_answer: Answer provided by AI
            expected_answer: Expected correct answer
            category: Test category for validation method
            
        Returns:
            Accuracy score between 0.0 and 1.0
        """
        if not ai_answer or not expected_answer:
            return 0.0
        
        # Use the result analyzer for accuracy calculation
        return self.result_analyzer.calculate_accuracy(
            ai_answer, 
            expected_answer, 
            category
        )
    
    def _calculate_confidence_score(self, response: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on response characteristics.
        
        Args:
            response: Agent response dictionary
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            messages = response.get('messages', [])
            if not messages:
                return 0.0
            
            # Simple confidence calculation based on response length and structure
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                content = str(last_message.content)
                
                # Longer, more detailed responses get higher confidence
                length_score = min(len(content) / 100, 1.0)
                
                # Responses with specific details get higher confidence
                detail_score = 0.0
                if any(word in content.lower() for word in ['defeated', 'won', 'champion', 'title']):
                    detail_score += 0.3
                if any(word in content.lower() for word in ['6-', '7-', 'set', 'final']):
                    detail_score += 0.2
                if any(word in content.lower() for word in ['year', 'tournament', 'surface']):
                    detail_score += 0.2
                
                return min(length_score + detail_score, 1.0)
            
            return 0.0
        except Exception:
            return 0.0
    
    def _determine_test_status(self, result: Dict[str, Any]) -> str:
        """
        Determine the test status based on accuracy and other factors.
        
        Args:
            result: Test result dictionary
            
        Returns:
            Test status ('passed', 'failed', or 'error')
        """
        accuracy = result.get('accuracy_score', 0.0)
        
        if accuracy >= 0.8:
            return 'passed'
        elif accuracy >= 0.5:
            return 'failed'
        else:
            return 'failed'
    
    def batch_execute_tests(self, test_cases: list, progress_callback=None) -> list:
        """
        Execute multiple test cases in batch.
        
        Args:
            test_cases: List of test case dictionaries
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of test execution results
        """
        results = []
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            try:
                result = self.execute_single_test(test_case)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, total_tests, result)
                    
            except Exception as e:
                category = test_case.get('category', '')
                category_str = category.value if hasattr(category, 'value') else str(category)
                
            error_result = {
                'test_id': test_case.get('id', 0),
                'question': test_case.get('question', ''),
                'generated_sql': '',
                'ai_answer': '',
                'expected_answer': test_case.get('expected_answer', ''),
                'accuracy_score': 0.0,
                'execution_time': 0.0,
                'status': 'error',
                'error_message': str(e),
                'confidence_score': 0.0,
                'category': category_str,
                'difficulty': test_case.get('difficulty', '')
            }
            results.append(error_result)
            
            if progress_callback:
                progress_callback(i + 1, total_tests, error_result)
        
        return results
