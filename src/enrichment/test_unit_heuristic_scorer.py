import unittest
from src.enrichment.heuristic_scorer import HeuristicScorer

class TestHeuristicScorerUnit(unittest.TestCase):
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

    def test_score_bullet_features(self):
        result = self.scorer.score_bullet(self.bullets[0], self.resume_meta)
        self.assertIn("education", result)
        self.assertIn("certifications", result)
        self.assertIn("experience", result)
        self.assertIn("project_impact", result)
        self.assertIsInstance(result["rationale"], str)

    def test_score_resume_aggregation(self):
        result = self.scorer.score_resume(self.bullets, self.resume_meta, context={"channel": "portal", "archetype": "mid-market"})
        self.assertIn("overall_score", result)
        self.assertIn("category", result)
        self.assertIn("rationales", result)
        self.assertEqual(len(result["rationales"]), len(self.bullets))
        self.assertIn("evidence_map", result)
        self.assertIsInstance(result["evidence_map"], dict)
        self.assertIn("gap_map", result)
        self.assertIsInstance(result["gap_map"], list)
        self.assertIn("psl", result)
        self.assertGreaterEqual(result["psl"], 0)

    def test_weight_tuning(self):
        custom_weights = {k: 5 for k in self.scorer.DEFAULT_WEIGHTS}
        scorer = HeuristicScorer(self.job_desc, weights=custom_weights)
        result = scorer.score_bullet(self.bullets[0], self.resume_meta)
        self.assertTrue(all(result[f] <= 5 for f in custom_weights))

    def test_feedback_loop(self):
        self.scorer.log_feedback("resume123", "Needs more cloud experience.")
        self.assertEqual(self.scorer.feedback_log[-1]["resume_id"], "resume123")

if __name__ == '__main__':
    unittest.main()
