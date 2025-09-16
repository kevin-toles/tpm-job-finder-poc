"""Quick debug script for Excel export issue."""

import pandas as pd
from pathlib import Path
import tempfile

# Simple test data
jobs_data = [
    {
        'title': 'Software Engineer',
        'company': 'TechCorp',
        'location': 'Remote',
        'salary': '$120K-150K',
        'source': 'Indeed',
        'date_posted': '2025-09-13',
        'id': 'job_456'
    }
]

# Build the spec row manually like our exporter does
spec_row = {
    'Job Title': jobs_data[0].get('title', jobs_data[0].get('Job Title', '')),
    'Company': jobs_data[0].get('company', jobs_data[0].get('Company', '')),
    'Location': jobs_data[0].get('location', jobs_data[0].get('Location', '')),
    'Salary': jobs_data[0].get('salary', jobs_data[0].get('Salary', '')),
    'Selected Resume': '',  # This should be empty string
    'Match Score': jobs_data[0].get('match_score', jobs_data[0].get('Match Score', '0%')),
    'Selection Rationale': '',
    'Enhancement 1': '',
    'Enhancement 2': '',
    'Enhancement 3': '',
    'Job Source': jobs_data[0].get('source', jobs_data[0].get('Job Source', '')),
    'Date Posted': jobs_data[0].get('date_posted', jobs_data[0].get('Date Posted', '')),
}

# No intelligence data, so fallback
spec_row.update({
    'Selected Resume': 'N/A',
    'Selection Rationale': 'Multi-resume processing not available',
    'Enhancement 1': '',
    'Enhancement 2': '',
    'Enhancement 3': '',
})

print("Spec row after fallback:")
for k, v in spec_row.items():
    print(f"  {k}: '{v}' ({type(v)})")

# Create DataFrame
enhanced_jobs = [spec_row]
df = pd.DataFrame(enhanced_jobs)

print("\nDataFrame after creation:")
print(df.dtypes)
print("\nSelected Resume value:")
print(f"Value: {df.iloc[0]['Selected Resume']}")
print(f"Type: {type(df.iloc[0]['Selected Resume'])}")
print(f"Is NaN: {pd.isna(df.iloc[0]['Selected Resume'])}")

# Export to Excel and read back
with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
    temp_path = tmp.name

df.to_excel(temp_path, index=False)
df_read = pd.read_excel(temp_path, sheet_name=0)

print("\nAfter Excel round trip:")
print(f"Value: {df_read.iloc[0]['Selected Resume']}")
print(f"Type: {type(df_read.iloc[0]['Selected Resume'])}")
print(f"Is NaN: {pd.isna(df_read.iloc[0]['Selected Resume'])}")