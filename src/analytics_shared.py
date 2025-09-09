"""
Shared analytics result schema for downstream consumers.
Fields:
- Callback_rate, Interview_rate, Offer_rate
- score_success_correlation
- feedback_stats
- records (list of job dicts)
"""
from typing import Dict, Any

def load_analytics_results(path: str) -> Dict[str, Any]:
    """
    Loads analytics results from a shared JSON file using SecureStorage.
    Args:
        path: Path to the JSON file.
    Returns:
        Dictionary of analytics results.
    """
    from src.storage.secure_storage import SecureStorage
    storage = SecureStorage()
    # Use the base filename without .json for retrieve_metadata
    import os
    base_name = os.path.basename(path).replace('.json', '')
    return storage.retrieve_metadata(base_name)
