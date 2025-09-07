"""
Orchestrator: Integrates HeuristicScorer and MLScorer for resume scoring
Returns combined results and rationales
"""
from src.enrichment.heuristic_scorer import HeuristicScorer
from src.enrichment.ml_scorer import MLScorer

class ResumeScoringOrchestrator:
    def __init__(self, job_desc, ml_model=None):
        self.heuristic = HeuristicScorer(job_desc)
        self.ml = MLScorer(model=ml_model)

    def score_resume(self, bullets, resume_data):
        heuristic_result = self.heuristic.score_resume(bullets)
        ml_result = self.ml.score_resume(resume_data)
        return {
            "heuristic": heuristic_result,
            "ml": ml_result,
            "aggregate": self._aggregate_results(heuristic_result, ml_result)
        }

    def _aggregate_results(self, heuristic_result, ml_result):
        # Simple aggregation: average likelihood, combine rationales
        likelihood = ml_result.get("likelihood_to_pass", 0.0)
        category = heuristic_result.get("category", "Unknown")
        rationale = f"Heuristic: {category}. ML: {ml_result.get('rationale', '')}"
        return {
            "likelihood_to_pass": likelihood,
            "heuristic_category": category,
            "rationale": rationale
        }

# Example usage:
# orchestrator = ResumeScoringOrchestrator(job_desc)
# result = orchestrator.score_resume(bullets, resume_data)
