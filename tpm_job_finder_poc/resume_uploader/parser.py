"""Resume parsing logic"""

from typing import Dict, List

class ResumeParser:
    """Parses resume content"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
        
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract structured data"""
        return {
            'text': '',
            'skills': [],
            'experience': [],
            'education': []
        }
        
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        return []
