#!/bin/bash

# BlogSEO v3 - Streamlit Application Runner
# ==========================================

echo "🚀 Starting BlogSEO v3..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before proceeding."
fi

# Clear Streamlit cache (optional)
# echo "🧹 Clearing Streamlit cache..."
# streamlit cache clear

# Run the Streamlit app
echo ""
echo "✨ Launching BlogSEO v3 application..."
echo "📱 Opening in browser: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

streamlit run app.py --server.port=8501 --server.address=localhost
