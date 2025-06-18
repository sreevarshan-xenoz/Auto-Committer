#!/bin/bash

# Enhanced Auto-Committer Quick Start Script

echo "Setting up Enhanced Auto-Committer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys and credentials."
fi

# Update repository path in config
if [ -f auto_committer_config.yaml ]; then
    echo "Updating repository path in config..."
    # Use sed to update the repository path
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|path: \".*\"|path: \"$(pwd)\"|g" auto_committer_config.yaml
    else
        # Linux
        sed -i "s|path: \".*\"|path: \"$(pwd)\"|g" auto_committer_config.yaml
    fi
fi

echo "Setup complete!"
echo "To start the auto-committer, run:"
echo "  source venv/bin/activate"
echo "  python auto_committer.py"
echo ""
echo "To run once and exit:"
echo "  python auto_committer.py --once"
echo ""
echo "To use a custom config:"
echo "  python auto_committer.py --config /path/to/custom_config.yaml" 