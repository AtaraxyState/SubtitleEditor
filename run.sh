#!/bin/bash

echo "Starting Subtitle Editor..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"  
        echo "Please install Python 3.7 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.7"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required"
    exit 1
fi

# Run the application
$PYTHON_CMD main.py

# Check exit code
if [ $? -ne 0 ]; then
    echo
    echo "Application ended with error"
    read -p "Press Enter to continue..."
fi 