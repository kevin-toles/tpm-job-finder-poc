"""Interfaces for multi-resume intelligence components"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pathlib import Path

from ..models.resume_inventory import (
    ResumeInventory, ResumeMetadata, JobKeywords, 
    SelectionResult, Enhancement, JobIntelligenceResult
)
from ..models.job import Job

class IResumeDiscoveryService(ABC):
    """Interface for discovering and cataloging resumes"""
    
    @abstractmethod
    def scan_resume_folders(self, base_path: Path) -> ResumeInventory:
        """Scan folders and build complete resume inventory"""
        pass
    
    @abstractmethod
    def identify_master_folder(self, folders: List[Path]) -> Optional[Path]:
        """Identify the master resume folder"""
        pass
    
    @abstractmethod
    def classify_resume_domain(self, resume_meta: ResumeMetadata) -> str:
        """Classify resume into professional domain"""
        pass
    
    @abstractmethod
    def build_candidate_pool(self, inventory: ResumeInventory) -> List[ResumeMetadata]:
        """Build candidate pool excluding master resume"""
        pass

class IHybridSelectionEngine(ABC):
    """Interface for intelligent resume selection"""
    
    @abstractmethod
    def analyze_job_keywords(self, job: Job) -> JobKeywords:
        """Extract and categorize keywords from job description"""
        pass
    
    @abstractmethod
    def filter_candidate_resumes(self, 
                                keywords: JobKeywords, 
                                inventory: ResumeInventory) -> List[ResumeMetadata]:
        """Stage 1: Keyword-based pre-filtering"""
        pass
    
    @abstractmethod
    def batch_score_candidates(self, 
                              job: Job,
                              candidates: List[ResumeMetadata]) -> List[SelectionResult]:
        """Stage 2: Batch LLM scoring if multiple candidates"""
        pass
    
    @abstractmethod
    def select_optimal_resume(self, 
                             job: Job,
                             inventory: ResumeInventory) -> SelectionResult:
        """Complete selection process with rationale"""
        pass

class IEnhancedContentAnalyzer(ABC):
    """Interface for content analysis and enhancement generation"""
    
    @abstractmethod
    def extract_bullet_points(self, resume_content: str) -> List[str]:
        """Extract bullet points from resume content"""
        pass
    
    @abstractmethod
    def calculate_semantic_similarity(self, 
                                    bullet1: str, 
                                    bullet2: str) -> float:
        """Calculate semantic similarity between bullet points"""
        pass
    
    @abstractmethod
    def identify_unique_content(self, 
                               master_bullets: List[str],
                               selected_bullets: List[str]) -> List[str]:
        """Find bullet points in master that are NOT in selected resume"""
        pass
    
    @abstractmethod
    def score_relevance_to_job(self, 
                              bullets: List[str],
                              job: Job) -> List[float]:
        """Score bullet point relevance to job requirements"""
        pass
    
    @abstractmethod
    def select_top_enhancements(self, 
                               job: Job,
                               master_resume: ResumeMetadata,
                               selected_resume: ResumeMetadata) -> List[Enhancement]:
        """Generate 3 strategic enhancements from master resume"""
        pass

class IMultiResumeIntelligenceOrchestrator(ABC):
    """Main orchestrator interface"""
    
    @abstractmethod
    def process_job_with_multi_resume_intelligence(self, 
                                                  job: Job, 
                                                  resume_base_path: Path) -> JobIntelligenceResult:
        """Complete multi-resume intelligence processing"""
        pass
    
    @abstractmethod
    def generate_selection_rationale(self, 
                                   selection: SelectionResult, 
                                   resume: ResumeMetadata) -> str:
        """Generate natural language explanation of selection logic"""
        pass
    
    @abstractmethod
    def validate_enhancement_uniqueness(self, 
                                      enhancements: List[Enhancement], 
                                      selected_resume: ResumeMetadata) -> bool:
        """Ensure enhancements are <80% similar to selected resume content"""
        pass