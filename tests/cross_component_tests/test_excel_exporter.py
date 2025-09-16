import unittest
import tempfile
import os
from tpm_job_finder_poc.excel_exporter import export_to_excel, SPEC_COLUMNS
import pandas as pd

class TestExcelExporter(unittest.TestCase):
    def setUp(self):
        self.records = [
            {
                "Job Title": "TPM",
                "Company": "Acme Corp",
                "Location": "Remote",
                "Salary": "$150k",
                "Selected Resume": "resume1.pdf",
                "Match Score": "92.0%",
                "Selection Rationale": "Strong skills match",
                "Enhancement 1": "Add AWS certification",
                "Enhancement 2": "Quantify project impact",
                "Enhancement 3": "Include leadership examples",
                "Job Source": "Indeed",
                "Date Posted": "2025-01-15"
            },
            {
                "Job Title": "TPM",
                "Company": "Beta Inc",
                "Location": "NYC",
                "Salary": "$140k",
                "Selected Resume": "resume2.pdf",
                "Match Score": "80.0%",
                "Selection Rationale": "Good technology fit",
                "Enhancement 1": "Add quantifiable results",
                "Enhancement 2": "Improve impact statements",
                "Enhancement 3": "Include team management examples",
                "Job Source": "LinkedIn",
                "Date Posted": "2025-01-14"
            }
        ]
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_export_to_excel(self):
        export_to_excel(self.records, self.temp_file.name)
        df = pd.read_excel(self.temp_file.name, engine='openpyxl')
        self.assertEqual(list(df.columns), SPEC_COLUMNS)
        self.assertEqual(len(df), 2)
        
        # Test new multi-resume intelligence columns
        self.assertIn("Selected Resume", df.columns)
        self.assertIn("Match Score", df.columns)
        self.assertIn("Selection Rationale", df.columns)
        self.assertIn("Enhancement 1", df.columns)
        self.assertIn("Enhancement 2", df.columns)
        self.assertIn("Enhancement 3", df.columns)
        
        # Verify data content
        self.assertEqual(df["Selected Resume"][0], "resume1.pdf")
        self.assertEqual(df["Match Score"][0], "92.0%")
        self.assertEqual(df["Enhancement 1"][1], "Add quantifiable results")

if __name__ == "__main__":
    unittest.main()
