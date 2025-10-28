"""
Configuration settings for AskTennis data loading.
Centralizes all configuration constants and settings.
"""

import os

# --- Project Configuration ---
# Get the project root directory (parent of load_data)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Data Directories ---
DATA_DIRS = [
    os.path.join(PROJECT_ROOT, "data/tennis_atp"), 
    os.path.join(PROJECT_ROOT, "data/tennis_wta")
]

# --- Database Configuration ---
DB_FILE = os.path.join(PROJECT_ROOT, "tennis_data.db")

# --- Year Configuration ---
YEARS = list(range(1968, 2026))  # Complete historical coverage: 1968-2024

# --- Testing Configuration ---
# Option to load only recent years for testing (set to False for complete data)
LOAD_RECENT_ONLY = False  # Set to True to load only 2020-2024 for testing
RECENT_YEARS = list(range(2020, 2026)) if LOAD_RECENT_ONLY else YEARS

# --- Progress Tracking Configuration ---
PROGRESS_UPDATE_INTERVAL = 10  # Update progress every N files
PROGRESS_DISPLAY_INTERVAL = 5  # Display progress every N seconds

# --- Data Processing Configuration ---
BATCH_SIZE = 1000  # Process data in batches
CHUNK_SIZE = 10000  # Read large files in chunks

# --- Database Index Configuration ---
CREATE_INDEXES = True
INDEX_BATCH_SIZE = 100000  # Create indexes in batches

# --- Logging Configuration ---
VERBOSE_LOGGING = True
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "data_loading.log")
