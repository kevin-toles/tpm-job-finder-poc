from src.storage.secure_storage import SecureStorage
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
        # Use a consistent base name for saving and retrieving metadata
        base_name = "test_results"
        self.analysis.save_results(results, base_name)
        storage = SecureStorage()
        loaded = storage.retrieve_metadata(base_name)
        self.assertEqual(loaded["Callback_rate"], results["Callback_rate"])
        # Clean up
        meta_path = os.path.join(storage.metadata_dir, base_name + ".json")
        if os.path.exists(meta_path):
            os.unlink(meta_path)
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
