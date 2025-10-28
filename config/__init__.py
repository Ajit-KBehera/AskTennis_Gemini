"""
Configuration package for AskTennis application.
Contains all configuration constants and settings.
"""

from .constants import (
    DEFAULT_DB_PATH,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    APP_TITLE,
    APP_SUBTITLE,
    EXAMPLE_QUESTIONS
)

__all__ = [
    'DEFAULT_DB_PATH',
    'DEFAULT_MODEL', 
    'DEFAULT_TEMPERATURE',
    'APP_TITLE',
    'APP_SUBTITLE',
    'EXAMPLE_QUESTIONS'
]
