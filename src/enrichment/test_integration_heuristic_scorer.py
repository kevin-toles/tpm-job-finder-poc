import unittest
import logging
import io
import json
from src.enrichment.heuristic_scorer import HeuristicScorer
from audit_logger.logger import setup_logger, JsonFormatter, log_structured, set_correlation_id

class TestHeuristicScorerAuditIntegration(unittest.TestCase):
    def setUp(self):
        # HeuristicScorer setup
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
        # Audit logger setup
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setFormatter(JsonFormatter())
        self.logger = setup_logger()
        self.logger.handlers = []
        self.logger.addHandler(self.handler)
        set_correlation_id('scorer-corr-id')

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        self.stream.close()

    def test_score_resume_audit_logging(self):
        job_desc = {
            "keywords": ["TPM", "agile", "cloud"],
            "responsibilities": ["lead projects", "manage teams"],
            "skills": ["python", "jira"],
            "must_haves": ["leadership"],
        }
        bullets = [
            "Led agile teams to deliver cloud projects using python and jira.",
            "Managed teams and improved delivery by 30%."
        ]
        scorer = HeuristicScorer(job_desc)
        result = scorer.score_resume(bullets)
        log_structured(
            logging.INFO,
            "Heuristic scoring result",
            event_type="SCORER_RESULT",
            user_id=42,
            job_id=101,
            timestamp="2025-09-07T12:00:00Z",
            correlation_id='scorer-corr-id',
            details={"score": result["overall_score"], "category": result["category"]}
        )
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        self.assertTrue(any('"event_type": "SCORER_RESULT"' in line for line in output))
        for line in output:
            data = json.loads(line)
            if data.get("event_type") == "SCORER_RESULT":
                self.assertEqual(data["correlation_id"], 'scorer-corr-id')
                self.assertEqual(data["details"]["score"], result["overall_score"])
                self.assertEqual(data["details"]["category"], result["category"])

    def test_audit_logging_error_case(self):
        log_structured(
            logging.INFO,
            "Heuristic scoring error",
            event_type="SCORER_RESULT",
            timestamp="2025-09-07T12:01:00Z",
            correlation_id='scorer-corr-id'
        )
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        found_error = False
        for line in output:
            data = json.loads(line)
            if data.get("event_type") == "SCORER_RESULT" and "audit_schema_error" in data:
                found_error = True
        self.assertTrue(found_error)

if __name__ == '__main__':
    unittest.main()
