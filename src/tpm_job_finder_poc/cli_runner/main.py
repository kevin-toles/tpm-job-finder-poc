"""
Main entry point for CLI Runner component.
Handles argument parsing, pipeline orchestration, error handling, logging, and extensibility.
"""
import argparse
import sys
import os
from ..logging_service.logger import CentralLogger, example_cloud_hook
logger = CentralLogger(name='cli_runner', log_file='cli_runner.log', cloud_hook=example_cloud_hook)
from ..error_service.handler import handle_error
from ..resume.store.store import ResumeStore
from ..resume.uploader.uploader import ResumeUploader
from ..cache.applied_tracker import AlreadyAppliedTracker
from ..cache.dedupe_cache import DedupeCache
from ..enrichment.heuristic_scorer import HeuristicScorer
import pandas as pd

class CLIRunner:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Run the job/resume matching pipeline locally.")
        self._add_arguments()

    def _add_arguments(self):
        self.parser.add_argument('--input', type=str, required=True, help='Path to job data file (Excel, CSV, JSON, etc.)')
        self.parser.add_argument('--resume', type=str, required=True, help='Path to resume file (PDF, DOCX, TXT)')
        self.parser.add_argument('--applied', type=str, required=True, help='Path to already-applied jobs Excel sheet')
        self.parser.add_argument('--output', type=str, required=True, help='Path for output results (Excel, CSV, JSON)')
        self.parser.add_argument('--config', type=str, help='Path to config or .env file (optional)')
        self.parser.add_argument('--log', type=str, help='Path for audit log (optional)')
        self.parser.add_argument('--dry-run', action='store_true', help='Run pipeline without writing output (for testing)')
        self.parser.add_argument('--verbose', action='store_true', help='Print detailed logs to console')
        self.parser.add_argument('--dedupe', action='store_true', help='Enable deduplication')
        self.parser.add_argument('--enrich', action='store_true', help='Enable enrichment/LLM scoring')
        self.parser.add_argument('--export-format', type=str, choices=['excel', 'csv', 'json'], default='excel', help='Specify output format')
        self.parser.add_argument('--feature-toggle', type=str, help='Enable experimental features')

    def run(self):
        args = self.parser.parse_args()
        try:
            self._validate_args(args)
            if args.verbose:
                logger.info("Starting pipeline with arguments", cli_args=vars(args))
            logger.info("pipeline_start", details=vars(args))
            jobs_df = self._load_jobs(args.input)
            resume_store = ResumeStore()
            resume_uploader = ResumeUploader()
            resume_meta = resume_store.save_resume(args.resume, metadata={})
            resume_data = resume_uploader.upload_resume(args.resume)
            applied_tracker = AlreadyAppliedTracker(args.applied)
            applied_job_ids = set()
            if hasattr(applied_tracker, '_load_applied'):
                applied_tracker._load_applied()
                applied_job_ids = set(applied_tracker.filter_unapplied(jobs_df['JobID'].tolist()))
            if args.dedupe:
                dedupe_cache = DedupeCache()
                jobs_df = dedupe_cache.dedupe(jobs_df)
            if args.enrich:
                scorer = HeuristicScorer(job_desc={})
                jobs_df['score'] = jobs_df.apply(lambda row: scorer.score_resume([row.get('description', '')], resume_meta), axis=1)
            if applied_job_ids:
                jobs_df = jobs_df[jobs_df['JobID'].isin(applied_job_ids)]
            if not args.dry_run:
                self._export_results(jobs_df, args.output, args.export_format)
                logger.info("Results written to output", output=args.output, format=args.export_format)
                logger.info("pipeline_export", details={"output": args.output, "format": args.export_format})
            else:
                logger.info("Dry run: results not written.", output=args.output)
                logger.info("pipeline_dry_run", details={"output": args.output})
            logger.info("pipeline_complete")
            if args.verbose:
                logger.info("Pipeline completed successfully.")
        except Exception as e:
            handle_error(e, context={'component': 'cli_runner', 'args': vars(args)})
            sys.exit(1)

    def _validate_args(self, args):
        for arg in ['input', 'resume', 'applied']:
            if not os.path.exists(getattr(args, arg)):
                raise FileNotFoundError(f"{arg} file '{getattr(args, arg)}' does not exist.")

    def _load_jobs(self, input_path):
        if input_path.endswith('.csv'):
            return pd.read_csv(input_path)
        elif input_path.endswith('.xlsx') or input_path.endswith('.xls'):
            return pd.read_excel(input_path)
        elif input_path.endswith('.json'):
            return pd.read_json(input_path)
        else:
            raise ValueError(f"Unsupported job data format: {input_path}")

    def _export_results(self, df, output_path, export_format):
        if export_format == 'excel':
            df.to_excel(output_path, index=False)
        elif export_format == 'csv':
            df.to_csv(output_path, index=False)
        elif export_format == 'json':
            df.to_json(output_path, orient='records')
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

if __name__ == "__main__":
    runner = CLIRunner()
    runner.run()
