import pandas as pd
from typing import List, Dict, Any

def import_excel_records(file_path: str, columns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Reads an Excel sheet and returns a list of job records (dicts).
    Args:
        file_path: Path to the Excel file.
        columns: Optional list of columns to select.
    Returns:
        List of records (dicts).
    """
    df = pd.read_excel(file_path)
    if columns:
        df = df[columns]
    return df.to_dict(orient="records")
