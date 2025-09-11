"""
TimelineAnalyzer: Extracts and scores recency and time-in-title/function from resume timeline
"""
import re
from typing import List, Dict, Any
from datetime import datetime

class TimelineAnalyzer:
    def extract_roles(self, timeline: List[str]) -> List[Dict[str, Any]]:
        # Example: parse lines like "Senior TPM, BigTech, 2020-2025"
        roles = []
        for line in timeline:
            match = re.match(r"(.+?),\s*(.+?),\s*(\d{4})-(\d{4})", line)
            if match:
                title, company, start, end = match.groups()
                roles.append({
                    "title": title.strip(),
                    "company": company.strip(),
                    "start_year": int(start),
                    "end_year": int(end)
                })
        return roles

    def compute_recency(self, roles: List[Dict[str, Any]]) -> Dict[str, float]:
        # Returns recency score for each role (1.0 for current, decays for older)
        current_year = datetime.now().year
        recency_scores = {}
        for role in roles:
            years_ago = current_year - role["end_year"]
            # Decay: 1.0 for current, 0.4 for 2-5 years ago, 0.1 for >5 years
            if years_ago <= 2:
                score = 1.0
            elif years_ago <= 5:
                score = 0.4
            else:
                score = 0.1
            recency_scores[f"{role['title']}@{role['company']}"] = score
        return recency_scores

    def time_in_title(self, roles: List[Dict[str, Any]]) -> Dict[str, int]:
        # Returns time spent in each title
        title_times = {}
        for role in roles:
            duration = role["end_year"] - role["start_year"]
            title_times[role["title"]] = title_times.get(role["title"], 0) + duration
        return title_times

# Example usage:
# analyzer = TimelineAnalyzer()
# roles = analyzer.extract_roles(["Senior TPM, BigTech, 2020-2025"])
# recency = analyzer.compute_recency(roles)
# time_in_title = analyzer.time_in_title(roles)
