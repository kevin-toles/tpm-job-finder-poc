"""
Utility functions for data processing and manipulation.

This module contains common utility functions used throughout the application.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.,;:!?\-()]', '', text)
    
    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Simple keyword extraction - in production would use NLP
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [word for word in words if len(word) >= min_length]
    
    # Remove common stop words
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [word for word in keywords if word not in stop_words]
    
    return list(set(keywords))


def parse_salary_range(salary_str: str) -> Optional[Dict[str, int]]:
    """
    Parse salary range from text.
    
    Args:
        salary_str: Salary string to parse
        
    Returns:
        Dictionary with min and max salary or None
    """
    if not salary_str:
        return None
    
    # Simple regex patterns for salary parsing
    patterns = [
        r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)',  # $100,000 - $150,000
        r'\$(\d{1,3}(?:,\d{3})*)',  # $100,000
        r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)',  # 100,000 - 150,000
    ]
    
    for pattern in patterns:
        match = re.search(pattern, salary_str)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                min_sal = int(groups[0].replace(',', ''))
                max_sal = int(groups[1].replace(',', ''))
                return {'min': min_sal, 'max': max_sal}
            elif len(groups) == 1:
                salary = int(groups[0].replace(',', ''))
                return {'min': salary, 'max': salary}
    
    return None


def calculate_days_ago(date_str: str) -> int:
    """
    Calculate how many days ago a date was.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Number of days ago
    """
    try:
        # Try common date formats
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
        
        for fmt in formats:
            try:
                date = datetime.strptime(date_str, fmt)
                return (datetime.now() - date).days
            except ValueError:
                continue
        
        return 0
    except Exception:
        return 0


def normalize_location(location: str) -> str:
    """
    Normalize location string.
    
    Args:
        location: Raw location string
        
    Returns:
        Normalized location
    """
    if not location:
        return ""
    
    # Clean and standardize location
    location = location.strip().title()
    
    # Handle common remote variations
    remote_terms = ['remote', 'work from home', 'wfh', 'telecommute']
    for term in remote_terms:
        if term.lower() in location.lower():
            return "Remote"
    
    return location


def generate_job_hash(title: str, company: str, location: str) -> str:
    """
    Generate a hash for job deduplication.
    
    Args:
        title: Job title
        company: Company name
        location: Job location
        
    Returns:
        Hash string for deduplication
    """
    import hashlib
    
    # Normalize inputs for consistent hashing
    normalized = f"{title.lower().strip()}_{company.lower().strip()}_{location.lower().strip()}"
    return hashlib.md5(normalized.encode()).hexdigest()[:12]