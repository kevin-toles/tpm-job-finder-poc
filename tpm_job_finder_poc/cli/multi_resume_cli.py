"""Enhanced CLI for multi-resume intelligence workflows"""

import asyncio
import argparse
import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..enrichment.multi_resume_orchestrator import MultiResumeIntelligenceOrchestrator
from ..config.multi_resume_config import get_config, update_config
from ..models.job import Job
from ..excel_exporter import SpecCompliantExcelExporter
from .runner import AutomatedJobSearchRunner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/multi_resume_cli.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MultiResumeJobFinderCLI:
    """Enhanced CLI for multi-resume intelligence workflows"""
    
    def __init__(self):
        self.config = get_config()
        self.orchestrator = None
        self.job_runner = AutomatedJobSearchRunner()
        self.excel_exporter = SpecCompliantExcelExporter()
    
    async def run_multi_resume_search(self, 
                                    resume_folder: str,
                                    keywords: List[str],
                                    location: str = "Remote",
                                    output_path: Optional[str] = None) -> str:
        """
        Run job search with multi-resume intelligence
        
        Args:
            resume_folder: Path to folder containing resume variants and master resume
            keywords: Job search keywords
            location: Job location filter
            output_path: Output Excel file path
            
        Returns:
            Path to generated Excel file
        """
        logger.info(f"Starting multi-resume job search")
        logger.info(f"Resume folder: {resume_folder}")
        logger.info(f"Keywords: {keywords}")
        logger.info(f"Location: {location}")
        
        resume_base_path = Path(resume_folder)
        if not resume_base_path.exists():
            raise ValueError(f"Resume folder does not exist: {resume_folder}")
        
        # Update config with resume folder path
        update_config(resume_folder_path=resume_base_path)
        
        # Initialize orchestrator with LLM provider
        llm_provider = await self._get_llm_provider()
        self.orchestrator = MultiResumeIntelligenceOrchestrator(llm_provider=llm_provider)
        
        try:
            # Step 1: Run standard job search
            logger.info("Step 1: Running job search...")
            jobs_data = await self._run_job_search(keywords, location)
            logger.info(f"Found {len(jobs_data)} jobs")
            
            # Step 2: Convert to Job objects
            job_objects = [self._dict_to_job(job_data) for job_data in jobs_data]
            
            # Step 3: Process with multi-resume intelligence
            logger.info("Step 2: Processing with multi-resume intelligence...")
            intelligence_results = []
            
            for i, job in enumerate(job_objects):
                logger.info(f"Processing job {i+1}/{len(job_objects)}: {job.title}")
                result = self.orchestrator.process_job_with_multi_resume_intelligence(
                    job, resume_base_path
                )
                intelligence_results.append(result)
            
            # Step 4: Export enhanced results to Excel
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"output/multi_resume_results_{timestamp}.xlsx"
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info("Step 3: Exporting enhanced Excel results...")
            self.excel_exporter.export_with_multi_resume_intelligence(
                jobs_data, intelligence_results, str(output_file)
            )
            
            logger.info(f"Multi-resume job search completed: {output_file}")
            
            # Print summary
            self._print_summary(intelligence_results)
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Multi-resume search failed: {e}")
            raise
    
    async def setup_resume_portfolio(self, resume_folder: str) -> None:
        """
        Setup and validate resume portfolio structure
        
        Args:
            resume_folder: Path to resume folder to setup
        """
        logger.info(f"Setting up resume portfolio: {resume_folder}")
        
        resume_path = Path(resume_folder)
        resume_path.mkdir(parents=True, exist_ok=True)
        
        # Create example folder structure
        example_structure = {
            "master": "Master resume folder (comprehensive resume - never selected)",
            "AI": "AI/ML/Data Science focused resumes", 
            "Backend": "Backend development resumes",
            "Sales": "Sales and business development resumes",
            "Finance": "Finance and consulting resumes"
        }
        
        print("\\n📁 Setting up resume portfolio structure:")
        print(f"Base folder: {resume_path.absolute()}")
        print("\\nRecommended folder structure:")
        
        for folder, description in example_structure.items():
            folder_path = resume_path / folder
            folder_path.mkdir(exist_ok=True)
            print(f"  {folder}/  - {description}")
            
            # Create example placeholder file
            placeholder = folder_path / "README.md"
            if not placeholder.exists():
                placeholder.write_text(f"# {folder} Resume Folder\\n\\n{description}\\n\\nPlace your {folder.lower()} resumes here.")
        
        print(f"\\n✅ Resume portfolio structure created at: {resume_path.absolute()}")
        print("\\n📋 Next steps:")
        print("1. Place your comprehensive master resume in the 'master/' folder")
        print("2. Place specialized resume variants in appropriate domain folders")
        print("3. Ensure all resume files have unique names")
        print("4. Run: python -m tpm_job_finder_poc.cli.multi_resume_cli search --resume-folder [path]")
    
    def configure_system(self, **kwargs) -> None:
        """
        Configure multi-resume system settings
        
        Args:
            **kwargs: Configuration parameters to update
        """
        logger.info("Configuring multi-resume system")
        
        # Update configuration
        update_config(**kwargs)
        
        # Save configuration
        config = get_config()
        config_path = Path("config/multi_resume_config.json")
        config.save_to_file(config_path)
        
        print(f"✅ Configuration saved to: {config_path.absolute()}")
        print("\\nCurrent settings:")
        print(f"  Semantic similarity threshold: {config.semantic_similarity_threshold}")
        print(f"  Keyword match threshold: {config.keyword_match_threshold}")
        print(f"  Max enhancements: {config.max_enhancements}")
        print(f"  Supported formats: {config.supported_resume_formats}")
    
    async def _run_job_search(self, keywords: List[str], location: str) -> List[Dict[str, Any]]:
        """Run standard job search using existing job runner"""
        # Use existing job search infrastructure
        result_file = await self.job_runner.run_quick_search(keywords, location)
        
        # Parse results from Excel file (simplified for this implementation)
        # In practice, you'd integrate with the actual job aggregation service
        return [
            {
                "id": f"job_{i}",
                "Job Title": f"Sample Job {i+1}",
                "Company": f"Company {i+1}",
                "Location": location,
                "Salary": "$100k-150k",
                "Job Description": f"Sample job description {i+1} with keywords: {' '.join(keywords)}"
            }
            for i in range(5)  # Return sample jobs for demonstration
        ]
    
    def _dict_to_job(self, job_data: Dict[str, Any]) -> Job:
        """Convert job dictionary to Job object"""
        return Job(
            id=job_data.get("id", ""),
            title=job_data.get("Job Title", ""),
            company=job_data.get("Company", ""),
            location=job_data.get("Location", ""),
            description=job_data.get("Job Description", ""),
            salary=job_data.get("Salary", "")
        )
    
    async def _get_llm_provider(self):
        """Get LLM provider for intelligence processing"""
        try:
            # Import and initialize LLM provider
            from ..llm_provider.llm_adapter import LLMAdapter
            return LLMAdapter()
        except Exception as e:
            logger.warning(f"Failed to initialize LLM provider: {e}")
            return None
    
    def _print_summary(self, results: List) -> None:
        """Print summary of multi-resume processing results"""
        print("\\n" + "="*60)
        print("📊 MULTI-RESUME INTELLIGENCE SUMMARY")
        print("="*60)
        
        total_jobs = len(results)
        successful_selections = sum(1 for r in results if r.selected_resume)
        avg_score = sum(r.match_score for r in results) / max(1, total_jobs)
        avg_enhancements = sum(len(r.enhancements) for r in results) / max(1, total_jobs)
        
        print(f"📈 Total jobs processed: {total_jobs}")
        print(f"✅ Successful selections: {successful_selections}")
        print(f"📊 Average match score: {avg_score:.1f}%")
        print(f"🎯 Average enhancements per job: {avg_enhancements:.1f}")
        
        # Show top selections
        print("\\n🏆 Top Matches:")
        sorted_results = sorted(results, key=lambda r: r.match_score, reverse=True)
        for i, result in enumerate(sorted_results[:3]):
            if result.selected_resume:
                print(f"  {i+1}. {result.selected_resume.filename} - {result.match_score:.1f}%")
        
        print("\\n" + "="*60)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Multi-Resume Intelligence Job Finder")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Run multi-resume job search')
    search_parser.add_argument('--resume-folder', type=str, required=True, 
                              help='Path to folder containing resume variants and master resume')
    search_parser.add_argument('--keywords', type=str, nargs='+', required=True,
                              help='Job search keywords')
    search_parser.add_argument('--location', type=str, default='Remote',
                              help='Job location filter (default: Remote)')
    search_parser.add_argument('--output', type=str,
                              help='Output Excel file path')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup resume portfolio structure')
    setup_parser.add_argument('--resume-folder', type=str, required=True,
                             help='Path to create resume portfolio structure')
    
    # Configure command
    config_parser = subparsers.add_parser('configure', help='Configure system settings')
    config_parser.add_argument('--similarity-threshold', type=float,
                              help='Semantic similarity threshold (0-1)')
    config_parser.add_argument('--keyword-threshold', type=float,
                              help='Keyword match threshold (0-1)')
    config_parser.add_argument('--max-enhancements', type=int,
                              help='Maximum number of enhancements to generate')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = MultiResumeJobFinderCLI()
    
    try:
        if args.command == 'search':
            asyncio.run(cli.run_multi_resume_search(
                resume_folder=args.resume_folder,
                keywords=args.keywords,
                location=args.location,
                output_path=args.output
            ))
        elif args.command == 'setup':
            asyncio.run(cli.setup_resume_portfolio(args.resume_folder))
        elif args.command == 'configure':
            config_kwargs = {}
            if args.similarity_threshold:
                config_kwargs['semantic_similarity_threshold'] = args.similarity_threshold
            if args.keyword_threshold:
                config_kwargs['keyword_match_threshold'] = args.keyword_threshold
            if args.max_enhancements:
                config_kwargs['max_enhancements'] = args.max_enhancements
            
            cli.configure_system(**config_kwargs)
    
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()