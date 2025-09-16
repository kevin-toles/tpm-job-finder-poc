"""Multi-Resume Intelligence Package

This package provides advanced resume portfolio management and intelligent selection
capabilities for the TPM Job Finder POC.

Key Components:
- ResumeDiscoveryService: Scans and catalogs resume portfolios
- HybridSelectionEngine: Two-stage intelligent resume selection
- EnhancedContentAnalyzer: Semantic similarity and enhancement generation
- MultiResumeIntelligenceOrchestrator: Main coordination layer

Usage:
    from tpm_job_finder_poc.enrichment.multi_resume_orchestrator import MultiResumeIntelligenceOrchestrator
    from tpm_job_finder_poc.models.job import Job
    from pathlib import Path
    
    orchestrator = MultiResumeIntelligenceOrchestrator()
    job = Job(title="ML Engineer", company="Google", description="...")
    result = orchestrator.process_job_with_multi_resume_intelligence(job, Path("~/resumes"))
"""

__version__ = "1.0.0"
__author__ = "TPM Job Finder Team"

# Export main classes for easy importing
try:
    from .multi_resume_orchestrator import MultiResumeIntelligenceOrchestrator
    from .resume_discovery_service import ResumeDiscoveryService  
    from .hybrid_selection_engine import HybridSelectionEngine
    from .enhanced_content_analyzer import EnhancedContentAnalyzer

    __all__ = [
        "MultiResumeIntelligenceOrchestrator",
        "ResumeDiscoveryService", 
        "HybridSelectionEngine",
        "EnhancedContentAnalyzer"
    ]
except ImportError:
    # Graceful degradation if dependencies not available
    __all__ = []
