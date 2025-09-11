"""
CLI entry point for Job/Resume Matching Pipeline
Moved main() here to avoid circular import issues.
"""
import argparse
import sys
import os
from tpm_job_finder_poc.audit_logger.logger import AuditLogger
from tpm_job_finder_poc.resume_store.store import ResumeStore
from tpm_job_finder_poc.resume_uploader.uploader import ResumeUploader
from tpm_job_finder_poc.cache.applied_tracker import AlreadyAppliedTracker
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache
from tpm_job_finder_poc.enrichment.heuristic_scorer import HeuristicScorer
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Run the job/resume matching pipeline locally.")
    parser.add_argument('--input', type=str, required=True, help='Path to job data file (Excel, CSV, JSON, etc.)')
    parser.add_argument('--resume', type=str, required=True, help='Path to resume file (PDF, DOCX, TXT)')
    parser.add_argument('--applied', type=str, required=True, help='Path to already-applied jobs Excel sheet')
    parser.add_argument('--output', type=str, required=True, help='Path for output results (Excel, CSV, JSON)')
    parser.add_argument('--config', type=str, help='Path to config or .env file (optional)')
    parser.add_argument('--log', type=str, help='Path for audit log (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Run pipeline without writing output (for testing)')
    parser.add_argument('--verbose', action='store_true', help='Print detailed logs to console')
    parser.add_argument('--dedupe', action='store_true', help='Enable deduplication')
    parser.add_argument('--enrich', action='store_true', help='Enable enrichment/LLM scoring')
    parser.add_argument('--export-format', type=str, choices=['excel', 'csv', 'json'], default='excel', help='Specify output format')
    parser.add_argument('--feature-toggle', type=str, help='Enable experimental features')
    args = parser.parse_args()

    # Validate file paths
    for arg in ['input', 'resume', 'applied']:
        if not os.path.exists(getattr(args, arg)):
            print(f"Error: {arg} file '{getattr(args, arg)}' does not exist.", file=sys.stderr)
            sys.exit(1)

    if args.verbose:
        print("Starting pipeline with arguments:", vars(args))

    # Log start of run
    if args.log:
        AuditLogger.set_log_path(args.log)
    AuditLogger.log("pipeline_start", details=vars(args))

    # 1. Load job data
    if args.input.endswith('.csv'):
        jobs_df = pd.read_csv(args.input)
    elif args.input.endswith('.xlsx') or args.input.endswith('.xls'):
        jobs_df = pd.read_excel(args.input)
    elif args.input.endswith('.json'):
        jobs_df = pd.read_json(args.input)
    else:
        print(f"Unsupported job data format: {args.input}", file=sys.stderr)
        sys.exit(1)

    # 2. Load resume
    resume_store = ResumeStore()
    resume_uploader = ResumeUploader()
    resume_meta = resume_store.save_resume(args.resume, metadata={})
    resume_data = resume_uploader.upload_resume(args.resume)

    # 3. Load applied jobs
    applied_tracker = AlreadyAppliedTracker(args.applied)
    applied_job_ids = set()
    if hasattr(applied_tracker, '_load_applied'):
        applied_tracker._load_applied()
        applied_job_ids = set(applied_tracker.filter_unapplied(jobs_df['JobID'].tolist()))

    # 4. Dedupe jobs (if enabled)
    if args.dedupe:
        dedupe_cache = DedupeCache()
        jobs_df = dedupe_cache.dedupe(jobs_df)

    # 5. Enrich jobs (if enabled)
    if args.enrich:
        scorer = HeuristicScorer(job_desc={})
        jobs_df['score'] = jobs_df.apply(lambda row: scorer.score_resume([row.get('description', '')], resume_meta), axis=1)

    # 6. Filter out already applied
    if applied_job_ids:
        jobs_df = jobs_df[jobs_df['JobID'].isin(applied_job_ids)]

    # 7. Export results (unless dry-run)
    if not args.dry_run:
        if args.export_format == 'excel':
            jobs_df.to_excel(args.output, index=False)
        elif args.export_format == 'csv':
            jobs_df.to_csv(args.output, index=False)
        elif args.export_format == 'json':
            jobs_df.to_json(args.output, orient='records')
        else:
            print(f"Unsupported export format: {args.export_format}", file=sys.stderr)
            sys.exit(1)
        print(f"Results written to {args.output} in format {args.export_format}.")
        AuditLogger.log("pipeline_export", details={"output": args.output, "format": args.export_format})
    else:
        print("Dry run: results not written.")
        AuditLogger.log("pipeline_dry_run", details={"output": args.output})

    # 8. Log completion
    AuditLogger.log("pipeline_complete")
    if args.verbose:
        print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
