"""Automated selector maintenance and repair system."""

import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import json
import os
import logging
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import difflib

logger = logging.getLogger(__name__)

@dataclass
class SelectorInfo:
    """Information about a CSS selector."""
    selector: str
    purpose: str
    required: bool
    fallbacks: List[str]
    last_success: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0

class SelectorMaintainer:
    """Maintains and repairs CSS selectors for job scrapers."""
    
    def __init__(self, selectors_file: str):
        """Initialize the selector maintainer.
        
        Args:
            selectors_file: Path to JSON file containing selector definitions
        """
        self.selectors_file = selectors_file
        self.selectors: Dict[str, Dict[str, SelectorInfo]] = {}
        self._load_selectors()
        
    def _load_selectors(self):
        """Load selector definitions from file."""
        if not os.path.exists(self.selectors_file):
            logger.warning(f"Selectors file not found: {self.selectors_file}")
            return
            
        try:
            with open(self.selectors_file, 'r') as f:
                data = json.load(f)
                
            for site, site_selectors in data.items():
                self.selectors[site] = {}
                for purpose, info in site_selectors.items():
                    self.selectors[site][purpose] = SelectorInfo(
                        selector=info['selector'],
                        purpose=purpose,
                        required=info.get('required', True),
                        fallbacks=info.get('fallbacks', [])
                    )
        except Exception as e:
            logger.error(f"Error loading selectors: {str(e)}")
            
    def _save_selectors(self):
        """Save current selector definitions to file."""
        try:
            data = {
                site: {
                    purpose: {
                        'selector': info.selector,
                        'required': info.required,
                        'fallbacks': info.fallbacks
                    }
                    for purpose, info in site_selectors.items()
                }
                for site, site_selectors in self.selectors.items()
            }
            
            with open(self.selectors_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving selectors: {str(e)}")
            
    def get_selector(self, site: str, purpose: str) -> Optional[str]:
        """Get current selector for a specific purpose.
        
        Args:
            site: Website identifier
            purpose: Purpose of the selector (e.g., 'job_title', 'company_name')
            
        Returns:
            Current selector if available, None otherwise
        """
        if site in self.selectors and purpose in self.selectors[site]:
            return self.selectors[site][purpose].selector
        return None
        
    def report_success(self, site: str, purpose: str):
        """Report successful use of a selector.
        
        Args:
            site: Website identifier
            purpose: Purpose of the selector
        """
        if site in self.selectors and purpose in self.selectors[site]:
            info = self.selectors[site][purpose]
            info.success_count += 1
            info.last_success = datetime.now()
            
    def report_failure(self, site: str, purpose: str):
        """Report failed use of a selector.
        
        Args:
            site: Website identifier
            purpose: Purpose of the selector
        """
        if site in self.selectors and purpose in self.selectors[site]:
            info = self.selectors[site][purpose]
            info.failure_count += 1
            
    async def repair_selector(
        self,
        site: str,
        purpose: str,
        html: str,
        sample_content: Optional[str] = None
    ) -> Optional[str]:
        """Attempt to repair a broken selector.
        
        Args:
            site: Website identifier
            purpose: Purpose of the selector
            html: Current page HTML
            sample_content: Optional sample of expected content
            
        Returns:
            Repaired selector if successful, None otherwise
        """
        if site not in self.selectors or purpose not in self.selectors[site]:
            return None
            
        info = self.selectors[site][purpose]
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try fallback selectors first
        for fallback in info.fallbacks:
            element = soup.select_one(fallback)
            if element and self._validate_element(element, purpose, sample_content):
                logger.info(f"Found working fallback selector for {site}/{purpose}: {fallback}")
                info.selector = fallback
                self._save_selectors()
                return fallback
                
        # If no fallbacks work, try to generate new selector
        new_selector = await self._generate_selector(soup, purpose, sample_content)
        if new_selector:
            logger.info(f"Generated new selector for {site}/{purpose}: {new_selector}")
            info.selector = new_selector
            info.fallbacks.insert(0, new_selector)
            self._save_selectors()
            return new_selector
            
        return None
        
    def _validate_element(
        self,
        element: Tag,
        purpose: str,
        sample_content: Optional[str]
    ) -> bool:
        """Validate if an element matches expected characteristics.
        
        Args:
            element: BeautifulSoup Tag to validate
            purpose: Purpose of the selector
            sample_content: Optional sample of expected content
            
        Returns:
            True if element appears valid, False otherwise
        """
        text = element.get_text(strip=True)
        
        if not text:
            return False
            
        if sample_content:
            # Use fuzzy matching to compare content
            similarity = difflib.SequenceMatcher(None, text, sample_content).ratio()
            if similarity < 0.5:  # Adjust threshold as needed
                return False
                
        # Purpose-specific validation
        if purpose == 'job_title':
            # Job titles usually have 2-7 words
            word_count = len(text.split())
            if word_count < 2 or word_count > 7:
                return False
                
        elif purpose == 'company_name':
            # Company names usually have 1-4 words
            word_count = len(text.split())
            if word_count < 1 or word_count > 4:
                return False
                
        elif purpose == 'location':
            # Locations often contain commas or specific words
            if ',' not in text and not any(word in text.lower() for word in ['remote', 'hybrid']):
                return False
                
        elif purpose == 'salary':
            # Salary usually contains numbers and currency symbols
            if not any(c.isdigit() for c in text):
                return False
                
        return True
        
    async def _generate_selector(
        self,
        soup: BeautifulSoup,
        purpose: str,
        sample_content: Optional[str]
    ) -> Optional[str]:
        """Generate new selector based on page structure and content.
        
        Args:
            soup: BeautifulSoup object of the page
            purpose: Purpose of the selector
            sample_content: Optional sample of expected content
            
        Returns:
            Generated selector if successful, None otherwise
        """
        candidates = []
        
        # Search for elements with matching content
        if sample_content:
            for element in soup.find_all(text=True):
                if element.parent and isinstance(element.parent, Tag):
                    similarity = difflib.SequenceMatcher(None, element.strip(), sample_content).ratio()
                    if similarity >= 0.5:
                        candidates.append(element.parent)
                        
        # If no content match, try common patterns
        if not candidates:
            if purpose == 'job_title':
                candidates.extend(soup.find_all(['h1', 'h2', 'h3']))
            elif purpose == 'company_name':
                candidates.extend(soup.find_all(['a', 'span', 'div'], class_=lambda x: x and 'company' in x.lower()))
            elif purpose == 'location':
                candidates.extend(soup.find_all(['span', 'div'], class_=lambda x: x and 'location' in x.lower()))
            elif purpose == 'salary':
                candidates.extend(soup.find_all(['span', 'div'], class_=lambda x: x and 'salary' in x.lower()))
                
        # Generate and score selectors for candidates
        scored_selectors = []
        for element in candidates:
            if not self._validate_element(element, purpose, sample_content):
                continue
                
            # Generate multiple selector variants
            selectors = self._generate_selector_variants(element)
            
            for selector in selectors:
                # Score selector based on uniqueness and robustness
                score = self._score_selector(selector, soup)
                scored_selectors.append((selector, score))
                
        if scored_selectors:
            # Return the highest-scoring selector
            return max(scored_selectors, key=lambda x: x[1])[0]
            
        return None
        
    def _generate_selector_variants(self, element: Tag) -> List[str]:
        """Generate multiple selector variants for an element.
        
        Args:
            element: BeautifulSoup Tag to generate selectors for
            
        Returns:
            List of possible selectors
        """
        selectors = []
        
        # Try with ID
        if element.get('id'):
            selectors.append(f"#{element['id']}")
            
        # Try with classes
        if element.get('class'):
            selectors.append(f"{element.name}.{'.'.join(element['class'])}")
            
        # Try with parent context
        if element.parent and isinstance(element.parent, Tag):
            if element.parent.get('class'):
                selectors.append(f"{element.parent.name}.{'.'.join(element.parent['class'])} > {element.name}")
                
        # Try with sibling context
        prev_sibling = element.find_previous_sibling()
        if prev_sibling and isinstance(prev_sibling, Tag):
            if prev_sibling.get('class'):
                selectors.append(f"{prev_sibling.name}.{'.'.join(prev_sibling['class'])} + {element.name}")
                
        return selectors
        
    def _score_selector(self, selector: str, soup: BeautifulSoup) -> float:
        """Score a selector based on various factors.
        
        Args:
            selector: CSS selector to score
            soup: BeautifulSoup object of the page
            
        Returns:
            Score between 0 and 1
        """
        try:
            matches = soup.select(selector)
            
            # Ideal selectors should match exactly one element
            if len(matches) != 1:
                return 0
                
            score = 1.0
            
            # Prefer ID-based selectors
            if selector.startswith('#'):
                score *= 1.2
                
            # Prefer simple selectors
            score /= (1 + selector.count(' '))
            
            # Prefer class-based selectors over complex ones
            score *= (1 + 0.1 * selector.count('.'))
            
            return min(score, 1.0)
            
        except Exception:
            return 0
