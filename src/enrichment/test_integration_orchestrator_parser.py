import unittest
from src.enrichment.orchestrator import ResumeScoringOrchestrator
from src.enrichment.resume_feedback_generator import ResumeFeedbackGenerator

class DummyLLMProvider:
    def get_feedback(self, llm_input):
        return f"LLM feedback for {llm_input['job_desc'].get('role_level', 'unknown')} level."

class TestResumeFeedbackIntegration(unittest.TestCase):
    def setUp(self):
        self.job_desc = {
            "keywords": ["TPM", "agile", "cloud"],
            "responsibilities": ["lead projects", "manage teams"],
            "skills": ["python", "jira"],
            "must_haves": ["leadership"],
            "education": ["BS Computer Science"],
            "certifications": ["PMP"],
            "years_experience": 5,
            "project_impact": ["launched", "delivered"],
            "role_level": "executive"
        }
        self.resume_meta = {
            "education": "BS Computer Science",
            "certifications": "None",
            "years_experience": 3,
            "skills": "python, jira",
            "keywords": "TPM, agile, cloud",
            "length": 3,
            "role_level": "executive"
        }
        self.scoring_result = {
            "format_issues": "Font inconsistency",
            "gap_map": ["KO failed: certifications"],
            "bullets": [
                {"bullet": "Managed teams.", "achievements": 0, "impact": 0},
                {"bullet": "Delivered cloud project.", "achievements": 1, "impact": 1}
            ]
        }
        self.context = {"archetype": "enterprise", "channel": "referral"}
        self.generator = ResumeFeedbackGenerator(llm_provider=DummyLLMProvider())

    def test_feedback_integration(self):
        feedback = self.generator.generate_feedback(self.job_desc, self.resume_meta, self.scoring_result, self.context)
        self.assertIsInstance(feedback, list)
        self.assertGreater(len(feedback), 0)
        self.assertTrue(any(item["severity"] == "critical" for item in feedback))
        self.assertTrue(any(item["category"] == "analytics" for item in feedback))
        self.assertTrue(any(item["category"] == "llm" for item in feedback))

if __name__ == '__main__':
    unittest.main()
import unittest
from src.enrichment.orchestrator import ResumeScoringOrchestrator
from src.enrichment.jd_parser import JDParser
from src.enrichment.resume_parser import ResumeParser
import tempfile
import os

class TestOrchestratorParserIntegration(unittest.TestCase):
    def setUp(self):
        self.jd_text = """
        Keywords: TPM, agile, cloud
        Responsibilities: lead projects, manage teams
        Skills: python, jira
        Must-haves: leadership
        Education: BS Computer Science
        Certifications: PMP
        5+ years experience
        Project Impact: launched, delivered
        Title: Senior TPM
        Company: BigTech
        2020-2025
        """
        self.resume_txt = """
        John Doe
        Education: BS Computer Science
        Certifications: PMP
        Experience:
        - Led agile teams to deliver cloud projects using python and jira.
        - Launched new product and managed teams.
        6+ years experience
        """
        # Create temp resume file
        self.resume_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        self.resume_file.write(self.resume_txt.encode("utf-8"))
        self.resume_file.close()

    def tearDown(self):
        os.unlink(self.resume_file.name)

    def test_orchestrator_with_parsing(self):
        orchestrator = ResumeScoringOrchestrator(
            resume_path=self.resume_file.name,
            jd_text=self.jd_text
        )
        result = orchestrator.score_resume()
        self.assertIn("heuristic", result)
        self.assertIn("ml", result)
        self.assertIn("aggregate", result)
        self.assertIn("bm25_tfidf", result)
        bm25 = result["bm25_tfidf"]
        if bm25:
            self.assertIn("tfidf_max", bm25)
            self.assertIn("bm25_max", bm25)
            self.assertGreaterEqual(bm25["tfidf_max"], 0)
            self.assertGreaterEqual(bm25["bm25_max"], 0)
        # Check parsed resume and JD signals
        self.assertGreaterEqual(result["heuristic"]["overall_score"], 0)
        self.assertIn("category", result["heuristic"])
        self.assertIn("evidence_map", result["heuristic"])
        self.assertIn("gap_map", result["heuristic"])
        self.assertIn("psl", result["heuristic"])
        # Check expanded JD signals
        self.assertTrue(orchestrator.heuristic.job_desc.get("titles"))
        self.assertTrue(orchestrator.heuristic.job_desc.get("companies"))
        self.assertTrue(orchestrator.heuristic.job_desc.get("timeline"))

if __name__ == '__main__':
    unittest.main()
