"""
Configuration constants for AskTennis application.
Centralizes all hardcoded values and configuration settings.
"""

# Database Configuration
DEFAULT_DB_PATH = "sqlite:///tennis_data.db"

# LLM Configuration
DEFAULT_MODEL = "gemini-2.5-flash-lite"
DEFAULT_TEMPERATURE = 0

# Application Configuration
APP_TITLE = "🎾 AskTennis: The Advanced AI Engine"
APP_SUBTITLE = "#### Powered by Gemini & LangGraph (Stateful Agent)"

# Example Questions
EXAMPLE_QUESTIONS = """
- *How many matches did Roger Federer win in 2006?*
- *Who won the most matches on clay in 2010?*
- *What was the score of the Wimbledon final in 2008?*
"""

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
