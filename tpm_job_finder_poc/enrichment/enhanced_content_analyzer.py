"""Enhanced Content Analyzer - Semantic similarity detection and enhancement generation"""

import re
import logging
from typing import List, Dict, Optional, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ..models.resume_inventory import (
    ResumeMetadata, Enhancement, BulletPoint
)
from ..models.job import Job
from ..config.multi_resume_config import get_config
from .interfaces import IEnhancedContentAnalyzer

logger = logging.getLogger(__name__)

class EnhancedContentAnalyzer(IEnhancedContentAnalyzer):
    """
    Master resume analysis with semantic similarity detection
    
    - Parse both resumes: Extract bullet points from selected resume and master resume
    - Identify unique content: Find bullet points in master that are NOT in selected resume
    - Semantic similarity detection: Ensure enhancements are not similar variations of existing content
    - Relevance scoring: Rank master resume bullets by job description alignment
    - Select top 3: Choose most relevant, unique enhancements
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.config = get_config()
        
        # Initialize sentence transformer model
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model: {e}")
            self.model = None
            
        # Cache for embeddings to improve performance
        self._embedding_cache = {}
    
    def extract_bullet_points(self, resume_content: str) -> List[str]:
        """
        Extract bullet points from resume content
        
        Args:
            resume_content: Raw resume text content
            
        Returns:
            List of bullet point strings
        """
        # Patterns for bullet points
        bullet_patterns = [
            r'^\s*[•▪▫◦‣⁃]\s+(.+)',  # Unicode bullets
            r'^\s*[-*]\s+(.+)',        # Dash/asterisk bullets
            r'^\s*\d+\.\s+(.+)',       # Numbered lists
            r'^\s*[a-zA-Z]\.\s+(.+)',  # Lettered lists
        ]
        
        bullets = []
        lines = resume_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in bullet_patterns:
                match = re.match(pattern, line)
                if match:
                    bullet_text = match.group(1).strip()
                    if len(bullet_text) > 20:  # Filter out short bullets
                        bullets.append(bullet_text)
                    break
        
        # If no formal bullet points found, look for sentences with action verbs
        if not bullets:
            bullets = self._extract_action_sentences(resume_content)
        
        logger.debug(f"Extracted {len(bullets)} bullet points")
        return bullets
    
    def calculate_semantic_similarity(self, bullet1: str, bullet2: str) -> float:
        """
        Calculate semantic similarity between bullet points
        
        Args:
            bullet1: First bullet point
            bullet2: Second bullet point
            
        Returns:
            Similarity score between 0 and 1
        """
        if not self.model:
            # Fallback to simple keyword overlap
            return self._calculate_keyword_similarity(bullet1, bullet2)
        
        try:
            # Get embeddings (with caching)
            embedding1 = self._get_embedding(bullet1)
            embedding2 = self._get_embedding(bullet2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate semantic similarity: {e}")
            return self._calculate_keyword_similarity(bullet1, bullet2)
    
    def identify_unique_content(self, 
                               master_bullets: List[str],
                               selected_bullets: List[str]) -> List[str]:
        """
        Find bullet points in master that are NOT in selected resume
        
        Args:
            master_bullets: Bullet points from master resume
            selected_bullets: Bullet points from selected resume
            
        Returns:
            List of unique bullet points from master resume
        """
        unique_bullets = []
        threshold = self.config.semantic_similarity_threshold
        
        for master_bullet in master_bullets:
            is_unique = True
            
            for selected_bullet in selected_bullets:
                similarity = self.calculate_semantic_similarity(master_bullet, selected_bullet)
                
                if similarity >= threshold:
                    logger.debug(f"Rejecting similar content (sim={similarity:.3f}): "
                               f"{master_bullet[:50]}...")
                    is_unique = False
                    break
            
            if is_unique:
                unique_bullets.append(master_bullet)
        
        logger.info(f"Identified {len(unique_bullets)} unique bullets from {len(master_bullets)} master bullets")
        return unique_bullets
    
    def score_relevance_to_job(self, 
                              bullets: List[str],
                              job: Job) -> List[float]:
        """
        Score bullet point relevance to job requirements
        
        Args:
            bullets: List of bullet points to score
            job: Job posting for relevance context
            
        Returns:
            List of relevance scores (0-1) for each bullet
        """
        job_text = f"{job.title} {job.description}".lower()
        job_embedding = self._get_embedding(job_text) if self.model else None
        
        scores = []
        
        for bullet in bullets:
            if self.model and job_embedding is not None:
                # Semantic similarity to job description
                bullet_embedding = self._get_embedding(bullet)
                semantic_score = cosine_similarity([bullet_embedding], [job_embedding])[0][0]
            else:
                # Fallback to keyword overlap
                semantic_score = self._calculate_keyword_similarity(bullet.lower(), job_text)
            
            # Bonus for impact indicators
            impact_score = self._calculate_impact_score(bullet)
            
            # Combined relevance score
            relevance_score = 0.7 * semantic_score + 0.3 * impact_score
            scores.append(float(relevance_score))
        
        return scores
    
    def select_top_enhancements(self, 
                               job: Job,
                               master_resume: ResumeMetadata,
                               selected_resume: ResumeMetadata) -> List[Enhancement]:
        """
        Generate 3 strategic enhancements from master resume
        
        Args:
            job: Job posting for context
            master_resume: Master resume metadata
            selected_resume: Selected resume metadata
            
        Returns:
            List of top 3 enhancements
        """
        logger.info(f"Generating enhancements from master resume for {selected_resume.filename}")
        
        # Extract bullet points from both resumes
        master_content = self._load_resume_content(master_resume)
        selected_content = self._load_resume_content(selected_resume)
        
        master_bullets = self.extract_bullet_points(master_content)
        selected_bullets = self.extract_bullet_points(selected_content)
        
        # Identify unique content in master resume
        unique_bullets = self.identify_unique_content(master_bullets, selected_bullets)
        
        if not unique_bullets:
            logger.warning("No unique content found in master resume")
            return []
        
        # Score relevance to job
        relevance_scores = self.score_relevance_to_job(unique_bullets, job)
        
        # Create enhanced bullet points with metadata
        enhanced_bullets = []
        for bullet, score in zip(unique_bullets, relevance_scores):
            if score >= self.config.min_enhancement_relevance_score:
                enhanced_bullets.append(BulletPoint(
                    text=bullet,
                    semantic_embedding=self._get_embedding(bullet) if self.model else None,
                    relevance_score=score,
                    uniqueness_score=1.0,  # All are unique by definition
                    impact_indicators=self._extract_impact_indicators(bullet)
                ))
        
        # Sort by relevance score
        enhanced_bullets.sort(key=lambda b: b.relevance_score, reverse=True)
        
        # Select top enhancements
        max_enhancements = self.config.max_enhancements
        top_bullets = enhanced_bullets[:max_enhancements]
        
        # Convert to Enhancement objects
        enhancements = []
        categories = ["technical", "leadership", "impact"]  # Rotate categories
        
        for i, bullet in enumerate(top_bullets):
            category = categories[i % len(categories)]
            reasoning = self._generate_enhancement_reasoning(bullet, job, category)
            
            enhancement = Enhancement(
                bullet_point=bullet.text,
                relevance_score=bullet.relevance_score,
                source_resume="master",
                category=category,
                reasoning=reasoning
            )
            enhancements.append(enhancement)
        
        logger.info(f"Generated {len(enhancements)} enhancements with avg relevance score: "
                   f"{np.mean([e.relevance_score for e in enhancements]):.3f}")
        
        return enhancements
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get sentence embedding with caching"""
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        if not self.model:
            raise RuntimeError("Sentence transformer model not available")
        
        embedding = self.model.encode(text)
        self._embedding_cache[text] = embedding
        return embedding
    
    def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """Fallback keyword-based similarity calculation"""
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_impact_score(self, bullet: str) -> float:
        """Calculate impact score based on quantifiable achievements"""
        impact_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+[kmb]',  # Thousands/millions/billions
            r'\d+x',  # Multipliers
            r'increased|improved|reduced|optimized|enhanced|accelerated',  # Impact verbs
            r'led|managed|directed|coordinated|supervised',  # Leadership verbs
        ]
        
        score = 0.0
        bullet_lower = bullet.lower()
        
        for pattern in impact_patterns:
            matches = len(re.findall(pattern, bullet_lower))
            score += matches * 0.2  # Each match adds 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_action_sentences(self, content: str) -> List[str]:
        """Extract sentences that start with action verbs"""
        action_verbs = [
            "led", "managed", "developed", "created", "implemented", "designed",
            "built", "launched", "delivered", "achieved", "improved", "increased",
            "reduced", "optimized", "collaborated", "coordinated", "supervised"
        ]
        
        sentences = re.split(r'[.!?]+', content)
        action_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            words = sentence.lower().split()
            
            if words and words[0] in action_verbs and len(sentence) > 30:
                action_sentences.append(sentence)
        
        return action_sentences[:20]  # Limit to prevent overwhelming
    
    def _extract_impact_indicators(self, bullet: str) -> List[str]:
        """Extract impact indicators from bullet point"""
        indicators = []
        
        # Numerical impacts
        numbers = re.findall(r'\d+%|\$\d+|\d+[kmb]|\d+x', bullet.lower())
        indicators.extend(numbers)
        
        # Impact verbs
        impact_verbs = re.findall(r'increased|improved|reduced|optimized|enhanced|accelerated', bullet.lower())
        indicators.extend(impact_verbs)
        
        return indicators
    
    def _load_resume_content(self, resume: ResumeMetadata) -> str:
        """Load resume content from file"""
        try:
            # In practice, integrate with existing resume parser
            # For now, return a placeholder
            return f"Sample content for {resume.filename}"
        except Exception as e:
            logger.error(f"Failed to load resume content for {resume.filename}: {e}")
            return ""
    
    def _generate_enhancement_reasoning(self, bullet: BulletPoint, job: Job, category: str) -> str:
        """Generate reasoning for why this enhancement was selected"""
        reasoning_templates = {
            "technical": f"Technical expertise relevant to {job.title} position",
            "leadership": f"Leadership experience valuable for {job.title} role",
            "impact": f"Quantifiable achievements aligned with {job.company} goals"
        }
        
        base_reasoning = reasoning_templates.get(category, "Relevant experience for position")
        
        if bullet.impact_indicators:
            base_reasoning += f" (includes: {', '.join(bullet.impact_indicators[:2])})"
        
        return base_reasoning