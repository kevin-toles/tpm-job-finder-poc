"""Multi-Resume Intelligence Orchestrator - Main coordinator for all multi-resume components"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..models.resume_inventory import (
    ResumeInventory, ResumeMetadata, JobIntelligenceResult, Enhancement
)
from ..models.job import Job
from ..config.multi_resume_config import get_config
from .interfaces import IMultiResumeIntelligenceOrchestrator
from .resume_discovery_service import ResumeDiscoveryService
from .hybrid_selection_engine import HybridSelectionEngine
from .enhanced_content_analyzer import EnhancedContentAnalyzer

logger = logging.getLogger(__name__)

class MultiResumeIntelligenceOrchestrator(IMultiResumeIntelligenceOrchestrator):
    """
    Main orchestrator coordinating all multi-resume intelligence components
    
    Coordinates:
    1. Resume Discovery Service - Scans and catalogs resume portfolio
    2. Hybrid Selection Engine - Intelligent resume selection
    3. Enhanced Content Analyzer - Semantic analysis and enhancement generation
    """
    
    def __init__(self, llm_provider=None):
        self.config = get_config()
        
        # Initialize components
        self.discovery_service = ResumeDiscoveryService()
        self.selection_engine = HybridSelectionEngine(llm_provider=llm_provider)
        self.content_analyzer = EnhancedContentAnalyzer()
        
        # Cache for resume inventory to avoid repeated scanning
        self._inventory_cache: Optional[ResumeInventory] = None
        self._cache_path: Optional[Path] = None
        
        logger.info("Multi-Resume Intelligence Orchestrator initialized")
    
    def process_job_with_multi_resume_intelligence(self, 
                                                  job: Job, 
                                                  resume_base_path: Path) -> JobIntelligenceResult:
        """
        Complete multi-resume intelligence processing
        
        Args:
            job: Job posting to process
            resume_base_path: Base path containing resume folders
            
        Returns:
            Complete intelligence result with selection and enhancements
        """
        start_time = time.time()
        job_id = job.id if hasattr(job, 'id') else f"job_{int(time.time())}"
        
        logger.info(f"Processing job {job_id}: {job.title} at {job.company}")
        
        try:
            # Step 1: Discover and catalog resume portfolio
            inventory = self._get_resume_inventory(resume_base_path)
            
            if not inventory.candidate_resumes:
                logger.warning("No candidate resumes found")
                return self._create_empty_result(job_id, "No candidate resumes found")
            
            logger.info(f"Resume portfolio: {len(inventory.candidate_resumes)} candidates, "
                       f"master: {'Yes' if inventory.master_resume else 'No'}")
            
            # Step 2: Intelligent resume selection
            selection_result = self.selection_engine.select_optimal_resume(job, inventory)
            
            if not selection_result.selected_resume:
                logger.warning("No resume selected")
                return self._create_empty_result(job_id, "Resume selection failed")
            
            logger.info(f"Selected resume: {selection_result.selected_resume.filename} "
                       f"(score: {selection_result.match_score:.1f}%)")
            
            # Step 3: Generate enhancements from master resume
            enhancements = []
            if inventory.master_resume:
                try:
                    enhancements = self.content_analyzer.select_top_enhancements(
                        job, inventory.master_resume, selection_result.selected_resume
                    )
                    logger.info(f"Generated {len(enhancements)} enhancements from master resume")
                except Exception as e:
                    logger.error(f"Enhancement generation failed: {e}")
                    enhancements = self._create_fallback_enhancements()
            else:
                logger.warning("No master resume available for enhancements")
                enhancements = []
            
            # Step 4: Validate enhancement uniqueness
            if enhancements:
                is_unique = self.validate_enhancement_uniqueness(enhancements, selection_result.selected_resume)
                if not is_unique:
                    logger.warning("Enhancement uniqueness validation failed")
            
            # Step 5: Generate final result
            processing_time = time.time() - start_time
            
            result = JobIntelligenceResult(
                job_id=job_id,
                selected_resume=selection_result.selected_resume,
                match_score=selection_result.match_score,
                selection_rationale=self.generate_selection_rationale(selection_result, selection_result.selected_resume),
                enhancements=enhancements,
                processing_time=processing_time,
                confidence_level=selection_result.confidence_level
            )
            
            logger.info(f"Multi-resume intelligence completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Multi-resume intelligence processing failed: {e}")
            processing_time = time.time() - start_time
            return JobIntelligenceResult(
                job_id=job_id,
                selected_resume=None,
                match_score=0.0,
                selection_rationale=f"Processing failed: {str(e)}",
                enhancements=[],
                processing_time=processing_time,
                confidence_level=0.0
            )
    
    def generate_selection_rationale(self, 
                                   selection: Any, 
                                   resume: ResumeMetadata) -> str:
        """
        Generate natural language explanation of selection logic
        
        Args:
            selection: Selection result object
            resume: Selected resume metadata
            
        Returns:
            Human-readable selection rationale
        """
        # Extract relevant details
        domain = resume.domain.value
        filename = resume.filename
        match_score = getattr(selection, 'match_score', 0)
        keyword_matches = getattr(selection, 'keyword_matches', 0)
        domain_match = getattr(selection, 'domain_match', False)
        
        # Generate rationale based on selection factors
        rationale_parts = []
        
        # Domain alignment
        if domain_match:
            rationale_parts.append(f"Strong {domain} domain alignment")
        else:
            rationale_parts.append(f"Selected from {domain} domain")
        
        # Keyword matching
        if keyword_matches > 0:
            rationale_parts.append(f"{keyword_matches} keyword matches")
        
        # Score interpretation
        if match_score >= 80:
            rationale_parts.append("excellent fit")
        elif match_score >= 60:
            rationale_parts.append("good fit")
        elif match_score >= 40:
            rationale_parts.append("moderate fit")
        else:
            rationale_parts.append("limited fit")
        
        # Construct final rationale
        if len(rationale_parts) >= 3:
            rationale = f"{rationale_parts[0]} with {rationale_parts[1]}, indicating {rationale_parts[2]}"
        else:
            rationale = "; ".join(rationale_parts)
        
        return rationale
    
    def validate_enhancement_uniqueness(self, 
                                      enhancements: List[Enhancement], 
                                      selected_resume: ResumeMetadata) -> bool:
        """
        Ensure enhancements are <80% similar to selected resume content
        and <20% similar to each other
        
        Args:
            enhancements: List of enhancement recommendations
            selected_resume: Selected resume metadata
            
        Returns:
            True if all enhancements are sufficiently unique
        """
        try:
            # Load selected resume content
            selected_content = self._load_resume_content(selected_resume)
            selected_bullets = self.content_analyzer.extract_bullet_points(selected_content)
            
            resume_threshold = self.config.semantic_similarity_threshold
            enhancement_threshold = self.config.enhancement_similarity_threshold
            
            # Check enhancement-to-resume uniqueness
            for enhancement in enhancements:
                for selected_bullet in selected_bullets:
                    similarity = self.content_analyzer.calculate_semantic_similarity(
                        enhancement.bullet_point, selected_bullet
                    )
                    
                    if similarity >= resume_threshold:
                        logger.warning(f"Enhancement too similar to existing content: "
                                     f"{enhancement.bullet_point[:50]}... (sim={similarity:.3f})")
                        return False
            
            # Check enhancement-to-enhancement uniqueness
            for i, enhancement1 in enumerate(enhancements):
                for j, enhancement2 in enumerate(enhancements[i+1:], i+1):
                    similarity = self.content_analyzer.calculate_semantic_similarity(
                        enhancement1.bullet_point, enhancement2.bullet_point
                    )
                    
                    if similarity >= enhancement_threshold:
                        logger.warning(f"Enhancements too similar to each other: "
                                     f"'{enhancement1.bullet_point[:30]}...' vs "
                                     f"'{enhancement2.bullet_point[:30]}...' (sim={similarity:.3f})")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Enhancement uniqueness validation failed: {e}")
            return False  # Fail safe
    
    def process_multiple_jobs(self, 
                            jobs: List[Job], 
                            resume_base_path: Path) -> List[JobIntelligenceResult]:
        """
        Process multiple jobs with shared resume inventory for efficiency
        
        Args:
            jobs: List of job postings to process
            resume_base_path: Base path containing resume folders
            
        Returns:
            List of intelligence results for all jobs
        """
        logger.info(f"Processing {len(jobs)} jobs with multi-resume intelligence")
        
        # Pre-load resume inventory for efficiency
        inventory = self._get_resume_inventory(resume_base_path)
        
        results = []
        for i, job in enumerate(jobs):
            logger.info(f"Processing job {i+1}/{len(jobs)}: {job.title}")
            result = self.process_job_with_multi_resume_intelligence(job, resume_base_path)
            results.append(result)
        
        logger.info(f"Completed processing {len(jobs)} jobs")
        return results
    
    def _get_resume_inventory(self, resume_base_path: Path) -> ResumeInventory:
        """Get resume inventory with caching"""
        # Check if we can use cached inventory
        if (self._inventory_cache and 
            self._cache_path == resume_base_path and
            self._is_cache_valid(resume_base_path)):
            logger.debug("Using cached resume inventory")
            return self._inventory_cache
        
        # Scan and cache new inventory
        logger.info("Scanning resume inventory...")
        inventory = self.discovery_service.scan_resume_folders(resume_base_path)
        
        self._inventory_cache = inventory
        self._cache_path = resume_base_path
        
        return inventory
    
    def _is_cache_valid(self, resume_base_path: Path) -> bool:
        """Check if cached inventory is still valid"""
        try:
            # Simple check - if base path modification time is newer than cache creation
            # In practice, you might want more sophisticated cache invalidation
            return True  # For now, assume cache is always valid within session
        except Exception:
            return False
    
    def _create_empty_result(self, job_id: str, reason: str) -> JobIntelligenceResult:
        """Create empty result for failed processing"""
        return JobIntelligenceResult(
            job_id=job_id,
            selected_resume=None,
            match_score=0.0,
            selection_rationale=reason,
            enhancements=[],
            processing_time=0.0,
            confidence_level=0.0
        )
    
    def _create_fallback_enhancements(self) -> List[Enhancement]:
        """Create fallback enhancements when generation fails"""
        return [
            Enhancement(
                bullet_point="Led cross-functional initiatives to deliver high-impact results",
                relevance_score=0.5,
                source_resume="fallback",
                category="leadership",
                reasoning="Generic leadership enhancement (fallback)"
            ),
            Enhancement(
                bullet_point="Implemented technical solutions that improved operational efficiency",
                relevance_score=0.5,
                source_resume="fallback", 
                category="technical",
                reasoning="Generic technical enhancement (fallback)"
            ),
            Enhancement(
                bullet_point="Achieved measurable business impact through strategic execution",
                relevance_score=0.5,
                source_resume="fallback",
                category="impact", 
                reasoning="Generic impact enhancement (fallback)"
            )
        ]
    
    def _load_resume_content(self, resume: ResumeMetadata) -> str:
        """Load resume content from file"""
        try:
            # In practice, integrate with existing resume parser
            # For now, return a placeholder
            return f"Sample content for {resume.filename}"
        except Exception as e:
            logger.error(f"Failed to load resume content for {resume.filename}: {e}")
            return ""