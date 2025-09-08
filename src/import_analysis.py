import pandas as pd
from typing import List, Dict, Any

class ImportAnalysis:
    def save_results(self, results: dict, output_path: str):
        """
        Save analysis results to a JSON file for downstream consumption.
        Args:
            results: Output from analyze().
            output_path: Path to save the JSON file.
        """
        import json
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
    """
    ImportAnalysis reads and analyzes an Excel sheet of job matches and outcomes.
    Usage:
        analysis = ImportAnalysis()
        results = analysis.analyze('path/to/master_sheet.xlsx')
        print(results['Callback_rate'])
        print(results['score_success_correlation'])
    """
    def __init__(self, job_id_col: str = "Job ID", status_cols: List[str] = None, score_col: str = "Match Score", feedback_col: str = "Resume Feedback"):
        """
        Args:
            job_id_col: Name of the job ID column.
            status_cols: List of status columns (e.g., Callback, Interview, Offer).
            score_col: Name of the match score column.
            feedback_col: Name of the feedback column.
        """
        self.job_id_col = job_id_col
        self.status_cols = status_cols or ["Callback", "Interview", "Offer"]
        self.score_col = score_col
        self.feedback_col = feedback_col

    def analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Reads and analyzes the imported Excel sheet.
        Returns summary metrics, annotated records, and signals for model improvement.
        Args:
            file_path: Path to the Excel file.
        Returns:
            Dictionary with rates, correlations, feedback stats, and records.
        """
        df = pd.read_excel(file_path)
        results = {}
        # Aggregate success rates
        for status in self.status_cols:
            if status in df.columns:
                results[f"{status}_rate"] = df[status].notnull().mean()
        # Score correlation
        if self.score_col in df.columns:
            score_success = {}
            for status in self.status_cols:
                if status in df.columns:
                    score_success[status] = df.groupby(self.score_col)[status].apply(lambda x: x.notnull().mean()).to_dict()
            results["score_success_correlation"] = score_success
        # Feedback effectiveness
        if self.feedback_col in df.columns:
            feedback_stats = df[self.feedback_col].value_counts().to_dict()
            results["feedback_stats"] = feedback_stats
        # Annotated records
        results["records"] = df.to_dict(orient="records")
        return results
