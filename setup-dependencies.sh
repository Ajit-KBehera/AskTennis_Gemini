#!/bin/bash

# AskTennis Unified Dependency Setup Script
# This script sets up dependencies for all branches so users don't need to install separately

echo "🎾 Setting up AskTennis dependencies for all branches..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install unified requirements
echo "Installing unified dependencies..."
pip install -r requirements-unified.txt

# Download spaCy model (needed for Phase 3 and Master)
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Create branch-specific requirements files for reference
echo "Creating branch-specific requirement files for reference..."

# Phase 2 requirements (minimal)
cat > requirements-phase2.txt << EOF
# Phase 2 - Testing (Minimal dependencies)
pandas>=1.5.0
EOF

# Phase 3 requirements
cat > requirements-phase3.txt << EOF
# Phase 3 - Beautiful Visualization Testing
streamlit>=1.28.0
pandas>=1.5.0
spacy>=3.4.0
plotly>=5.15.0
EOF

# Phase 4 requirements
cat > requirements-phase4.txt << EOF
# Phase 4 - AI LLM Testing
streamlit>=1.28.0
sqlalchemy>=1.4.0
langchain>=0.1.0
langchain-community>=0.0.20
langchain-google-genai>=1.0.0
langgraph>=0.0.30
lxml>=4.9.0
EOF

# Master requirements
cat > requirements-master.txt << EOF
# Master branch
streamlit>=1.28.0
pandas>=1.5.0
spacy>=3.4.0
plotly>=5.15.0
EOF

echo "✅ Dependencies setup complete!"
echo ""
echo "📋 Summary:"
echo "- Virtual environment created/activated"
echo "- All dependencies installed"
echo "- spaCy model downloaded"
echo "- Branch-specific requirement files created for reference"
echo ""
echo "🚀 You can now switch between any branch without reinstalling dependencies!"
echo ""
echo "To activate the environment in the future, run:"
echo "source venv/bin/activate"
