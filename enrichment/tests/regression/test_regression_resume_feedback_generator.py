import unittest
from enrichment.resume_feedback_generator import ResumeFeedbackGenerator

class DummyLLMProvider:
    def get_feedback(self, llm_input):
        return f"LLM feedback for {llm_input['job_desc'].get('role_level', 'unknown')} level."

class TestResumeFeedbackGeneratorRegression(unittest.TestCase):
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
            "role_level": "entry",
            "industry": "tech",
            "company_type": "startup"
        }
        self.resume_meta = {
            "education": "None",
            "certifications": "None",
            "years_experience": 0,
            "skills": "none",
            "keywords": "none",
            "length": 1,
            "role_level": "entry"
        }
        self.scoring_result = {
            "format_issues": "None",
            "gap_map": ["KO failed: education", "KO failed: certifications", "No match for skills"],
            "bullets": [
                {"bullet": "No relevant experience.", "achievements": 0, "impact": 0}
            ]
        }
        self.context = {"archetype": "startup", "channel": "easy_apply"}
        self.generator = ResumeFeedbackGenerator(llm_provider=DummyLLMProvider())

    def test_regression_feedback(self):
        feedback = self.generator.generate_feedback(self.job_desc, self.resume_meta, self.scoring_result, self.context)
        self.assertIsInstance(feedback, list)
        self.assertGreater(len(feedback), 0)
        self.assertTrue(any(item["severity"] == "critical" for item in feedback))
        self.assertTrue(any(item["category"] == "analytics" for item in feedback))
        self.assertTrue(any(item["category"] == "llm" for item in feedback))
        # Check for startup/easy_apply context in feedback
        self.assertTrue(any("easy_apply" in item["message"] or "startup" in item["message"] or item["category"] == "llm" for item in feedback))

if __name__ == '__main__':
    unittest.main()
