"""
Job Collection Service - Job enricher implementation.

Handles enrichment of job postings w            # TPM scoring
            if self.enable_tpm_scoring:
                job.tpm_keywords_found = self._count_tpm_keywords(job) additional metadata and classification.
"""

import logging
import re
from typing import Dict, List, Any

from ..shared.contracts.job_collection_service import (
    JobPosting,
    JobType
)

logger = logging.getLogger(__name__)


class JobEnricher:
    """
    Job enrichment service for adding metadata to job postings.
    
    Provides job classification, remote work detection, TPM scoring,
    and market analysis capabilities.
    """
    
    # Job type classification keywords
    JOB_TYPE_KEYWORDS = {
        JobType.ENTRY_LEVEL: [
            'junior', 'entry level', 'entry-level', 'associate', 'intern',
            'new grad', 'graduate', 'trainee', '0-2 years', 'fresh graduate'
        ],
        JobType.MID_LEVEL: [
            'mid level', 'mid-level', 'intermediate', '2-5 years', '3-7 years',
            'experienced', 'professional', 'specialist', 'engineer ii', 'engineer 2'
        ],
        JobType.SENIOR: [
            'senior', 'sr', 'lead', 'principal', 'staff', 'architect',
            '5+ years', '7+ years', 'expert', 'advanced', 'lead engineer'
        ],
        JobType.MANAGEMENT: [
            'manager', 'director', 'vp', 'vice president', 'head of',
            'team lead', 'engineering manager', 'project manager', 'program manager',
            'technical lead', 'team leader', 'supervisor', 'chief'
        ]
    }
    
    # Remote work indicators
    REMOTE_KEYWORDS = [
        'remote', 'work from home', 'wfh', 'distributed', 'anywhere',
        'location independent', 'remote-first', 'remote friendly',
        'fully remote', '100% remote', 'virtual', 'telecommute'
    ]
    
    # TPM (Technical Project Manager) keywords
    TPM_KEYWORDS = [
        'technical project manager', 'tpm', 'technical program manager',
        'engineering program manager', 'technical delivery manager',
        'project management', 'program management', 'agile', 'scrum',
        'technical leadership', 'cross-functional', 'stakeholder management',
        'roadmap', 'milestone', 'delivery', 'execution', 'coordination'
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize job enricher.
        
        Args:
            config: Enrichment configuration
        """
        self.config = config or {}
        self.enable_job_classification = self.config.get('enable_job_classification', True)
        self.enable_remote_detection = self.config.get('enable_remote_detection', True)
        self.enable_tpm_scoring = self.config.get('enable_tpm_scoring', True)
        self.enable_skill_extraction = self.config.get('enable_skill_extraction', False)
    
    async def enrich_job(self, job: JobPosting) -> JobPosting:
        """
        Enrich a single job posting with additional metadata.
        
        Args:
            job: Job posting to enrich
            
        Returns:
            Enriched job posting
        """
        try:
            # Job type classification
            if self.enable_job_classification:
                job.job_type = self._classify_job_type(job)
            
            # Remote work detection
            if self.enable_remote_detection:
                job.remote_friendly = self._detect_remote_work(job)
            
            # TPM scoring
            if self.enable_tpm_scoring:
                job.tpm_keywords_found = self._count_tpm_keywords(job)
            
            # Skill extraction (if enabled)
            if self.enable_skill_extraction:
                job.skills = self._extract_skills(job)
            
            logger.debug(f"Enriched job {job.id}: type={job.job_type}, remote={job.remote_friendly}")
            
        except Exception as e:
            logger.error(f"Error enriching job {job.id}: {e}")
            # Set default values on error
            job.job_type = JobType.MID_LEVEL
            job.remote_friendly = False
            job.tpm_keywords_found = 0
        
        return job
    
    def _classify_job_type(self, job: JobPosting) -> JobType:
        """
        Classify job type based on title and description.
        
        Args:
            job: Job posting to classify
            
        Returns:
            Classified job type
        """
        text = f"{job.title} {getattr(job, 'description', '')}".lower()
        
        # Check for each job type in order of specificity
        for job_type, keywords in self.JOB_TYPE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return job_type
        
        # Default to mid-level if no specific indicators
        return JobType.MID_LEVEL
    
    def _detect_remote_work(self, job: JobPosting) -> bool:
        """
        Detect if job is remote-friendly.
        
        Args:
            job: Job posting to analyze
            
        Returns:
            True if job appears to be remote-friendly
        """
        text = f"{job.title} {getattr(job, 'description', '')} {job.location}".lower()
        
        return any(keyword in text for keyword in self.REMOTE_KEYWORDS)
    
    def _count_tpm_keywords(self, job: JobPosting) -> int:
        """
        Count TPM-related keywords in job posting.
        
        Args:
            job: Job posting
            
        Returns:
            Number of TPM keywords found
        """
        text = f"{job.title} {getattr(job, 'description', '')}".lower()
        
        return sum(1 for keyword in self.TPM_KEYWORDS if keyword in text)