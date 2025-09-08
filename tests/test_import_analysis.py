import unittest
import pandas as pd
import tempfile
import os
from import_analysis import ImportAnalysis

class TestImportAnalysis(unittest.TestCase):
    def test_save_results(self):
        results = self.analysis.analyze(self.temp_file.name)
        temp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        temp_json.close()
        self.analysis.save_results(results, temp_json.name)
        import json
        with open(temp_json.name, "r") as f:
            loaded = json.load(f)
        self.assertEqual(loaded["Callback_rate"], results["Callback_rate"])
        os.unlink(temp_json.name)
    def test_missing_columns(self):
        df = pd.DataFrame({"Job ID": [1], "Match Score": [90]})
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        analysis = ImportAnalysis()
        results = analysis.analyze(temp_file.name)
        self.assertIn("records", results)
        os.unlink(temp_file.name)

    def test_empty_file(self):
        df = pd.DataFrame()
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        analysis = ImportAnalysis()
        results = analysis.analyze(temp_file.name)
        self.assertEqual(len(results["records"]), 0)
        os.unlink(temp_file.name)

    def test_custom_columns(self):
        df = pd.DataFrame({"ID": [1], "Score": [100], "Status": ["Yes"]})
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        analysis = ImportAnalysis(job_id_col="ID", status_cols=["Status"], score_col="Score")
        results = analysis.analyze(temp_file.name)
        self.assertIn("Status_rate", results)
        os.unlink(temp_file.name)

    def test_invalid_data(self):
        df = pd.DataFrame({"Job ID": [1], "Match Score": ["high"], "Callback": [None]})
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        analysis = ImportAnalysis()
        try:
            results = analysis.analyze(temp_file.name)
            self.assertIn("records", results)
        finally:
            os.unlink(temp_file.name)
    def setUp(self):
        # Create a sample DataFrame
        self.df = pd.DataFrame({
            "Job ID": [1, 2, 3],
            "Match Score": [90, 75, 60],
            "Callback": ["Yes", None, "Yes"],
            "Interview": [None, "Yes", None],
            "Offer": [None, None, "Yes"],
            "Resume Feedback": ["Improve skills", "Add certifications", "Good fit"]
        })
        # Save to a temporary Excel file
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        self.df.to_excel(self.temp_file.name, index=False)
        self.temp_file.close()
        self.analysis = ImportAnalysis()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_analyze(self):
        results = self.analysis.analyze(self.temp_file.name)
        self.assertIn("Callback_rate", results)
        self.assertIn("score_success_correlation", results)
        self.assertIn("feedback_stats", results)
        self.assertEqual(len(results["records"]), 3)

if __name__ == "__main__":
    unittest.main()
