# TPM Job Finder - Automated Job Search CLI

This document explains how to use the complete automated job search workflow that was implemented to address your specific requirements.

## Overview

The automated CLI implements your exact 5-step workflow:

1. **Upload/Process Resume** - Parse and extract your skills/experience  
2. **Daily Job Search** - Collect jobs from all sources (APIs + scrapers)
3. **Score & Enrich** - Match jobs to your profile and generate fit scores
4. **Export to Excel** - Create formatted spreadsheet with tracking columns
5. **Enable Automation** - Set up cron jobs or GitHub Actions for daily runs

## Quick Start

### 1. Run Daily Automated Search

```bash
# Complete daily workflow with your resume
python -m tpm_job_finder_poc.cli.automated_cli daily-search --resume /path/to/your/resume.pdf

# With custom configuration
python -m tpm_job_finder_poc.cli.automated_cli daily-search \
  --resume /path/to/your/resume.pdf \
  --config ./config/automation_config.json \
  --output ./output/today_jobs.xlsx
```

### 2. Quick Search (No Resume Needed)

```bash
# Quick search for specific keywords
python -m tpm_job_finder_poc.cli.automated_cli quick-search \
  --keywords "senior product manager" "technical product manager" \
  --location "Remote"
```

## Automation Setup

### Option 1: Cron Job (Linux/Mac)

```bash
# Generate cron job command
python -m tpm_job_finder_poc.cli.automated_cli setup-cron \
  --resume /path/to/your/resume.pdf \
  --time "09:00"

# This outputs the exact cron command to add to your crontab
# Example output:
# 0 9 * * * cd /path/to/project && python -m tpm_job_finder_poc.cli.automated_cli daily-search --resume '/path/to/resume.pdf' >> ./logs/cron_daily_search.log 2>&1

# To install:
crontab -e
# Paste the generated command
# Save and exit
```

### Option 2: GitHub Actions (Recommended)

```bash
# Generate GitHub Actions workflow
python -m tpm_job_finder_poc.cli.automated_cli setup-github-actions \
  --resume /path/to/your/resume.pdf

# This creates .github/workflows/daily-job-search.yml
# Commit and push to enable automation
# Add API keys as GitHub Secrets:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY (if using Anthropic)
```

## Excel Output Format

The generated Excel file includes these columns for your workflow:

| Column | Description | Your Usage |
|--------|-------------|------------|
| **Title** | Job title | Review for relevance |
| **Company** | Company name | Research company |
| **Location** | Job location | Check if acceptable |
| **Match Score** | AI-calculated fit (0-1) | Prioritize high scores |
| **Recommended Action** | Apply/Consider/Skip | Follow AI guidance |
| **Applied** | "No" (default) | **Update to "Yes" after applying** |
| **Status** | "New" (default) | **Track: Applied/Interview/Rejected** |
| **Notes** | Empty | **Add your notes/feedback** |
| **URL** | Application link | Click to apply |
| **Fit Analysis** | Why it matches | Understand the match |

## Your Daily Workflow

1. **Morning**: Receive Excel file from automated search
2. **Review**: Sort by Match Score, focus on "High Priority" jobs  
3. **Apply**: Use URLs to apply, mark "Applied" = "Yes"
4. **Track**: Update "Status" column as you hear back
5. **Feedback**: Add notes about why you applied/rejected
6. **Upload Updated Resume** (weekly): Re-run with updated resume to improve matching

## Configuration

### Create Custom Config

```bash
# Generate sample configuration
python -m tpm_job_finder_poc.cli.automated_cli create-config

# Edit config/automation_config.json to customize:
# - Search keywords
# - Job sources to use
# - Scoring preferences  
# - Output formats
```

### Sample Configuration

```json
{
  "search_params": {
    "keywords": [
      "product manager",
      "technical product manager", 
      "senior product manager"
    ],
    "location": "Remote",
    "max_jobs_per_source": 50
  },
  "enrichment": {
    "enable_scoring": true,
    "min_score_threshold": 0.4,
    "llm_provider": "openai"
  },
  "automation": {
    "cron_time": "09:00",
    "max_daily_jobs": 200
  }
}
```

## Job Sources

### API-Based Aggregators
- **RemoteOK**: Remote jobs from multiple sources
- **Greenhouse**: Direct company job boards (Airbnb, Stripe, etc.)
- **Lever**: Company job boards (configurable)
- **Ashby**: Modern ATS job boards
- **Workable**: Company career pages
- **SmartRecruiters**: Enterprise job boards

### Browser Scrapers (from Phase 2)
- **Indeed**: Largest job board
- **LinkedIn**: Professional network jobs
- **ZipRecruiter**: Aggregated job postings  
- **Greenhouse Browser**: Backup scraper for Greenhouse

## Troubleshooting

### Common Issues

1. **"No jobs found"**
   - Check your keywords are not too specific
   - Verify job sources are accessible
   - Review logs in `./logs/automated_cli.log`

2. **"Resume processing failed"** 
   - Ensure resume file exists and is readable
   - Supported formats: PDF, DOCX, TXT
   - Check file permissions

3. **"Scoring disabled"**
   - Set `"enable_scoring": true` in config
   - Ensure API keys are available
   - Check LLM provider configuration

### Logs and Debugging

```bash
# View automation logs
tail -f ./logs/automated_cli.log

# Run with verbose output
python -m tpm_job_finder_poc.cli.automated_cli daily-search \
  --resume resume.pdf --verbose

# Test configuration
python -m tpm_job_finder_poc.cli.automated_cli create-config
```

## Integration with Existing Services

The automated CLI integrates all existing project components:

- **Job Aggregator** (`job_aggregator/main.py`) - Orchestrates all job collection
- **Browser Scrapers** (`scraping_service_v2/`) - Phase 2 scraper architecture  
- **Enrichment Services** (`enrichment/`) - AI scoring and analysis
- **Resume Processing** (`resume_uploader/`) - Extract skills and experience
- **Deduplication** (`cache/dedupe_cache.py`) - Remove duplicate jobs
- **Export Tools** - Enhanced Excel formatting

## Example Complete Workflow

```bash
# 1. Initial setup (once)
python -m tpm_job_finder_poc.cli.automated_cli create-config
python -m tpm_job_finder_poc.cli.automated_cli setup-cron --resume resume.pdf --time "08:00"

# 2. Daily automation (via cron)
# Runs automatically every morning at 8 AM
# Generates: ./output/daily_jobs_YYYYMMDD.xlsx

# 3. Your morning routine
# - Open Excel file
# - Sort by Match Score  
# - Apply to "High Priority" jobs
# - Mark Applied = "Yes" and add notes
# - Track status as you hear back

# 4. Weekly resume updates
python -m tpm_job_finder_poc.cli.automated_cli daily-search --resume updated_resume.pdf

# 5. Quick ad-hoc searches
python -m tpm_job_finder_poc.cli.automated_cli quick-search --keywords "principal product manager"
```

This implements exactly the automated workflow you requested, with full integration of all existing services and the ability to run daily searches via cron or GitHub Actions.
