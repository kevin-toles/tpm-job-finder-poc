"""Resume metadata management"""

from typing import Dict, Optional

class ResumeMetadata:
    """Manages resume metadata"""
    
    def __init__(self):
        self.metadata_store = {}
        
    def store_metadata(self, resume_id: str, metadata: Dict):
        """Store resume metadata"""
        self.metadata_store[resume_id] = metadata
        
    def get_metadata(self, resume_id: str) -> Optional[Dict]:
        """Get resume metadata"""
        return self.metadata_store.get(resume_id)
        
    def update_metadata(self, resume_id: str, metadata: Dict):
        """Update resume metadata"""
        if resume_id in self.metadata_store:
            self.metadata_store[resume_id].update(metadata)
