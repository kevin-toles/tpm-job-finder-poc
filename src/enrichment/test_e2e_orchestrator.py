import unittest
from src.enrichment.orchestrator import ResumeScoringOrchestrator

class DummyLLMProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key
    def get_signals(self, prompt):
        return {"provider": "DummyLLM", "response": f"Rationale for: {prompt}"}
    def get_feedback(self, llm_input):
        return f"LLM feedback for {llm_input['job_desc'].get('role_level', 'unknown')} level."

class TestResumeScoringOrchestratorE2E(unittest.TestCase):
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
        self.llm_config = {"provider": "dummy"}
        # Patch orchestrator to use DummyLLMProvider
        ResumeScoringOrchestrator._init_llm = lambda self, cfg: DummyLLMProvider()
        self.orchestrator = ResumeScoringOrchestrator(self.job_desc, llm_config=self.llm_config)

    def test_e2e_orchestrator_with_feedback(self):
        result = self.orchestrator.score_resume(self.bullets, self.resume_meta, llm_prompt="Summarize fit", context={"archetype": "enterprise", "channel": "referral"})
        self.assertIn("heuristic", result)
        self.assertIn("ml", result)
        self.assertIn("llm", result)
        self.assertIn("aggregate", result)
        self.assertIn("feedback", result)
        feedback = result["feedback"]
        self.assertIsInstance(feedback, list)
        self.assertGreater(len(feedback), 0)
        # Check feedback structure and context-awareness
        for item in feedback:
            self.assertIn("message", item)
            self.assertIn("severity", item)
            self.assertIn("evidence", item)
            self.assertIn("rubric", item)
            self.assertIn("priority", item)
            self.assertIn("category", item)
        # Check for LLM feedback presence
        self.assertTrue(
            any(item["category"] == "llm" for item in feedback),
            "Missing llm feedback",
        )
        # Check for analytics summary
        self.assertTrue(
            any(item["category"] == "analytics" for item in feedback),
            "Missing analytics feedback",
        )

if __name__ == '__main__':
    unittest.main()
