#!/bin/bash

echo "🚀 Setting up Smart Geological RAG System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p data temp

# Copy environment template
cp .env.example .env

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your API keys: nano .env"
echo "2. Run locally: ./run.sh"
echo "3. Or use Docker: docker-compose up --build"
echo ""
echo "🔑 Get API keys from:"
echo "   • Groq: https://console.groq.com"
echo "   • HuggingFace: https://huggingface.co/settings/tokens"
