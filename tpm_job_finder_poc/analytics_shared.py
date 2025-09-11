"""Analytics shared utilities for loading and processing analytics data."""

import json
import os

def load_analytics_results(analytics_path):
    """Load analytics results from JSON file.
    
    Args:
        analytics_path: Path to analytics JSON file
        
    Returns:
        dict: Analytics data loaded from file
    """
    if not os.path.exists(analytics_path):
        return {}
    
    try:
        with open(analytics_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}
