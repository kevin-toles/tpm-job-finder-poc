import unittest
from src.bm25_tfidf.bm25_tfidf_matcher import BM25TFIDFMatcher

class TestBM25TFIDFMatcher(unittest.TestCase):
    def setUp(self):
        self.corpus = [
            "Led agile teams to deliver cloud projects using python and jira.",
            "Launched new product and managed teams.",
            "Managed cloud migration and agile transformation."
        ]
        self.matcher = BM25TFIDFMatcher(self.corpus)

    def test_tfidf_and_bm25_scores(self):
        query = "agile cloud project management"
        scores = self.matcher.score(query)
        self.assertIn("tfidf_max", scores)
        self.assertIn("tfidf_mean", scores)
        self.assertIn("bm25_max", scores)
        self.assertIn("bm25_mean", scores)
        self.assertGreaterEqual(scores["tfidf_max"], 0)
        self.assertGreaterEqual(scores["bm25_max"], 0)
        self.assertGreaterEqual(scores["tfidf_mean"], 0)
        self.assertGreaterEqual(scores["bm25_mean"], 0)

if __name__ == '__main__':
    unittest.main()
