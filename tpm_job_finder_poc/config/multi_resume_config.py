"""Configuration management for multi-resume intelligence"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import os

@dataclass
class MultiResumeConfig:
    """Configuration for multi-resume intelligence system"""
    
    # Resume folder configuration
    resume_folder_path: Optional[Path] = None
    master_folder_names: List[str] = field(default_factory=lambda: ["master", "complete", "comprehensive"])
    
    # Similarity thresholds
    semantic_similarity_threshold: float = 0.8  # >80% similarity = exclude enhancement
    enhancement_similarity_threshold: float = 0.2  # >20% similarity between enhancements = exclude
    keyword_match_threshold: float = 0.3  # Minimum keyword match for pre-filtering
    domain_classification_confidence: float = 0.6  # Minimum confidence for domain classification
    
    # Domain keywords for classification
    domain_keywords: Dict[str, List[str]] = field(default_factory=lambda: {
        "technology": [
            "python", "java", "javascript", "react", "node", "sql", "api", "backend", 
            "frontend", "database", "cloud", "aws", "docker", "kubernetes", "ml", 
            "machine learning", "ai", "data science", "algorithms", "software", 
            "engineering", "development", "programming", "coding", "technical",
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "keras"
        ],
        "business": [
            "sales", "marketing", "finance", "accounting", "consulting", "strategy",
            "operations", "management", "leadership", "revenue", "profit", "roi",
            "kpi", "metrics", "analysis", "business", "corporate", "enterprise",
            "client", "customer", "stakeholder", "negotiation", "deals"
        ],
        "creative": [
            "design", "creative", "art", "visual", "graphics", "ui", "ux", "brand",
            "marketing", "content", "writing", "copy", "photography", "video",
            "animation", "illustration", "typography", "layout", "portfolio"
        ]
    })
    
    # Performance limits
    max_batch_size: int = 10  # Maximum resumes to score in one batch
    llm_timeout_seconds: int = 30  # Timeout for LLM API calls
    max_processing_time_seconds: int = 120  # Maximum total processing time
    
    # Enhancement selection
    max_enhancements: int = 3  # Number of enhancements to generate
    min_enhancement_relevance_score: float = 0.5  # Minimum relevance score
    
    # File handling
    supported_resume_formats: List[str] = field(default_factory=lambda: [".pdf", ".docx", ".txt", ".doc"])
    max_file_size_mb: int = 10  # Maximum resume file size
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'MultiResumeConfig':
        """Load configuration from JSON file"""
        if not config_path.exists():
            return cls()  # Return default config
            
        with open(config_path, 'r') as f:
            data = json.load(f)
            
        # Convert string paths to Path objects
        if 'resume_folder_path' in data and data['resume_folder_path']:
            data['resume_folder_path'] = Path(data['resume_folder_path'])
            
        return cls(**data)
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to JSON file"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert Path objects to strings for JSON serialization
        data = self.__dict__.copy()
        if self.resume_folder_path:
            data['resume_folder_path'] = str(self.resume_folder_path)
            
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_master_folder_pattern(self) -> str:
        """Get regex pattern for master folder detection"""
        return f"({'|'.join(self.master_folder_names)})"
    
    def is_supported_format(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        return file_path.suffix.lower() in self.supported_resume_formats
    
    def validate_file_size(self, file_path: Path) -> bool:
        """Check if file size is within limits"""
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            return size_mb <= self.max_file_size_mb
        except OSError:
            return False

# Global configuration instance
_config: Optional[MultiResumeConfig] = None

def get_config() -> MultiResumeConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        # Try to load from environment or default location
        config_path = os.getenv('MULTI_RESUME_CONFIG_PATH', 'config/multi_resume_config.json')
        _config = MultiResumeConfig.load_from_file(Path(config_path))
    return _config

def set_config(config: MultiResumeConfig) -> None:
    """Set global configuration instance"""
    global _config
    _config = config

def update_config(**kwargs) -> None:
    """Update global configuration with new values"""
    config = get_config()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")