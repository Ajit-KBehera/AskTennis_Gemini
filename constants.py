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


# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Testing Configuration
MINIMUM_TEST_INTERVAL_SECONDS = 75
DEFAULT_TEST_INTERVAL_SECONDS = 75
