"""Resume inventory models for multi-resume intelligence"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid

class ResumeType(Enum):
    """Resume types in the system"""
    MASTER = "master"
    CANDIDATE = "candidate"

class DomainClassification(Enum):
    """Professional domains for resume classification"""
    TECHNOLOGY = "technology"
    BUSINESS = "business" 
    CREATIVE = "creative"
    GENERIC = "generic"

@dataclass
class ResumeMetadata:
    """Metadata for a single resume file"""
    id: str
    file_path: Path
    filename: str
    resume_type: ResumeType
    domain: DomainClassification
    skills: List[str]
    experience_years: int
    last_modified: str
    file_size: int
    parsed_content: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass 
class ResumeInventory:
    """Complete inventory of user's resume portfolio"""
    master_resume: Optional[ResumeMetadata]
    candidate_resumes: List[ResumeMetadata]
    base_path: Path
    total_resumes: int = field(init=False)
    
    def __post_init__(self):
        self.total_resumes = len(self.candidate_resumes) + (1 if self.master_resume else 0)
    
    def get_candidates_by_domain(self, domain: DomainClassification) -> List[ResumeMetadata]:
        """Get candidate resumes filtered by domain"""
        return [r for r in self.candidate_resumes if r.domain == domain]
    
    def get_candidate_by_filename(self, filename: str) -> Optional[ResumeMetadata]:
        """Get candidate resume by filename"""
        for resume in self.candidate_resumes:
            if resume.filename == filename:
                return resume
        return None

@dataclass
class JobKeywords:
    """Extracted keywords from job description"""
    technical_skills: List[str]
    business_skills: List[str]
    industry_terms: List[str]
    experience_requirements: List[str]
    responsibilities: List[str]
    
@dataclass
class SelectionResult:
    """Result of resume selection for a job"""
    selected_resume: Optional[ResumeMetadata]
    match_score: float
    selection_rationale: str
    keyword_matches: int
    domain_match: bool
    confidence_level: float
    
@dataclass
class BulletPoint:
    """Enhanced bullet point with metadata"""
    text: str
    semantic_embedding: Optional[List[float]]
    relevance_score: float
    uniqueness_score: float
    impact_indicators: List[str]
    
@dataclass
class Enhancement:
    """Resume enhancement recommendation"""
    bullet_point: str
    relevance_score: float
    source_resume: str  # "master" or specific candidate resume
    category: str  # technical, leadership, impact, etc.
    reasoning: str
    
@dataclass
class JobIntelligenceResult:
    """Complete result of multi-resume job intelligence processing"""
    job_id: str
    selected_resume: Optional[ResumeMetadata]
    match_score: float
    selection_rationale: str
    enhancements: List[Enhancement]
    processing_time: float
    confidence_level: float
    
    def to_excel_row(self) -> Dict[str, Any]:
        """Convert to Excel row format matching EXACT specification"""
        return {
            # Column E: Selected Resume - filename only (e.g., "ai/ml_engineer.pdf")
            "Selected Resume": self.selected_resume.filename if self.selected_resume else "Not Available",
            # Column F: Match Score - enhanced percentage (e.g., "87.5%")  
            "Match Score": f"{self.match_score:.1f}%" if self.match_score else "0%",
            # Column G: Selection Rationale - why this resume (e.g., "Best ML keyword match")
            "Selection Rationale": self.selection_rationale or "Multi-resume processing completed",
            # Column H: Enhancement 1 - strategic bullet from master resume
            "Enhancement 1": self.enhancements[0].bullet_point if len(self.enhancements) > 0 else "None",
            # Column I: Enhancement 2 - strategic bullet from master resume  
            "Enhancement 2": self.enhancements[1].bullet_point if len(self.enhancements) > 1 else "None",
            # Column J: Enhancement 3 - strategic bullet from master resume
            "Enhancement 3": self.enhancements[2].bullet_point if len(self.enhancements) > 2 else "None",
        }