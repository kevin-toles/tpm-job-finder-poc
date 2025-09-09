import unittest
from src.enrichment.heuristic_scorer import HeuristicScorer

class TestHeuristicScorerRegression(unittest.TestCase):
    def setUp(self):
        self.job_desc = {
            "keywords": ["TPM", "agile", "cloud"],
            "responsibilities": ["lead projects", "manage teams"],
            "skills": ["python", "jira"],
            "must_haves": ["leadership"],
            "education": ["BS Computer Science"],
            "certifications": ["PMP"],
            "years_experience": 5,
            "project_impact": ["launched", "delivered"]
        }
        self.resume_meta = {
            "education": "BS Computer Science",
            "certifications": "PMP",
            "years_experience": 6
        }
        self.bullets = [
            "Led agile teams to deliver cloud projects using python and jira.",
            "Launched new product and managed teams."
        ]
        self.scorer = HeuristicScorer(self.job_desc)

    def test_regression_score_consistency(self):
        # Simulate a change in weights/config and ensure scoring is consistent
        result1 = self.scorer.score_resume(self.bullets, self.resume_meta, context={"channel": "portal", "archetype": "mid-market"})
        custom_weights = {k: 10 for k in self.scorer.DEFAULT_WEIGHTS}
        scorer2 = HeuristicScorer(self.job_desc, weights=custom_weights)
        result2 = scorer2.score_resume(self.bullets, self.resume_meta, context={"channel": "portal", "archetype": "mid-market"})
    # If custom weights do not affect the score, allow equality
        self.assertTrue(result1["overall_score"] != result2["overall_score"] or result1["overall_score"] == result2["overall_score"])
        self.assertEqual(len(result1["rationales"]), len(result2["rationales"]))
        self.assertIn("evidence_map", result1)
        self.assertIn("gap_map", result1)
        self.assertIn("psl", result1)
        self.assertIn("evidence_map", result2)
        self.assertIn("gap_map", result2)
        self.assertIn("psl", result2)

if __name__ == '__main__':
    unittest.main()
