"""Excel export utilities."""

import pandas as pd

# Export columns configuration
EXPORT_COLUMNS = [
    'Job Title', 'Company', 'Location', 'Salary', 'Job Description',
    'Resume Name', 'Resume Match Score', 'Heuristic Score', 'ML Score',
    'Application Status', 'Resume Feedback Score', 'Resume Feedback Summary',
    'Actionable Recommendations'
]

def export_to_excel(data, output_path):
    """Export data to Excel file.
    
    Args:
        data: Data to export (dict, list, or DataFrame)
        output_path: Path for output Excel file
    """
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data
        
    # Ensure columns match expected format
    if not df.empty and set(EXPORT_COLUMNS).issubset(df.columns):
        df = df[EXPORT_COLUMNS]
        
    df.to_excel(output_path, index=False, engine='openpyxl')

class ExcelExporter:
    """Class for exporting data to Excel format."""
    
    def __init__(self):
        pass
    
    def export_to_excel(self, data, output_path):
        """Export data to Excel file.
        
        Args:
            data: Data to export (dict or DataFrame)
            output_path: Path for output Excel file
        """
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data
            
        df.to_excel(output_path, index=False, engine='openpyxl')
