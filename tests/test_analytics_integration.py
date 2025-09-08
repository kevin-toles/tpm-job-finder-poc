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
        loaded = load_analytics_results(self.json_path)
        self.assertEqual(loaded["Callback_rate"], self.results["Callback_rate"])

    def test_embeddings_consumer(self):
        update_embeddings_from_analytics(self.json_path)

    def test_ml_scoring_consumer(self):
        calibrate_scoring_from_analytics(self.json_path)

    def test_training_pipeline_consumer(self):
        train_models_from_analytics(self.json_path)

if __name__ == "__main__":
    unittest.main()
