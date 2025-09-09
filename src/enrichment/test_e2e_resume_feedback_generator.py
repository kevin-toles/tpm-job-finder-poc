import unittest
from src.enrichment.orchestrator import ResumeScoringOrchestrator

class DummyLLMProvider:
    def get_signals(self, prompt):
        return {"provider": "DummyLLM", "response": f"Rationale for: {prompt}"}
    def get_feedback(self, llm_input):
        return f"LLM feedback for {llm_input['job_desc'].get('role_level', 'unknown')} level."

class TestResumeFeedbackGeneratorE2E(unittest.TestCase):
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
            "role_level": "executive",
            "industry": "tech",
            "company_type": "enterprise"
        }
        self.resume_meta = {
            "education": "BS Computer Science",
            "certifications": "PMP",
            "years_experience": 6,
            "skills": "python, jira",
            "keywords": "TPM, agile, cloud",
            "length": 3,
            "role_level": "executive"
        }
        self.bullets = [
            "Managed teams and delivered cloud projects.",
            "Launched new product and led agile teams."
        ]
        self.context = {"archetype": "enterprise", "channel": "referral"}
        ResumeScoringOrchestrator._init_llm = lambda self, cfg: DummyLLMProvider()
        self.orchestrator = ResumeScoringOrchestrator(self.job_desc, llm_config={"provider": "dummy"})

    def test_e2e_feedback_in_orchestrator(self):
        result = self.orchestrator.score_resume(self.bullets, self.resume_meta, llm_prompt="Summarize fit", context=self.context)
        self.assertIn("feedback", result)
        feedback = result["feedback"]
        self.assertIsInstance(feedback, list)
        self.assertGreater(len(feedback), 0)
        self.assertTrue(any(item["severity"] == "critical" for item in feedback))
        self.assertTrue(any(item["category"] == "analytics" for item in feedback))
        self.assertTrue(any(item["category"] == "llm" for item in feedback))
        # Check for referral/enterprise context in feedback
        # Ensure all feedback items have 'category' key
        for item in feedback:
            self.assertIn("category", item)

if __name__ == '__main__':
    unittest.main()
