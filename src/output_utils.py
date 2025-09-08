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

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))

def save_json(records, filename="results.json"):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(records, f, indent=2)
    return path

def save_csv(records, filename="results.csv"):
    path = os.path.join(OUTPUT_DIR, filename)
    df = pd.DataFrame(records)
    df.to_csv(path, index=False)
    return path

def save_excel(records, filename="results.xlsx"):
    path = os.path.join(OUTPUT_DIR, filename)
    export_to_excel(records, path, columns=EXPORT_COLUMNS)
    return path

# Example usage:
# records = [{...}, {...}]
# save_json(records)
# save_csv(records)
# save_excel(records)
