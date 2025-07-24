#!/bin/bash

echo "🧠 Starting Smart Geological RAG System..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create directories if they don't exist
mkdir -p data temp

# Run Streamlit app
streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
