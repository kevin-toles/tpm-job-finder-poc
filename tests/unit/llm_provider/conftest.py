"""
Test configuration for LLM provider tests.
"""

import pytest
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure pytest
def pytest_configure(config):
    """Configure pytest settings."""
    pass