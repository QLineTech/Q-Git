#!/bin/bash

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install packages if not installed
pip install -r requirements.txt

# Run main.py
python3 main.py