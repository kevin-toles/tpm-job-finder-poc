"""
User model for the job finder system.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class User:
    """User model for job finder application."""
    
    id: str
    name: str
    email: str
    skills: List[str]
    experience_years: int
    current_title: Optional[str] = None
    location: Optional[str] = None
    resume_path: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.preferences is None:
            self.preferences = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "skills": self.skills,
            "experience_years": self.experience_years,
            "current_title": self.current_title,
            "location": self.location,
            "resume_path": self.resume_path,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary data."""
        # Parse datetime fields if they exist
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
            
        updated_at = None
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
            
        return cls(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            skills=data.get('skills', []),
            experience_years=data.get('experience_years', 0),
            current_title=data.get('current_title'),
            location=data.get('location'),
            resume_path=data.get('resume_path'),
            preferences=data.get('preferences', {}),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def add_skill(self, skill: str) -> None:
        """Add a skill to the user's skill list."""
        if skill and skill not in self.skills:
            self.skills.append(skill)
            self.updated_at = datetime.now()
    
    def remove_skill(self, skill: str) -> None:
        """Remove a skill from the user's skill list."""
        if skill in self.skills:
            self.skills.remove(skill)
            self.updated_at = datetime.now()
    
    def update_preference(self, key: str, value: Any) -> None:
        """Update a user preference."""
        self.preferences[key] = value
        self.updated_at = datetime.now()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference with optional default."""
        return self.preferences.get(key, default)
