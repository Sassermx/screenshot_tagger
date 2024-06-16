#!/bin/bash

# Function to install Python on Unix-based systems
install_python() {
    echo "Installing Python 3.9 or higher..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install -y python3 python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install python
    fi
}

# Check if Python 3.9 or higher is installed
if ! command -v python3 &> /dev/null || ! python3 -c 'import sys; exit(sys.version_info >= (3, 9))'; then
    install_python
fi

# Ensure pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip not found. Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Install required packages
echo "Installing required packages..."
python3 -m pip install -r ../requirements.txt

# Run the main script
echo "Running the main script..."
python3 ../main.py
