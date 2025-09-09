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
        # Test with all KO fields passing
        result = self.scorer.score_resume(self.bullets, self.resume_meta, context={"channel": "portal", "archetype": "mid-market"})
        self.assertGreaterEqual(result["overall_score"], 0)
        self.assertIn(result["category"], ["Strong", "High", "Average", "Weak", "Unlikely", "Negligible"])
        self.assertFalse(result["ko_failed"])
        self.assertEqual(result["failed_kos"], [])
        self.assertIn("evidence_map", result)
        self.assertIsInstance(result["evidence_map"], dict)
        self.assertIn("gap_map", result)
        self.assertIsInstance(result["gap_map"], list)
        self.assertIn("psl", result)
        self.assertGreaterEqual(result["psl"], 0)
        for bullet_result in result["bullets"]:
            self.assertIn("bm25_tfidf", bullet_result)
            bm25 = bullet_result["bm25_tfidf"]
            if bm25:
                self.assertIn("tfidf_max", bm25)
                self.assertIn("bm25_max", bm25)
                self.assertGreaterEqual(bm25["tfidf_max"], 0)
                self.assertGreaterEqual(bm25["bm25_max"], 0)
        for rationale in result["rationales"]:
            self.assertTrue(rationale)
        # Simulate feedback loop
        self.scorer.log_feedback("resume123", "E2E: Candidate should highlight cloud certification.")
        self.assertEqual(self.scorer.feedback_log[-1]["resume_id"], "resume123")

    def test_e2e_resume_scoring_ko_fail(self):
        # Test with KO failure (e.g., missing cert)
        bad_meta = {
            "education": "BS Computer Science",
            "certifications": "None",
            "years_experience": 3,
            "location": "Remote"
        }
        result = self.scorer.score_resume(self.bullets, bad_meta, context={"channel": "portal", "archetype": "mid-market"})
        self.assertTrue(result["ko_failed"])
        self.assertIn("certifications", result["failed_kos"])
        self.assertIn("years_experience", result["failed_kos"])
        self.assertIn("KO failed: certifications", result["gap_map"])
        self.assertIn("KO failed: years_experience", result["gap_map"])
        self.assertEqual(result["psl"], 0)

if __name__ == '__main__':
    unittest.main()
