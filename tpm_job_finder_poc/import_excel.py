"""Import Excel utilities for reading Excel files."""

import pandas as pd

def import_excel_records(file_path, columns=None):
    """Import records from Excel file.
    
    Args:
        file_path: Path to Excel file
        columns: List of columns to import (optional)
        
    Returns:
        list: List of record dictionaries
    """
    df = pd.read_excel(file_path, engine='openpyxl')
    
    if columns:
        # Filter to only requested columns if they exist
        available_columns = [col for col in columns if col in df.columns]
        if available_columns:
            df = df[available_columns]
    
    return df.to_dict('records')

class ImportExcel:
    """Class for importing data from Excel files."""
    
    def __init__(self):
        pass
    
    def import_excel(self, file_path, columns=None):
        """Import data from Excel file.
        
        Args:
            file_path: Path to Excel file
            columns: List of columns to import (optional)
            
        Returns:
            pd.DataFrame: Imported data
        """
        df = pd.read_excel(file_path, engine='openpyxl')
        
        if columns:
            # Filter to only requested columns if they exist
            available_columns = [col for col in columns if col in df.columns]
            if available_columns:
                df = df[available_columns]
        
        return df
