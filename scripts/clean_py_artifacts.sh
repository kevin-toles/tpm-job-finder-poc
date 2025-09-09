#!/bin/bash
# Clean Python build artifacts and caches
find . -type d -name '__pycache__' -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
echo "Python build artifacts cleaned."
