"""
Test data module for automated testing framework.
Contains tennis Q&A datasets and test categorization.
"""

from .tennis_qa_dataset import TENNIS_QA_DATASET, get_test_categories
from .test_categories import TEST_CATEGORIES, TestCategory

__all__ = [
    'TENNIS_QA_DATASET',
    'get_test_categories',
    'TEST_CATEGORIES', 
    'TestCategory'
]
