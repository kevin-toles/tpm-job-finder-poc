import unittest
from src.enrichment.orchestrator import ResumeScoringOrchestrator
from src.enrichment.heuristic_scorer import HeuristicScorer
from src.enrichment.ml_scorer import MLScorer

class DummyLLMProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key
    def get_signals(self, prompt):
        return {"provider": "DummyLLM", "response": f"Rationale for: {prompt}"}

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

    def test_e2e_orchestrator_with_llm(self):
        result = self.orchestrator.score_resume(self.bullets, self.resume_meta, llm_prompt="Summarize fit")
        self.assertIn("heuristic", result)
        self.assertIn("ml", result)
        self.assertIn("llm", result)
        self.assertIn("aggregate", result)
        self.assertEqual(result["llm"]["provider"], "DummyLLM")
        self.assertIn("Rationale for: Summarize fit", result["llm"]["response"])
        self.assertIn("LLM: Rationale for: Summarize fit", result["aggregate"]["rationale"])
        # Validate semantic similarity scores in aggregate output
        agg = result["aggregate"]
        self.assertIn("avg_resp_sem_sim", agg)
        self.assertIn("avg_skill_sem_sim", agg)
        self.assertIsInstance(agg["avg_resp_sem_sim"], float)
        self.assertIsInstance(agg["avg_skill_sem_sim"], float)

if __name__ == '__main__':
    unittest.main()
