"""
EntityCanonicalizer: Normalizes and maps titles, skills, companies to canonical forms
Supports aliasing and taxonomy expansion
"""
from typing import List, Dict

class EntityCanonicalizer:
    TITLE_ALIASES = {
        "TPM": "Technical Program Manager",
        "PM": "Product Manager",
        "SWE": "Software Engineer",
        "Sr TPM": "Senior Technical Program Manager"
    }
    SKILL_ALIASES = {
        "GCP IAM": "Cloud IAM",
        "LLM": "Large Language Model",
        "OpenAI API": "Large Language Model",
        "Python3": "Python"
    }
    COMPANY_ALIASES = {
        "Google": "Alphabet",
        "Meta": "Facebook",
        "AWS": "Amazon Web Services"
    }
    def canonicalize_titles(self, titles: List[str]) -> List[str]:
        return [self.TITLE_ALIASES.get(t, t) for t in titles]
    def canonicalize_skills(self, skills: List[str]) -> List[str]:
        return [self.SKILL_ALIASES.get(s, s) for s in skills]
    def canonicalize_companies(self, companies: List[str]) -> List[str]:
        return [self.COMPANY_ALIASES.get(c, c) for c in companies]
    def canonicalize(self, jd_or_resume: Dict[str, List[str]]) -> Dict[str, List[str]]:
        # Normalize all supported fields
        out = dict(jd_or_resume)
        if "titles" in out:
            out["titles"] = self.canonicalize_titles(out["titles"])
        if "skills" in out:
            out["skills"] = self.canonicalize_skills(out["skills"])
        if "companies" in out:
            out["companies"] = self.canonicalize_companies(out["companies"])
        return out

# Example usage:
# canonicalizer = EntityCanonicalizer()
# normalized = canonicalizer.canonicalize(jd_struct)
# print(normalized)
