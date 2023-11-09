#!/bin/bash
# Get the current directory
CURRENT_DIR="$(pwd)"

# Append the export command to the .bashrc file
echo "export PYTHONPATH=\"$CURRENT_DIR:\$PYTHONPATH\"" >> ~/.bashrc

# Source the .bashrc to update the environment variables in the current session
source ~/.bashrc
