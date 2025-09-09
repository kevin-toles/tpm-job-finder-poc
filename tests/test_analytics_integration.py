from src.storage.secure_storage import SecureStorage
import unittest
import tempfile
import os
import json
from import_analysis import ImportAnalysis
from analytics_shared import load_analytics_results
from embeddings_service import update_embeddings_from_analytics
from ml_scoring_api import calibrate_scoring_from_analytics
from ml_training_pipeline import train_models_from_analytics

class TestAnalyticsIntegration(unittest.TestCase):
    def setUp(self):
        self.df_path = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False).name
        import pandas as pd
        pd.DataFrame({
            "Job ID": [1], "Match Score": [100], "Callback": ["Yes"], "Resume Feedback": ["Good fit"]
        }).to_excel(self.df_path, index=False)
        self.analysis = ImportAnalysis()
        self.results = self.analysis.analyze(self.df_path)
        self.json_path = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name
        self.analysis.save_results(self.results, self.json_path)

    def tearDown(self):
        os.unlink(self.df_path)
        os.unlink(self.json_path)

    def test_load_analytics_results(self):
        # Use a consistent base name for saving and retrieving metadata
        base_name = "test_analytics"
        self.analysis.save_results(self.results, base_name)
        storage = SecureStorage()
        loaded = storage.retrieve_metadata(base_name)
        self.assertEqual(loaded["Callback_rate"], self.results["Callback_rate"])
        # Clean up
        meta_path = os.path.join(storage.metadata_dir, base_name + ".json")
        if os.path.exists(meta_path):
            os.unlink(meta_path)

    def test_embeddings_consumer(self):
        base_name = "test_analytics"
        self.analysis.save_results(self.results, base_name)
        storage = SecureStorage()
        analytics_path = os.path.join(storage.metadata_dir, base_name + ".json")
        update_embeddings_from_analytics(analytics_path)

    def test_ml_scoring_consumer(self):
        base_name = "test_analytics"
        self.analysis.save_results(self.results, base_name)
        storage = SecureStorage()
        analytics_path = os.path.join(storage.metadata_dir, base_name + ".json")
        calibrate_scoring_from_analytics(analytics_path)

    def test_training_pipeline_consumer(self):
        base_name = "test_analytics"
        self.analysis.save_results(self.results, base_name)
        storage = SecureStorage()
        analytics_path = os.path.join(storage.metadata_dir, base_name + ".json")
        train_models_from_analytics(analytics_path)

if __name__ == "__main__":
    unittest.main()
