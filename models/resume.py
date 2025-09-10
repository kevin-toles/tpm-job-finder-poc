"""Resume data model"""

from typing import List, Optional
from pydantic import BaseModel

class Resume(BaseModel):
    """Resume data structure"""
    
    id: Optional[str] = None
    user_id: str
    content: str
    skills: List[str] = []
    experience: List[dict] = []
    education: List[dict] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
