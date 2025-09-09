import unittest
import tempfile
import os
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "export"))
from excel_exporter import export_to_excel, EXPORT_COLUMNS
import pandas as pd

class TestExcelExporter(unittest.TestCase):
    def setUp(self):
        self.records = [
            {
                "Job Title": "TPM",
                "Company": "Acme Corp",
                "Location": "Remote",
                "Salary": "$150k",
                "Job Description": "Lead projects",
                "Resume Name": "resume1.pdf",
                "Resume Match Score": 92,
                "Heuristic Score": 88,
                "ML Score": 85,
                "Application Status": "Applied",
                "Resume Feedback Score": 4.5,
                "Resume Feedback Summary": "Strong skills, missing certifications.",
                "Actionable Recommendations": "Add AWS certification."
            },
            {
                "Job Title": "TPM",
                "Company": "Beta Inc",
                "Location": "NYC",
                "Salary": "$140k",
                "Job Description": "Manage teams",
                "Resume Name": "resume2.pdf",
                "Resume Match Score": 80,
                "Heuristic Score": 75,
                "ML Score": 70,
                "Application Status": "Interview",
                "Resume Feedback Score": 3.8,
                "Resume Feedback Summary": "Good fit, improve impact statements.",
                "Actionable Recommendations": "Add quantifiable results."
            }
        ]
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_export_to_excel(self):
        export_to_excel(self.records, self.temp_file.name)
        df = pd.read_excel(self.temp_file.name)
        self.assertEqual(list(df.columns), EXPORT_COLUMNS)
        self.assertEqual(len(df), 2)
        self.assertIn("Resume Feedback Score", df.columns)
        self.assertIn("Resume Feedback Summary", df.columns)
        self.assertIn("Actionable Recommendations", df.columns)
        self.assertEqual(df["Resume Feedback Score"][0], 4.5)
        self.assertEqual(df["Actionable Recommendations"][1], "Add quantifiable results.")

if __name__ == "__main__":
    unittest.main()
