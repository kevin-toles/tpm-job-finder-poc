import unittest
from src.enrichment.heuristic_scorer import HeuristicScorer

class TestHeuristicScorerE2E(unittest.TestCase):
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

    def test_e2e_resume_scoring(self):
        result = self.scorer.score_resume(self.bullets, self.resume_meta)
        self.assertGreaterEqual(result["overall_score"], 0)
        self.assertIn(result["category"], ["Strong", "High", "Average", "Weak", "Unlikely", "Negligible"])
        for rationale in result["rationales"]:
            self.assertTrue(rationale)
        # Simulate feedback loop
        self.scorer.log_feedback("resume123", "E2E: Candidate should highlight cloud certification.")
        self.assertEqual(self.scorer.feedback_log[-1]["resume_id"], "resume123")

if __name__ == '__main__':
    unittest.main()
