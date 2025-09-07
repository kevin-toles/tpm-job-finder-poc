import unittest
from src.enrichment.resume_feedback_generator import ResumeFeedbackGenerator

class DummyLLMProvider:
    def get_feedback(self, llm_input):
        return f"LLM feedback for {llm_input['job_desc'].get('role_level', 'unknown')} level."

class TestResumeFeedbackGeneratorUnit(unittest.TestCase):
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
            "role_level": "senior",
            "industry": "tech",
            "company_type": "enterprise"
        }
        self.resume_meta = {
            "education": "BS Computer Science",
            "certifications": "PMP",
            "years_experience": 6,
            "skills": "python, jira",
            "keywords": "TPM, agile, cloud",
            "length": 2,
            "role_level": "senior"
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

    def test_feedback_structure(self):
        feedback = self.generator.generate_feedback(self.job_desc, self.resume_meta, self.scoring_result, self.context)
        self.assertIsInstance(feedback, list)
        self.assertGreater(len(feedback), 0)
        for item in feedback:
            self.assertIn("message", item)
            self.assertIn("severity", item)
            self.assertIn("evidence", item)
            self.assertIn("rubric", item)
            self.assertIn("priority", item)
            self.assertIn("category", item)

    def test_severity_and_priority(self):
        feedback = self.generator.generate_feedback(self.job_desc, self.resume_meta, self.scoring_result, self.context)
        severities = {item["severity"] for item in feedback}
        self.assertIn("critical", severities)
        priorities = [item["priority"] for item in feedback]
        self.assertTrue(any(p >= 2 for p in priorities))

    def test_llm_feedback_integration(self):
        feedback = self.generator.generate_feedback(self.job_desc, self.resume_meta, self.scoring_result, self.context)
        llm_items = [item for item in feedback if item["category"] == "llm"]
        self.assertTrue(any("LLM feedback" in item["message"] for item in llm_items))

    def test_analytics_summary(self):
        feedback = self.generator.generate_feedback(self.job_desc, self.resume_meta, self.scoring_result, self.context)
        analytics_items = [item for item in feedback if item["category"] == "analytics"]
        self.assertTrue(any("Analytics summary" in item["message"] for item in analytics_items))

if __name__ == '__main__':
    unittest.main()
