"""
Indeed scraper configuration.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class IndeedConfig:
    """Configuration for Indeed scraper."""
    headless: bool = True
    max_pages: int = 3
    request_delay: float = 2.0
    timeout: int = 15
    
    # Anti-detection settings
    use_random_user_agent: bool = True
    simulate_human_behavior: bool = True
    
    # Default search parameters
    default_location: Optional[str] = None
    default_keywords: Optional[List[str]] = None


def get_indeed_config(**kwargs) -> IndeedConfig:
    """
    Get Indeed configuration with defaults.
    
    Args:
        **kwargs: Configuration overrides
        
    Returns:
        IndeedConfig object
    """
    return IndeedConfig(**kwargs)
