"""
JDParser: Extracts structured job description data from raw text
Output: dict with keywords, responsibilities, skills, must-haves, education, certs, experience, etc.
"""
import re
from typing import Dict, Any

class JDParser:
    def parse(self, jd_text: str) -> Dict[str, Any]:
        # Simple regex-based extraction (can be improved with LLM or NLP)
        lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
        result = {
            "keywords": [],
            "responsibilities": [],
            "skills": [],
            "must_haves": [],
            "education": [],
            "certifications": [],
            "years_experience": 0,
            "project_impact": [],
            "titles": [],
            "companies": [],
            "timeline": [],
            "ko_requirements": {}
        }
        for line in lines:
            # KO: Degree
            if re.search(r"(required|must[- ]have).*(degree|bachelor|master|phd)", line, re.I):
                result["ko_requirements"]["degree"] = True
            # KO: Certifications
            if re.search(r"(required|must[- ]have).*(certification|PMP|AWS|GCP|Azure)", line, re.I):
                result["ko_requirements"]["certifications"] = True
            # KO: Location
            if re.search(r"(required|must[- ]have).*(location|remote|onsite|hybrid|US citizen|work auth)", line, re.I):
                result["ko_requirements"]["location"] = True
            # KO: Years experience
            if re.search(r"(required|must[- ]have).*(\d+\+? years?)", line, re.I):
                match = re.search(r"(\d+\+? years?)", line, re.I)
                if match:
                    result["ko_requirements"]["years_experience"] = match.group(1)
            # KO: Clearance
            if re.search(r"(required|must[- ]have).*(clearance|secret|top secret|public trust)", line, re.I):
                result["ko_requirements"]["clearance"] = True
            # Keywords
            if re.search(r"keywords?[:\-]", line, re.I):
                result["keywords"].extend(self._extract_list(line))
            # Responsibilities
            elif re.search(r"responsibilit(y|ies)[:\-]", line, re.I):
                result["responsibilities"].extend(self._extract_list(line))
            # Skills
            elif re.search(r"skills?[:\-]", line, re.I):
                result["skills"].extend(self._extract_list(line))
            # Must-haves
            elif re.search(r"must[- ]?haves?[:\-]", line, re.I):
                result["must_haves"].extend(self._extract_list(line))
            # Education
            elif re.search(r"education[:\-]", line, re.I):
                result["education"].extend(self._extract_list(line))
            # Certifications
            elif re.search(r"certifications?[:\-]", line, re.I):
                result["certifications"].extend(self._extract_list(line))
            # Years experience
            elif re.search(r"(\d+)\+? years?", line, re.I):
                match = re.search(r"(\d+)\+? years?", line, re.I)
                if match:
                    result["years_experience"] = int(match.group(1))
            # Project impact
            elif re.search(r"impact[:\-]", line, re.I):
                result["project_impact"].extend(self._extract_list(line))
            # Titles
            elif re.search(r"title[:\-]", line, re.I):
                result["titles"].extend(self._extract_list(line))
            # Companies
            elif re.search(r"company[:\-]", line, re.I):
                result["companies"].extend(self._extract_list(line))
            # Timeline (dates)
            elif re.search(r"(\d{4})", line):
                result["timeline"].append(line)
        return result

    def _extract_list(self, line: str):
        # Extract comma-separated or semicolon-separated items
        items = re.split(r"[:,\-]", line, maxsplit=1)
        if len(items) < 2:
            return []
        return [i.strip() for i in re.split(r",|;|\|", items[1]) if i.strip()]

# Example usage:
# parser = JDParser()
# jd_struct = parser.parse(jd_text)
# print(jd_struct)
