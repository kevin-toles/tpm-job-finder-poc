"""Job application data model"""

from typing import Optional
from pydantic import BaseModel

class Application(BaseModel):
    """Job application data structure"""
    
    id: Optional[str] = None
    job_id: str
    user_id: str
    status: str = "applied"
    applied_at: str
    notes: Optional[str] = None
