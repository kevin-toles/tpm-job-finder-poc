"""
TaxonomyMapper: Utility for mapping skills, titles, and entities to standardized taxonomies
Supports Workday Skills Cloud, O*NET, ESCO, and custom mappings
"""
from typing import List, Dict, Optional

class TaxonomyMapper:
    def __init__(self, taxonomy_source: Optional[str] = None):
        self.taxonomy_source = taxonomy_source or "custom"
        self.taxonomy = self._load_taxonomy(self.taxonomy_source)

    def _load_taxonomy(self, source: str):
        # Expandable: load from file, API, or database
        if source == "workday":
            # TODO: Integrate Workday Skills Cloud API or file
            return {
                "tpm": "Technical Program Manager",
                "agile": "Agile Methodology",
                "cloud": "Cloud Computing",
                "python": "Python Programming Language",
                "jira": "Jira Software",
                "pmp": "Project Management Professional"
                # ...add Workday mappings...
            }
        elif source == "onet":
            # TODO: Integrate O*NET taxonomy
            return {
                "tpm": "Technical Program Manager",
                "agile": "Agile Methodology",
                "cloud": "Cloud Computing",
                "python": "Python Programming Language",
                "jira": "Jira Software",
                "pmp": "Project Management Professional"
                # ...add O*NET mappings...
            }
        elif source == "esco":
            # TODO: Integrate ESCO taxonomy
            return {
                "tpm": "Technical Program Manager",
                "agile": "Agile Methodology",
                "cloud": "Cloud Computing",
                "python": "Python Programming Language",
                "jira": "Jira Software",
                "pmp": "Project Management Professional"
                # ...add ESCO mappings...
            }
        elif source == "custom":
            # Custom or default mapping
            return {
                "tpm": "Technical Program Manager",
                "agile": "Agile Methodology",
                "cloud": "Cloud Computing",
                "python": "Python Programming Language",
                "jira": "Jira Software",
                "pmp": "Project Management Professional"
            }
        else:
            # Fallback: empty mapping
            return {}

    def map_skill(self, skill: str) -> str:
        return self.taxonomy.get(skill.lower(), skill)

    def map_title(self, title: str) -> str:
        return self.taxonomy.get(title.lower(), title)

    def map_skills(self, skills: List[str]) -> List[str]:
        return [self.map_skill(s) for s in skills]

    def map_titles(self, titles: List[str]) -> List[str]:
        return [self.map_title(t) for t in titles]

# Example usage:
# mapper = TaxonomyMapper()
# print(mapper.map_skill("tpm"))
# print(mapper.map_skills(["tpm", "python", "cloud"]))
