"""
Shared analytics result schema for downstream consumers.
Fields:
- Callback_rate, Interview_rate, Offer_rate
- score_success_correlation
- feedback_stats
- records (list of job dicts)
"""
import json
from typing import Dict, Any

def load_analytics_results(path: str) -> Dict[str, Any]:
    """
    Loads analytics results from a shared JSON file.
    Args:
        path: Path to the JSON file.
    Returns:
        Dictionary of analytics results.
    """
    with open(path, "r") as f:
        return json.load(f)
