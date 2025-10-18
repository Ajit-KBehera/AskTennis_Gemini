#!/bin/bash

# Activate the conda environment and run the Streamlit app
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate asktennis
streamlit run app.py
