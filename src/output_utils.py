# --- Database Integration Stub ---
def save_to_database(records, db_config=None):
    """
    Stub for saving job/resume results to a database.
    Args:
        records: List of dicts to save.
        db_config: Optional database configuration.
    Returns:
        None (stub)
    """
    # TODO: Implement database save logic when hosting/deploying
    pass
"""
Output utilities for job/resume matching results
Generates JSON, CSV, and Excel files in the output/ folder
"""

import os
import json
import pandas as pd
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "export"))
from excel_exporter import export_to_excel, EXPORT_COLUMNS
from src.storage.secure_storage import SecureStorage

storage = SecureStorage()

def save_json(records, filename="results.json"):
    path = os.path.join(storage.files_dir, filename)
    with open(path, "w") as f:
        json.dump(records, f, indent=2)
    storage.log_action("save_json", {"filename": filename})
    return path

def save_csv(records, filename="results.csv"):
    path = os.path.join(storage.files_dir, filename)
    df = pd.DataFrame(records)
    df.to_csv(path, index=False)
    storage.log_action("save_csv", {"filename": filename})
    return path

def save_excel(records, filename="results.xlsx"):
    path = os.path.join(storage.files_dir, filename)
    export_to_excel(records, path, columns=EXPORT_COLUMNS)
    storage.log_action("save_excel", {"filename": filename})
    return path

# Example usage:
# records = [{...}, {...}]
# save_json(records)
# save_csv(records)
# save_excel(records)
