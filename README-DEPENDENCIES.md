# AskTennis Dependency Management Guide

## Overview
This project has multiple branches with different dependency requirements. This guide ensures you can switch between branches without having to reinstall dependencies separately.

## Branches and Their Dependencies

### Phase 2 - Testing
- **Purpose**: Basic data loading and processing
- **Dependencies**: `pandas`
- **Files**: `load_data.py`, `app.py` (data processing only)

### Phase 3 - Beautiful Visualization Testing  
- **Purpose**: Streamlit app with visualizations
- **Dependencies**: `streamlit`, `pandas`, `spacy`, `plotly`
- **Files**: `app.py` (with Plotly charts)

### Phase 4 - AI LLM Testing
- **Purpose**: AI-powered tennis Q&A with LangChain/LangGraph
- **Dependencies**: `streamlit`, `sqlalchemy`, `langchain`, `langchain-community`, `langchain-google-genai`, `langgraph`, `lxml`
- **Files**: `app.py` (with AI agent), `requirements.txt`

### Master
- **Purpose**: Production-ready visualization app
- **Dependencies**: `streamlit`, `pandas`, `spacy`, `plotly`
- **Files**: `app.py` (with visualizations)

## Quick Setup (Recommended)

### Option 1: Automated Setup
```bash
# Run the unified setup script
./setup-dependencies.sh
```

This will:
- Create a virtual environment
- Install all dependencies for all branches
- Download required spaCy models
- Create branch-specific requirement files for reference

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements-unified.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Branch-Specific Requirements

If you prefer to install only what's needed for a specific branch:

```bash
# For Phase 2
pip install -r requirements-phase2.txt

# For Phase 3
pip install -r requirements-phase3.txt

# For Phase 4  
pip install -r requirements-phase4.txt

# For Master
pip install -r requirements-master.txt
```

## Usage

1. **Activate the environment** (if not already active):
   ```bash
   source venv/bin/activate
   ```

2. **Switch to any branch**:
   ```bash
   git checkout <branch-name>
   ```

3. **Run the application**:
   ```bash
   # For branches with Streamlit apps
   streamlit run app.py
   
   # For Phase 2 (data loading only)
   python load_data.py
   ```

## Environment Management

### Activating the Environment
```bash
source venv/bin/activate
```

### Deactivating the Environment
```bash
deactivate
```

### Updating Dependencies
```bash
# Update all dependencies
pip install -r requirements-unified.txt --upgrade

# Update specific packages
pip install --upgrade streamlit pandas
```

## Troubleshooting

### Common Issues

1. **spaCy model not found**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **LangChain import errors**:
   ```bash
   pip install --upgrade langchain langchain-community langchain-google-genai langgraph
   ```

3. **Plotly not working**:
   ```bash
   pip install --upgrade plotly
   ```

4. **Streamlit issues**:
   ```bash
   pip install --upgrade streamlit
   ```

### Branch-Specific Notes

- **Phase 4**: Requires `GOOGLE_API_KEY` in `.streamlit/secrets.toml`
- **Phase 3 & Master**: Requires spaCy English model
- **All branches**: Require `tennis_data.db` database file

## File Structure

```
AskTennis_Gemini/
├── requirements-unified.txt      # All dependencies
├── requirements-phase2.txt      # Phase 2 only
├── requirements-phase3.txt      # Phase 3 only  
├── requirements-phase4.txt      # Phase 4 only
├── requirements-master.txt       # Master only
├── setup-dependencies.sh         # Automated setup
├── README-DEPENDENCIES.md        # This file
└── venv/                         # Virtual environment (created by setup)
```

## Benefits of This Approach

1. **No reinstallation**: Switch branches without dependency issues
2. **Consistent environment**: Same Python packages across all branches
3. **Easy maintenance**: Single source of truth for all dependencies
4. **Development efficiency**: No time wasted on dependency management
5. **Team collaboration**: Everyone uses the same dependency setup
