#!/usr/bin/env python3
"""
Automated CLI for TPM Job Finder - Complete automation workflow.

This CLI implements the user's desired 5-step automated workflow:
1. Upload/process resume  
2. Run daily job search across all sources
3. Score and enrich results
4. Export to Excel for review
5. Enable cron/GitHub Actions automation

Usage Examples:
  # Daily automated search with resume
  python -m tpm_job_finder_poc.cli.automated_cli daily-search --resume /path/to/resume.pdf

  # Quick search without resume processing
  python -m tpm_job_finder_poc.cli.automated_cli quick-search --keywords "product manager" --location "Remote"

  # Setup cron job (outputs cron command)
  python -m tpm_job_finder_poc.cli.automated_cli setup-cron --resume /path/to/resume.pdf --time "09:00"
"""

import asyncio
import argparse
import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging for automation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/automated_cli.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AutomatedJobFinderCLI:
    """Main CLI class for automated job search workflows."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize CLI with configuration."""
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create defaults."""
        default_config = {
            'search_params': {
                'keywords': ['product manager', 'technical product manager', 'tpm', 'program manager'],
                'location': 'Remote',
                'max_jobs_per_source': 50
            },
            'output': {
                'directory': './output',
                'format': 'excel',
                'filename_template': 'daily_jobs_{date}.xlsx'
            },
            'enrichment': {
                'enable_scoring': True,
                'enable_feedback': True,
                'min_score_threshold': 0.3
            },
            'automation': {
                'cron_time': '09:00',
                'notify_email': None,
                'backup_results': True
            }
        }
        
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Deep merge with defaults
                    self._deep_merge_config(default_config, user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                
        return default_config
        
    def _deep_merge_config(self, base: Dict, override: Dict) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_config(base[key], value)
            else:
                base[key] = value
                
    async def run_daily_search(self, resume_path: str, output_path: Optional[str] = None) -> str:
        """
        Run the complete daily job search workflow.
        
        This implements the user's 5-step process:
        1. Process resume
        2. Collect jobs from all sources  
        3. Score and enrich
        4. Export to Excel
        5. Log results for tracking
        """
        try:
            logger.info("=== Starting Daily Automated Job Search ===")
            
            # Import services (lazy loading to avoid circular imports)
            from .runner import AutomatedJobSearchRunner
            
            runner = AutomatedJobSearchRunner(self.config_path)
            
            # Generate output path if not provided
            if not output_path:
                date_str = datetime.now().strftime("%Y%m%d")
                filename = self.config['output']['filename_template'].format(date=date_str)
                output_path = str(Path(self.config['output']['directory']) / filename)
                
            # Run the complete workflow
            result_path = await runner.run_daily_search_workflow(
                resume_path=resume_path,
                output_path=output_path
            )
            
            logger.info(f"Daily search completed successfully: {result_path}")
            
            # Print success message for automation scripts
            print(f"SUCCESS: {result_path}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Daily search failed: {e}")
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
            
    async def run_quick_search(self, 
                              keywords: List[str], 
                              location: str = "Remote",
                              output_path: Optional[str] = None) -> str:
        """Run a quick job search without resume processing."""
        try:
            logger.info(f"=== Starting Quick Job Search: {keywords} ===")
            
            from .runner import AutomatedJobSearchRunner
            
            runner = AutomatedJobSearchRunner(self.config_path)
            
            result_path = await runner.run_quick_search(
                keywords=keywords,
                location=location
            )
            
            logger.info(f"Quick search completed: {result_path}")
            print(f"SUCCESS: {result_path}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Quick search failed: {e}")
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
            
    def setup_cron_job(self, resume_path: str, cron_time: str = "09:00") -> None:
        """Generate cron job command for daily automation."""
        try:
            # Get absolute paths
            script_path = Path(__file__).resolve()
            resume_path = Path(resume_path).resolve()
            
            # Parse cron time (HH:MM format)
            hour, minute = cron_time.split(":")
            
            # Generate cron command
            cron_command = (
                f"{minute} {hour} * * * "
                f"cd {Path.cwd()} && "
                f"python -m tpm_job_finder_poc.cli.automated_cli daily-search "
                f"--resume '{resume_path}' "
                f"--config '{self.config_path or ''}' "
                f">> ./logs/cron_daily_search.log 2>&1"
            )
            
            print("=== Cron Job Setup ===")
            print(f"Add the following line to your crontab (crontab -e):")
            print()
            print(cron_command)
            print()
            print("This will run daily job search at", cron_time)
            print()
            print("To install:")
            print("1. Run: crontab -e")  
            print("2. Add the above line")
            print("3. Save and exit")
            print()
            print("To check: crontab -l")
            print("To remove: crontab -r")
            
        except Exception as e:
            logger.error(f"Cron setup failed: {e}")
            print(f"ERROR: {e}", file=sys.stderr)
            
    def setup_github_actions(self, resume_path: str) -> None:
        """Generate GitHub Actions workflow for automation."""
        try:
            workflow_content = f'''# Auto-generated GitHub Actions workflow for TPM Job Finder
name: Daily Job Search

on:
  schedule:
    # Run daily at 9 AM UTC (adjust timezone as needed)
    - cron: '0 9 * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  daily-job-search:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Create logs directory
      run: mkdir -p ./logs
      
    - name: Run daily job search
      run: |
        python -m tpm_job_finder_poc.cli.automated_cli daily-search \\
          --resume "{resume_path}" \\
          --config "config/automation.json"
      env:
        # Add your API keys as GitHub Secrets
        OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
        ANTHROPIC_API_KEY: ${{{{ secrets.ANTHROPIC_API_KEY }}}}
        
    - name: Upload results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: daily-job-results
        path: |
          ./output/
          ./logs/
        retention-days: 30
'''

            # Write to .github/workflows/
            workflow_dir = Path('.github/workflows')
            workflow_dir.mkdir(parents=True, exist_ok=True)
            
            workflow_file = workflow_dir / 'daily-job-search.yml'
            
            with open(workflow_file, 'w') as f:
                f.write(workflow_content)
                
            print("=== GitHub Actions Setup ===")
            print(f"Created workflow file: {workflow_file}")
            print()
            print("Setup steps:")
            print("1. Commit and push the .github/workflows/daily-job-search.yml file")
            print("2. Add API keys as GitHub Secrets:")
            print("   - Go to Settings > Secrets and variables > Actions")
            print("   - Add: OPENAI_API_KEY, ANTHROPIC_API_KEY")
            print("3. The workflow will run daily at 9 AM UTC")
            print("4. Results will be available in the Actions tab as artifacts")
            
        except Exception as e:
            logger.error(f"GitHub Actions setup failed: {e}")
            print(f"ERROR: {e}", file=sys.stderr)
            
    def create_sample_config(self) -> None:
        """Create a sample configuration file."""
        config_path = Path('./config/automation_config.json')
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
        print(f"Sample configuration created at: {config_path}")
        print("Customize the settings and use with --config flag")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Automated TPM Job Finder CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run daily automated search
  python -m tpm_job_finder_poc.cli.automated_cli daily-search --resume resume.pdf
  
  # Quick search for specific keywords  
  python -m tpm_job_finder_poc.cli.automated_cli quick-search --keywords "senior product manager"
  
  # Setup automation
  python -m tpm_job_finder_poc.cli.automated_cli setup-cron --resume resume.pdf --time "08:30"
        """
    )
    
    # Global arguments
    parser.add_argument('--config', type=str, help='Path to configuration JSON file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Daily search command
    daily_parser = subparsers.add_parser('daily-search', help='Run complete daily job search workflow')
    daily_parser.add_argument('--resume', type=str, required=True, help='Path to resume file (PDF, DOCX)')
    daily_parser.add_argument('--output', type=str, help='Custom output path for results')
    
    # Quick search command  
    quick_parser = subparsers.add_parser('quick-search', help='Run quick job search without resume')
    quick_parser.add_argument('--keywords', nargs='+', required=True, help='Job search keywords')
    quick_parser.add_argument('--location', type=str, default='Remote', help='Job location')
    quick_parser.add_argument('--output', type=str, help='Custom output path for results')
    
    # Cron setup command
    cron_parser = subparsers.add_parser('setup-cron', help='Generate cron job for daily automation')
    cron_parser.add_argument('--resume', type=str, required=True, help='Path to resume file')
    cron_parser.add_argument('--time', type=str, default='09:00', help='Daily run time (HH:MM)')
    
    # GitHub Actions setup command
    github_parser = subparsers.add_parser('setup-github-actions', help='Generate GitHub Actions workflow')
    github_parser.add_argument('--resume', type=str, required=True, help='Path to resume file')
    
    # Config management commands
    config_parser = subparsers.add_parser('create-config', help='Create sample configuration file')
    
    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Create CLI instance
    cli = AutomatedJobFinderCLI(args.config)
    
    # Route to appropriate command
    try:
        if args.command == 'daily-search':
            await cli.run_daily_search(args.resume, args.output)
            
        elif args.command == 'quick-search':
            await cli.run_quick_search(args.keywords, args.location, args.output)
            
        elif args.command == 'setup-cron':
            cli.setup_cron_job(args.resume, args.time)
            
        elif args.command == 'setup-github-actions':
            cli.setup_github_actions(args.resume)
            
        elif args.command == 'create-config':
            cli.create_sample_config()
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Ensure output directories exist
    Path('./logs').mkdir(exist_ok=True)
    Path('./output').mkdir(exist_ok=True)
    
    # Run async main
    asyncio.run(main())
