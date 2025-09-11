#!/bin/bash
# Simple deploy script for POC
# Usage: ./deploy.sh

set -e

# Example: build docs and run tests before deploy
sphinx-build -b html docs docs/_build/html
PYTHONPATH=$(pwd) pytest --disable-warnings -v

# Add your deployment logic here (e.g., copy files, restart services)
echo "Deployment steps go here."
