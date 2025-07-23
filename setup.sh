#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Setup complete. Activate the environment with 'source .venv/bin/activate'"
