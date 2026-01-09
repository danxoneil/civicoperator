#!/bin/bash
# Setup script for Dress Monitor

echo "🔧 Setting up Emilio Pucci Dress Monitor..."

# Check Python version
python3 --version || { echo "❌ Python 3 is required but not installed."; exit 1; }

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Make monitor.py executable
chmod +x monitor.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your notification settings"
echo "2. Test the monitor: python3 monitor.py"
echo "3. Set up daily cron job: ./setup_cron.sh"
