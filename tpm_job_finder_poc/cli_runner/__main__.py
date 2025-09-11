import sys
import argparse
from tpm_job_finder_poc.cli_runner.main import CLIRunner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input')
    parser.add_argument('--resume')
    parser.add_argument('--applied')
    parser.add_argument('--output')
    parser.add_argument('--log')
    parser.add_argument('--export-format', default='csv')
    parser.add_argument('--dedupe', action='store_true')
    parser.add_argument('--enrich', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    import pandas as pd
    import re
    import logging
    # Setup logging to both file and console
    log_path = args.log or 'cli_runner.log'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ])
    runner = CLIRunner()
    try:
        print("[DEBUG] Validating args...")
        runner._validate_args(args)
        print("[DEBUG] Loading input files...")
        jobs_df = pd.read_json(args.input)
        print("[DEBUG] Loaded jobs_df:", jobs_df.head())
        resume_text = open(args.resume).read().lower()
        print("[DEBUG] Loaded resume text.")
        applied_df = pd.read_excel(args.applied)
        print("[DEBUG] Loaded applied_df:", applied_df.head())
        logging.info('Loaded input files successfully.')
        # Patch: Map 'position' to 'Title' if 'Title' is missing
        if 'Title' not in jobs_df.columns and 'position' in jobs_df.columns:
            print("[DEBUG] 'Title' column missing, mapping 'position' to 'Title'.")
            jobs_df['Title'] = jobs_df['position']
            # Optionally map 'Company' and 'Location' if present
            if 'company' in jobs_df.columns and 'Company' not in jobs_df.columns:
                jobs_df['Company'] = jobs_df['company']
            if 'location' in jobs_df.columns and 'Location' not in jobs_df.columns:
                jobs_df['Location'] = jobs_df['location']
        # Deduplication
        print("[DEBUG] Deduplication step...")
        if args.dedupe:
            dedupe_cols = ['Title', 'Company', 'Location']
            missing_cols = [col for col in dedupe_cols if col not in jobs_df.columns]
            if missing_cols:
                print(f"[DEBUG] Deduplication skipped, missing columns: {missing_cols}")
                logging.warning(f"Deduplication skipped, missing columns: {missing_cols}")
            else:
                jobs_df = jobs_df.drop_duplicates(subset=dedupe_cols)
                print("[DEBUG] Deduplication applied.")
                logging.info('Deduplication applied.')
        # Enrichment (add a dummy enrichment column)
        print("[DEBUG] Enrichment step...")
        if args.enrich:
            jobs_df['Enriched'] = jobs_df['Title'].apply(lambda t: f"Enriched: {t}")
            print("[DEBUG] Enrichment applied.")
            logging.info('Enrichment applied.')
        # Extract keywords from resume
        print("[DEBUG] Scoring step...")
        resume_keywords = set(re.findall(r'\w+', resume_text))
        def score_job(row):
            reqs = row.get('Requirements', [])
            desc = row.get('Description', '')
            job_text = ' '.join(reqs) + ' ' + desc.lower()
            job_keywords = set(re.findall(r'\w+', job_text))
            matches = resume_keywords & job_keywords
            return len(matches) / max(1, len(resume_keywords))
        jobs_df['score'] = jobs_df.apply(score_job, axis=1)
        print("[DEBUG] Scoring completed.")
        logging.info('Scoring completed.')
        # Filter out applied jobs
        print("[DEBUG] Filtering applied jobs...")
        if 'JobID' in applied_df.columns:
            applied_ids = set(applied_df['JobID'])
            jobs_df = jobs_df[~jobs_df['JobID'].isin(applied_ids)]
            print("[DEBUG] Filtered out applied jobs.")
            logging.info('Filtered out applied jobs.')
        # Sort by score descending
        print("[DEBUG] Sorting jobs by score...")
        jobs_df = jobs_df.sort_values(by='score', ascending=False)
        out_path = args.output
        print(f"[DEBUG] About to export results to {out_path} with format {args.export_format}")
        logging.info(f'[DEBUG] About to export results to {out_path} with format {args.export_format}')
        try:
            runner._export_results(jobs_df, out_path, args.export_format)
            logging.info(f'Exported results to {out_path}')
            print(f"Exported results to {out_path}")
        except Exception as export_exc:
            print(f"[ERROR] Export failed: {export_exc}")
            logging.error(f"Export failed: {export_exc}")
        print("[DEBUG] CLI runner finished.")
    except Exception as e:
        print(f"[ERROR] Error in CLI runner: {e}")
        logging.error(f"Error in CLI runner: {e}")

if __name__ == "__main__":
    main()
