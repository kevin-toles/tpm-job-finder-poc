"""Hybrid Selection Engine - Two-stage resume selection with keyword pre-filtering and LLM scoring"""

import re
import logging
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from ..models.resume_inventory import (
    ResumeInventory, ResumeMetadata, JobKeywords, SelectionResult
)
from ..models.job import Job
from ..config.multi_resume_config import get_config
from .interfaces import IHybridSelectionEngine

logger = logging.getLogger(__name__)

class HybridSelectionEngine(IHybridSelectionEngine):
    """
    Two-stage resume selection with keyword pre-filtering and LLM scoring
    
    Stage 1: Keyword Pre-filtering - Analyze job keywords against resume domains/filenames to identify 1-3 candidates
    Stage 2: Batch Scoring - If multiple candidates, run LLM scoring and select highest score
    """
    
    def __init__(self, llm_provider=None):
        self.config = get_config()
        self.llm_provider = llm_provider
        
    def analyze_job_keywords(self, job: Job) -> JobKeywords:
        """
        Extract and categorize keywords from job description
        
        Args:
            job: Job posting to analyze
            
        Returns:
            Categorized keywords from job description
        """
        description = f"{job.title} {job.description}".lower()
        
        # Technical skills extraction
        technical_skills = self._extract_domain_keywords(description, "technology")
        
        # Business skills extraction  
        business_skills = self._extract_domain_keywords(description, "business")
        
        # Industry terms (combination of all domains)
        industry_terms = technical_skills + business_skills
        
        # Experience requirements
        experience_requirements = self._extract_experience_requirements(description)
        
        # Responsibilities (action words and role indicators)
        responsibilities = self._extract_responsibilities(description)
        
        return JobKeywords(
            technical_skills=technical_skills,
            business_skills=business_skills,
            industry_terms=industry_terms,
            experience_requirements=experience_requirements,
            responsibilities=responsibilities
        )
    
    def filter_candidate_resumes(self, 
                                keywords: JobKeywords, 
                                inventory: ResumeInventory) -> List[ResumeMetadata]:
        """
        Stage 1: Keyword-based pre-filtering
        
        Args:
            keywords: Extracted job keywords
            inventory: Complete resume inventory
            
        Returns:
            Filtered list of 1-3 candidate resumes
        """
        logger.info("Stage 1: Keyword-based pre-filtering")
        
        candidates = inventory.candidate_resumes
        if not candidates:
            logger.warning("No candidate resumes found")
            return []
        
        # Score each candidate based on keyword matches
        scored_candidates = []
        
        for candidate in candidates:
            score = self._calculate_keyword_match_score(candidate, keywords)
            scored_candidates.append((candidate, score))
            logger.debug(f"{candidate.filename}: keyword score = {score:.3f}")
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by minimum threshold
        threshold = self.config.keyword_match_threshold
        filtered_candidates = [
            candidate for candidate, score in scored_candidates 
            if score >= threshold
        ]
        
        # Limit to top 3 candidates
        max_candidates = min(3, len(filtered_candidates))
        final_candidates = filtered_candidates[:max_candidates]
        
        logger.info(f"Pre-filtering result: {len(final_candidates)} candidates selected")
        for candidate in final_candidates:
            logger.info(f"  - {candidate.filename} ({candidate.domain.value})")
        
        return final_candidates
    
    def batch_score_candidates(self, 
                              job: Job,
                              candidates: List[ResumeMetadata]) -> List[SelectionResult]:
        """
        Stage 2: Batch LLM scoring if multiple candidates
        
        Args:
            job: Job posting for scoring context
            candidates: Pre-filtered candidate resumes
            
        Returns:
            List of selection results with LLM scores
        """
        logger.info(f"Stage 2: Batch LLM scoring for {len(candidates)} candidates")
        
        if not self.llm_provider:
            logger.warning("No LLM provider available, using heuristic scoring")
            return self._fallback_heuristic_scoring(job, candidates)
        
        results = []
        
        # Batch process candidates
        with ThreadPoolExecutor(max_workers=self.config.max_batch_size) as executor:
            future_to_candidate = {
                executor.submit(self._score_candidate_with_llm, job, candidate): candidate
                for candidate in candidates
            }
            
            for future in as_completed(future_to_candidate, timeout=self.config.llm_timeout_seconds):
                candidate = future_to_candidate[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.debug(f"LLM score for {candidate.filename}: {result.match_score:.1f}%")
                except Exception as e:
                    logger.error(f"Failed to score {candidate.filename}: {e}")
                    # Create fallback result
                    fallback_result = self._create_fallback_result(job, candidate)
                    results.append(fallback_result)
        
        return results
    
    def select_optimal_resume(self, 
                             job: Job,
                             inventory: ResumeInventory) -> SelectionResult:
        """
        Complete selection process with rationale
        
        Args:
            job: Job posting to match against
            inventory: Complete resume inventory
            
        Returns:
            Final selection result with rationale
        """
        start_time = time.time()
        
        # Stage 1: Keyword pre-filtering
        keywords = self.analyze_job_keywords(job)
        candidates = self.filter_candidate_resumes(keywords, inventory)
        
        if not candidates:
            # No candidates pass filtering - fallback to best available
            logger.warning("No candidates passed pre-filtering, using fallback selection")
            if inventory.candidate_resumes:
                best_candidate = max(inventory.candidate_resumes, key=lambda r: len(r.skills))
                return SelectionResult(
                    selected_resume=best_candidate,
                    match_score=25.0,  # Low score indicates fallback
                    selection_rationale="Fallback selection: no candidates matched job keywords",
                    keyword_matches=0,
                    domain_match=False,
                    confidence_level=0.2
                )
            else:
                return SelectionResult(
                    selected_resume=None,
                    match_score=0.0,
                    selection_rationale="No candidate resumes available",
                    keyword_matches=0,
                    domain_match=False,
                    confidence_level=0.0
                )
        
        elif len(candidates) == 1:
            # Single candidate - use directly (skip Stage 2)
            candidate = candidates[0]
            keyword_score = self._calculate_keyword_match_score(candidate, keywords)
            
            return SelectionResult(
                selected_resume=candidate,
                match_score=min(keyword_score * 100, 95.0),  # Cap at 95% for single candidate
                selection_rationale=f"Single candidate matched job requirements in {candidate.domain.value} domain",
                keyword_matches=len(self._get_matching_keywords(candidate, keywords)),
                domain_match=self._check_domain_match(candidate, keywords),
                confidence_level=0.8
            )
        
        else:
            # Multiple candidates - Stage 2: LLM scoring
            scored_results = self.batch_score_candidates(job, candidates)
            
            if not scored_results:
                # Fallback if LLM scoring fails
                return self.select_optimal_resume(job, ResumeInventory(
                    master_resume=inventory.master_resume,
                    candidate_resumes=[candidates[0]],  # Just pick first
                    base_path=inventory.base_path
                ))
            
            # Select highest scoring result
            best_result = max(scored_results, key=lambda r: r.match_score)
            
            processing_time = time.time() - start_time
            logger.info(f"Selection completed in {processing_time:.2f}s: {best_result.selected_resume.filename} "
                       f"(score: {best_result.match_score:.1f}%)")
            
            return best_result
    
    def _extract_domain_keywords(self, text: str, domain: str) -> List[str]:
        """Extract keywords for specific domain from text"""
        domain_keywords = self.config.domain_keywords.get(domain, [])
        found_keywords = []
        
        for keyword in domain_keywords:
            if keyword.lower() in text:
                found_keywords.append(keyword)
                
        return found_keywords
    
    def _extract_experience_requirements(self, text: str) -> List[str]:
        """Extract experience requirements from job description"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'senior|lead|principal|staff|director',
            r'junior|entry.level|associate',
            r'mid.level|intermediate'
        ]
        
        requirements = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements.extend(matches)
            
        return requirements
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibility keywords from job description"""
        responsibility_keywords = [
            "lead", "manage", "develop", "design", "implement", "build", "create",
            "analyze", "optimize", "collaborate", "coordinate", "oversee", "drive",
            "deliver", "execute", "maintain", "support", "troubleshoot"
        ]
        
        found_responsibilities = []
        for keyword in responsibility_keywords:
            if keyword in text:
                found_responsibilities.append(keyword)
                
        return found_responsibilities
    
    def _calculate_keyword_match_score(self, candidate: ResumeMetadata, keywords: JobKeywords) -> float:
        """Calculate keyword match score for a candidate"""
        total_keywords = len(keywords.technical_skills) + len(keywords.business_skills)
        if total_keywords == 0:
            return 0.0
        
        # Check matches in candidate skills
        matches = 0
        candidate_skills_lower = [skill.lower() for skill in candidate.skills]
        
        for keyword in keywords.technical_skills + keywords.business_skills:
            if keyword.lower() in candidate_skills_lower:
                matches += 1
        
        # Check matches in filename/folder structure
        filename_lower = candidate.filename.lower()
        for keyword in keywords.technical_skills + keywords.business_skills:
            if keyword.lower() in filename_lower:
                matches += 0.5  # Partial credit for filename matches
        
        return matches / total_keywords
    
    def _get_matching_keywords(self, candidate: ResumeMetadata, keywords: JobKeywords) -> List[str]:
        """Get list of matching keywords between candidate and job"""
        matches = []
        candidate_skills_lower = [skill.lower() for skill in candidate.skills]
        
        for keyword in keywords.technical_skills + keywords.business_skills:
            if keyword.lower() in candidate_skills_lower:
                matches.append(keyword)
                
        return matches
    
    def _check_domain_match(self, candidate: ResumeMetadata, keywords: JobKeywords) -> bool:
        """Check if candidate domain matches job requirements"""
        if keywords.technical_skills and candidate.domain.value == "technology":
            return True
        if keywords.business_skills and candidate.domain.value == "business":
            return True
        return False
    
    def _score_candidate_with_llm(self, job: Job, candidate: ResumeMetadata) -> SelectionResult:
        """Score a single candidate using LLM"""
        try:
            # Create scoring prompt
            prompt = self._create_scoring_prompt(job, candidate)
            
            # Get LLM score
            llm_response = self.llm_provider.get_signals(prompt)
            
            # Parse LLM response
            match_score, rationale = self._parse_llm_response(llm_response)
            
            return SelectionResult(
                selected_resume=candidate,
                match_score=match_score,
                selection_rationale=rationale,
                keyword_matches=len(self._get_matching_keywords(candidate, self.analyze_job_keywords(job))),
                domain_match=self._check_domain_match(candidate, self.analyze_job_keywords(job)),
                confidence_level=0.9  # High confidence for LLM scores
            )
            
        except Exception as e:
            logger.error(f"LLM scoring failed for {candidate.filename}: {e}")
            return self._create_fallback_result(job, candidate)
    
    def _create_scoring_prompt(self, job: Job, candidate: ResumeMetadata) -> str:
        """Create LLM prompt for resume scoring"""
        return f"""
        Score the fit between this resume and job posting on a scale of 0-100:
        
        Job: {job.title} at {job.company}
        Job Description: {job.description[:500]}...
        
        Resume: {candidate.filename}
        Domain: {candidate.domain.value}
        Skills: {', '.join(candidate.skills[:10])}
        Experience: {candidate.experience_years} years
        
        Provide response in format:
        SCORE: [0-100]
        REASON: [brief explanation]
        """
    
    def _parse_llm_response(self, response: Any) -> tuple[float, str]:
        """Parse LLM response to extract score and rationale"""
        try:
            if isinstance(response, dict) and 'response' in response:
                text = response['response']
            else:
                text = str(response)
            
            # Extract score
            score_match = re.search(r'SCORE:\s*(\d+)', text)
            score = float(score_match.group(1)) if score_match else 50.0
            
            # Extract reason
            reason_match = re.search(r'REASON:\s*(.+)', text)
            reason = reason_match.group(1).strip() if reason_match else "LLM scoring completed"
            
            return score, reason
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return 50.0, "LLM response parsing failed"
    
    def _create_fallback_result(self, job: Job, candidate: ResumeMetadata) -> SelectionResult:
        """Create fallback result when LLM scoring fails"""
        keywords = self.analyze_job_keywords(job)
        keyword_score = self._calculate_keyword_match_score(candidate, keywords)
        
        return SelectionResult(
            selected_resume=candidate,
            match_score=keyword_score * 80,  # Scale down for fallback
            selection_rationale=f"Keyword-based scoring (LLM unavailable): {candidate.domain.value} domain match",
            keyword_matches=len(self._get_matching_keywords(candidate, keywords)),
            domain_match=self._check_domain_match(candidate, keywords),
            confidence_level=0.6  # Lower confidence for fallback
        )
    
    def _fallback_heuristic_scoring(self, job: Job, candidates: List[ResumeMetadata]) -> List[SelectionResult]:
        """Fallback to heuristic scoring when LLM is unavailable"""
        logger.info("Using fallback heuristic scoring")
        
        keywords = self.analyze_job_keywords(job)
        results = []
        
        for candidate in candidates:
            result = self._create_fallback_result(job, candidate)
            results.append(result)
            
        return results