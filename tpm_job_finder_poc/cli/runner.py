"""
CLI runner for automated TPM Job Finder workflows.

Provides complete automation interface for daily job searches,
including resume processing, job collection, scoring, and export.
"""

import sys
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cli_runner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AutomatedJobSearchRunner:
    """
    Main CLI runner for automated job search workflows.
    
    Orchestrates the complete pipeline from resume upload to 
    scored job results export.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the runner with configuration."""
        self.config = self._load_config(config_path)
        self.setup_services()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'search_params': {
                'keywords': ['product manager', 'technical product manager', 'tpm'],
                'location': 'Remote',
                'max_jobs_per_source': 50
            },
            'output': {
                'format': 'excel',
                'path': './output/daily_jobs.xlsx'
            },
            'resume': {
                'path': None,  # Will be provided via CLI
                'auto_reprocess': True
            },
            'enrichment': {
                'enable_scoring': True,
                'enable_feedback': True,
                'llm_provider': 'openai'
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                
        return default_config
        
    def setup_services(self):
        """Initialize all required services."""
        try:
            # Import services
            from ..job_aggregator.main import JobAggregatorService
            from ..enrichment.orchestrator import ResumeScoringOrchestrator
            from ..resume_uploader.uploader import ResumeUploader
            
            self.job_aggregator = JobAggregatorService(self.config)
            self.enrichment_service = ResumeScoringOrchestrator(job_desc={}) # Provide empty job desc for initialization
            self.resume_uploader = ResumeUploader()
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
            
    async def run_daily_search_workflow(self, 
                                       resume_path: str,
                                       output_path: Optional[str] = None) -> str:
        """
        Run the complete daily job search workflow.
        
        This is the main automation method that implements the user's 
        5-step workflow:
        1. Upload/process resume
        2. Run daily job search
        3. Score and enrich results  
        4. Export to Excel
        5. Prepare for user review
        
        Args:
            resume_path: Path to resume file
            output_path: Optional custom output path
            
        Returns:
            Path to generated Excel file
        """
        workflow_start = datetime.now()
        logger.info(f"Starting daily job search workflow at {workflow_start}")
        
        try:
            # Step 1: Process Resume
            logger.info("Step 1: Processing resume...")
            resume_data = await self._process_resume(resume_path)
            
            # Step 2: Run Job Aggregation
            logger.info("Step 2: Collecting jobs from all sources...")
            raw_jobs = await self._collect_jobs()
            
            # Step 3: Enrich and Score Jobs
            logger.info("Step 3: Enriching and scoring jobs...")
            scored_jobs = await self._enrich_and_score_jobs(raw_jobs, resume_data)
            
            # Step 4: Export Results
            logger.info("Step 4: Exporting results...")
            excel_path = await self._export_results(
                scored_jobs, 
                output_path or self.config['output']['path']
            )
            
            # Step 5: Log Summary
            workflow_duration = datetime.now() - workflow_start
            logger.info(f"Workflow completed in {workflow_duration}")
            logger.info(f"Total jobs collected: {len(raw_jobs)}")
            logger.info(f"Jobs after scoring: {len(scored_jobs)}")
            logger.info(f"Results exported to: {excel_path}")
            
            return excel_path
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise
            
    async def _process_resume(self, resume_path: str) -> Dict[str, Any]:
        """Process and extract resume data."""
        try:
            # Upload and parse resume
            upload_result = await self.resume_uploader.upload_resume(resume_path)
            
            if not upload_result.get('success'):
                raise Exception(f"Resume upload failed: {upload_result.get('error')}")
                
            # Extract structured data
            resume_data = {
                'skills': upload_result.get('parsed_data', {}).get('skills', []),
                'experience': upload_result.get('parsed_data', {}).get('experience', []),
                'preferences': self.config.get('search_params', {}),
                'file_path': resume_path
            }
            
            logger.info(f"Resume processed: {len(resume_data['skills'])} skills extracted")
            
            return resume_data
            
        except Exception as e:
            logger.error(f"Resume processing failed: {e}")
            raise
            
    async def _collect_jobs(self) -> List[Dict[str, Any]]:
        """Collect jobs from all configured sources."""
        try:
            search_params = self.config['search_params']
            
            jobs = await self.job_aggregator.run_daily_aggregation(
                search_params=search_params,
                max_jobs_per_source=search_params.get('max_jobs_per_source', 50)
            )
            
            logger.info(f"Collected {len(jobs)} jobs from all sources")
            
            return jobs
            
        except Exception as e:
            logger.error(f"Job collection failed: {e}")
            raise
            
    async def _enrich_and_score_jobs(self, 
                                   jobs: List[Dict[str, Any]], 
                                   resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich jobs with scoring and feedback."""
        try:
            if not self.config['enrichment']['enable_scoring']:
                logger.info("Scoring disabled, returning raw jobs")
                return jobs
                
            # Run enrichment pipeline
            enriched_jobs = []
            
            for job in jobs:
                try:
                    # Score job match
                    score_result = await self.enrichment_service.score_job_match(
                        job, resume_data
                    )
                    
                    # Add enrichment data
                    enriched_job = {
                        **job,
                        'match_score': score_result.get('score', 0),
                        'score_breakdown': score_result.get('breakdown', {}),
                        'fit_analysis': score_result.get('analysis', ''),
                        'recommended_action': self._get_recommendation(
                            score_result.get('score', 0)
                        )
                    }
                    
                    enriched_jobs.append(enriched_job)
                    
                except Exception as e:
                    logger.warning(f"Failed to enrich job {job.get('id', 'unknown')}: {e}")
                    # Include job without enrichment
                    enriched_jobs.append({**job, 'match_score': 0})
                    
            # Sort by match score
            enriched_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            logger.info(f"Enriched {len(enriched_jobs)} jobs with scoring")
            
            return enriched_jobs
            
        except Exception as e:
            logger.error(f"Job enrichment failed: {e}")
            # Return jobs without enrichment rather than fail completely
            return jobs
            
    async def _export_results(self, 
                            jobs: List[Dict[str, Any]], 
                            output_path: str) -> str:
        """Export jobs to Excel with enhanced formatting."""
        try:
            import pandas as pd
            from pathlib import Path
            
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for Excel
            excel_data = []
            
            for job in jobs:
                excel_row = {
                    'Title': job.get('title', ''),
                    'Company': job.get('company', ''),
                    'Location': job.get('location', ''),
                    'Source': job.get('source', ''),
                    'Match Score': job.get('match_score', 0),
                    'Recommended Action': job.get('recommended_action', ''),
                    'URL': job.get('url', ''),
                    'Date Posted': job.get('date_posted', ''),
                    'Applied': 'No',  # User will update this
                    'Status': 'New',  # User will update this
                    'Notes': '',      # User can add notes
                    'Fit Analysis': job.get('fit_analysis', '')[:500]  # Truncate for Excel
                }
                excel_data.append(excel_row)
                
            # Create DataFrame and export
            df = pd.DataFrame(excel_data)
            
            # Sort by match score (highest first)
            df = df.sort_values('Match Score', ascending=False)
            
            # Export to Excel with formatting
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Job Opportunities', index=False)
                
                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets['Job Opportunities']
                
                # Add formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Format header row
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    
                # Auto-adjust column widths
                for i, col in enumerate(df.columns):
                    max_len = max(
                        df[col].astype(str).str.len().max(),
                        len(str(col))
                    )
                    worksheet.set_column(i, i, min(max_len + 2, 50))
                    
            logger.info(f"Results exported to {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            # Fallback to JSON export
            json_path = output_path.replace('.xlsx', '.json')
            with open(json_path, 'w') as f:
                json.dump(jobs, f, indent=2, default=str)
            logger.info(f"Fallback: exported JSON to {json_path}")
            return json_path
            
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on match score."""
        if score >= 0.8:
            return "High Priority - Apply ASAP"
        elif score >= 0.6:
            return "Good Match - Review & Apply"
        elif score >= 0.4:
            return "Moderate Match - Consider"
        else:
            return "Low Match - Skip"
            
    async def run_quick_search(self, 
                             keywords: List[str], 
                             location: str = "Remote") -> str:
        """Run a quick job search without resume processing."""
        try:
            logger.info(f"Running quick search for: {keywords}")
            
            search_params = {
                'keywords': keywords,
                'location': location,
                'max_jobs_per_source': 25
            }
            
            jobs = await self.job_aggregator.run_daily_aggregation(search_params)
            
            # Export without scoring
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./output/quick_search_{timestamp}.xlsx"
            
            result_path = await self._export_results(jobs, output_path)
            
            logger.info(f"Quick search completed: {len(jobs)} jobs exported")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Quick search failed: {e}")
            raise


# Legacy CLI command runner for backward compatibility
class CLIRunner:
    """Handles CLI command execution"""
    
    def __init__(self):
        self.commands = {}
        
    async def run_command(self, command: str, args: Dict[str, Any]):
        """Execute a CLI command"""
        if command in self.commands:
            return await self.commands[command](**args)
        raise ValueError(f"Unknown command: {command}")
        
    def register_command(self, name: str, handler):
        """Register a new CLI command"""
        self.commands[name] = handler


def _validate_args(args) -> bool:
    """Validate CLI arguments."""
    if hasattr(args, 'resume_path') and args.resume_path:
        if not Path(args.resume_path).exists():
            logger.error(f"Resume file not found: {args.resume_path}")
            return False
            
    return True


def _export_results(jobs: List[Dict[str, Any]], 
                   output_format: str = 'excel', 
                   output_path: str = None) -> str:
    """Legacy export function for backward compatibility."""
    runner = AutomatedJobSearchRunner()
    return asyncio.run(runner._export_results(jobs, output_path or './output/results.xlsx'))
