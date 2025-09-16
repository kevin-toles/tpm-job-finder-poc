"""Resume Discovery Service - Intelligent resume discovery and categorization"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from ..models.resume_inventory import (
    ResumeInventory, ResumeMetadata, ResumeType, DomainClassification
)
from ..config.multi_resume_config import get_config
from .interfaces import IResumeDiscoveryService

logger = logging.getLogger(__name__)

class ResumeDiscoveryService(IResumeDiscoveryService):
    """
    Intelligent resume discovery and categorization
    
    Recursively scans folders to discover resume variants
    Identifies master folder and classifies domains
    """
    
    def __init__(self):
        self.config = get_config()
        self._domain_keywords = self.config.domain_keywords
        
    def scan_resume_folders(self, base_path: Path) -> ResumeInventory:
        """
        Scan folders and build complete resume inventory
        
        Args:
            base_path: Base directory containing resume folders
            
        Returns:
            Complete resume inventory with master and candidates
        """
        logger.info(f"Scanning resume folders in: {base_path}")
        
        if not base_path.exists():
            raise FileNotFoundError(f"Resume base path does not exist: {base_path}")
        
        # Discover all resume files recursively
        all_resumes = self._discover_all_resumes(base_path)
        logger.info(f"Found {len(all_resumes)} resume files")
        
        # Identify master resume
        master_resume = self._identify_master_resume(all_resumes)
        
        # Build candidate pool (excluding master)
        candidate_resumes = [r for r in all_resumes if r != master_resume]
        
        # Classify domains for candidates
        for resume in candidate_resumes:
            resume.domain = self._classify_domain(resume)
        
        inventory = ResumeInventory(
            master_resume=master_resume,
            candidate_resumes=candidate_resumes,
            base_path=base_path
        )
        
        logger.info(f"Built inventory: {inventory.total_resumes} total resumes, "
                   f"1 master, {len(candidate_resumes)} candidates")
        
        return inventory
    
    def identify_master_folder(self, folders: List[Path]) -> Optional[Path]:
        """
        Identify the master resume folder
        
        Args:
            folders: List of folder paths to check
            
        Returns:
            Path to master folder if found
        """
        master_pattern = self.config.get_master_folder_pattern()
        
        for folder in folders:
            if re.search(master_pattern, folder.name.lower()):
                return folder
                
        return None
    
    def classify_resume_domain(self, resume_meta: ResumeMetadata) -> DomainClassification:
        """
        Classify resume into professional domain
        
        Args:
            resume_meta: Resume metadata to classify
            
        Returns:
            Domain classification
        """
        return self._classify_domain(resume_meta)
    
    def build_candidate_pool(self, inventory: ResumeInventory) -> List[ResumeMetadata]:
        """
        Build candidate pool excluding master resume
        
        Args:
            inventory: Complete resume inventory
            
        Returns:
            List of candidate resumes only
        """
        return inventory.candidate_resumes
    
    def _discover_all_resumes(self, base_path: Path) -> List[ResumeMetadata]:
        """Recursively discover all resume files"""
        resumes = []
        
        for file_path in base_path.rglob("*"):
            if self._is_resume_file(file_path):
                try:
                    resume_meta = self._create_resume_metadata(file_path, base_path)
                    resumes.append(resume_meta)
                except Exception as e:
                    logger.warning(f"Failed to process resume {file_path}: {e}")
                    
        return resumes
    
    def _is_resume_file(self, file_path: Path) -> bool:
        """Check if file is a valid resume"""
        if not file_path.is_file():
            return False
            
        if not self.config.is_supported_format(file_path):
            return False
            
        if not self.config.validate_file_size(file_path):
            logger.warning(f"Resume file too large: {file_path}")
            return False
            
        return True
    
    def _create_resume_metadata(self, file_path: Path, base_path: Path) -> ResumeMetadata:
        """Create resume metadata from file"""
        # Determine if this is in master folder
        relative_path = file_path.relative_to(base_path)
        is_master = any(
            part.lower() in self.config.master_folder_names 
            for part in relative_path.parts[:-1]  # Exclude filename
        )
        
        resume_type = ResumeType.MASTER if is_master else ResumeType.CANDIDATE
        
        # Extract basic file metadata
        stat = file_path.stat()
        
        # Parse resume content for skills and experience
        skills, experience_years = self._parse_resume_content(file_path)
        
        return ResumeMetadata(
            id="",  # Will be auto-generated
            file_path=file_path,
            filename=file_path.name,
            resume_type=resume_type,
            domain=DomainClassification.GENERIC,  # Will be classified later
            skills=skills,
            experience_years=experience_years,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            file_size=stat.st_size
        )
    
    def _identify_master_resume(self, resumes: List[ResumeMetadata]) -> Optional[ResumeMetadata]:
        """Identify the master resume from all resumes"""
        masters = [r for r in resumes if r.resume_type == ResumeType.MASTER]
        
        if not masters:
            logger.warning("No master resume found")
            return None
            
        if len(masters) == 1:
            return masters[0]
            
        # Multiple masters found, pick the most comprehensive one
        logger.warning(f"Multiple master resumes found: {len(masters)}")
        return max(masters, key=lambda r: r.file_size)  # Largest file as proxy for most comprehensive
    
    def _classify_domain(self, resume: ResumeMetadata) -> DomainClassification:
        """Classify resume domain based on skills and folder structure"""
        # Check folder path for domain hints
        folder_name = resume.file_path.parent.name.lower()
        
        # Score against domain keywords
        domain_scores = {}
        
        for domain, keywords in self._domain_keywords.items():
            score = 0
            
            # Score based on folder name
            for keyword in keywords:
                if keyword.lower() in folder_name:
                    score += 2  # Folder match gets higher weight
                    
            # Score based on extracted skills
            for skill in resume.skills:
                if skill.lower() in [k.lower() for k in keywords]:
                    score += 1
                    
            domain_scores[domain] = score
        
        # Find highest scoring domain
        if not domain_scores or max(domain_scores.values()) == 0:
            return DomainClassification.GENERIC
            
        best_domain = max(domain_scores, key=domain_scores.get)
        confidence = domain_scores[best_domain] / sum(domain_scores.values())
        
        if confidence >= self.config.domain_classification_confidence:
            return DomainClassification(best_domain)
        else:
            return DomainClassification.GENERIC
    
    def _parse_resume_content(self, file_path: Path) -> tuple[List[str], int]:
        """
        Parse resume content to extract skills and experience
        
        Returns:
            Tuple of (skills, years_experience)
        """
        try:
            # This is a simplified parser - in practice you'd use the existing resume parser
            content = self._read_file_content(file_path)
            
            # Extract skills (simplified keyword matching)
            skills = self._extract_skills_from_content(content)
            
            # Extract years of experience
            experience_years = self._extract_experience_years(content)
            
            return skills, experience_years
            
        except Exception as e:
            logger.warning(f"Failed to parse resume content {file_path}: {e}")
            return [], 0
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read file content based on format"""
        if file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif file_path.suffix.lower() in ['.pdf', '.docx', '.doc']:
            # In practice, integrate with existing resume parser
            # For now, return filename as proxy for content
            return file_path.stem.replace('_', ' ').replace('-', ' ')
        else:
            return ""
    
    def _extract_skills_from_content(self, content: str) -> List[str]:
        """Extract skills from resume content"""
        skills = []
        content_lower = content.lower()
        
        # Check against all domain keywords
        for domain_keywords in self._domain_keywords.values():
            for keyword in domain_keywords:
                if keyword.lower() in content_lower:
                    skills.append(keyword)
                    
        return list(set(skills))  # Remove duplicates
    
    def _extract_experience_years(self, content: str) -> int:
        """Extract years of experience from content"""
        # Look for patterns like "5 years", "5+ years", etc.
        import re
        
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)',
            r'over\s*(\d+)\s*years?',
            r'more than\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content.lower())
            if matches:
                return max(int(match) for match in matches)
                
        return 0