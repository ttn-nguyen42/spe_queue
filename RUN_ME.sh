#!/usr/bin/env bash

# Create environment
python3 -m venv './venv'
source './venv/bin/activate'
python3 -m pip install -r './requirements.txt'

# Run code
make all
