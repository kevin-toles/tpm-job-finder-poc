#!/usr/bin/env python3
"""
Demonstration script for TPM Job Finder automation.

Shows how to set up and run automated job searches using the CLI.
This script demonstrates the complete workflow the user requested.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tpm_job_finder_poc.cli.runner import AutomatedJobSearchRunner

async def demo_automation():
    """Demonstrate the automated job search workflow."""
    print("🚀 TPM Job Finder Automation Demo")
    print("=" * 50)
    
    # Configuration
    config_path = "./config/automation_config.json"
    sample_resume = "./sample_files/resume.pdf"  # User would provide their resume
    
    try:
        # Initialize the runner
        print("📋 Initializing automation runner...")
        runner = AutomatedJobSearchRunner(config_path)
        print("✅ Runner initialized successfully")
        
        # Option 1: Quick search (no resume needed)
        print("\n🔍 Running quick search demo...")
        keywords = ["senior product manager", "technical product manager"]
        
        try:
            quick_result = await runner.run_quick_search(
                keywords=keywords,
                location="Remote"
            )
            print(f"✅ Quick search completed: {quick_result}")
        except Exception as e:
            print(f"⚠️ Quick search failed (expected if no scrapers available): {e}")
        
        # Option 2: Full daily workflow (requires resume)
        if Path(sample_resume).exists():
            print("\n📄 Running full daily workflow with resume...")
            
            daily_result = await runner.run_daily_search_workflow(
                resume_path=sample_resume,
                output_path="./output/demo_daily_results.xlsx"
            )
            print(f"✅ Daily workflow completed: {daily_result}")
        else:
            print(f"\n📄 Skipping full workflow demo (resume not found: {sample_resume})")
            print("To test with your resume:")
            print(f"  python demo_automation.py --resume /path/to/your/resume.pdf")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0

def show_automation_setup():
    """Show how to set up automation."""
    print("\n📅 Automation Setup Instructions")
    print("=" * 40)
    
    print("\n1. For Cron Job (Linux/Mac):")
    print("   python -m tpm_job_finder_poc.cli.automated_cli setup-cron \\")
    print("     --resume /path/to/resume.pdf --time '09:00'")
    
    print("\n2. For GitHub Actions:")
    print("   python -m tpm_job_finder_poc.cli.automated_cli setup-github-actions \\")
    print("     --resume /path/to/resume.pdf")
    
    print("\n3. Manual Daily Run:")
    print("   python -m tpm_job_finder_poc.cli.automated_cli daily-search \\")
    print("     --resume /path/to/resume.pdf")
    
    print("\n4. Quick Search (no resume needed):")
    print("   python -m tpm_job_finder_poc.cli.automated_cli quick-search \\")
    print("     --keywords 'senior product manager' 'tpm'")

if __name__ == "__main__":
    # Create necessary directories
    Path("./output").mkdir(exist_ok=True)
    Path("./logs").mkdir(exist_ok=True)
    
    # Check if user provided resume path
    if len(sys.argv) > 1 and sys.argv[1] == "--resume":
        if len(sys.argv) > 2:
            sample_resume = sys.argv[2]
        else:
            print("Error: --resume requires a path argument")
            sys.exit(1)
    
    # Run demo
    try:
        result = asyncio.run(demo_automation())
        show_automation_setup()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        sys.exit(130)
