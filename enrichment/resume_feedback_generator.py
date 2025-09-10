"""
ResumeFeedbackGenerator: Generates actionable, evidence-based feedback for resume/job fit
Integrates rule-based heuristics and LLM-driven suggestions
"""
from typing import Dict, Any, List, Optional

class ResumeFeedbackGenerator:
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider

    def generate_feedback(self, job_desc: Dict[str, Any], resume_meta: Dict[str, Any], scoring_result: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Returns a list of feedback dicts with fields:
        - message: feedback text
        - severity: critical/recommended/optional
        - evidence: resume section/bullet/job criteria
        - rubric: external guideline/rubric reference
        - priority: int (higher = more important)
        - category: structure, targeting, achievement, skills, llm, analytics
        """
        feedback_items = []
        # Context extraction
        job_level = job_desc.get("role_level", "mid")
        industry = job_desc.get("industry", "general")
        company_type = job_desc.get("company_type", "mid-market")
        archetype = context.get("archetype") if context else "mid-market"
        channel = context.get("channel") if context else "portal"

        # Structure & Presentation
        structure_checks = []
        if scoring_result.get("format_issues"):
            structure_checks.append({
                "message": f"Formatting issues: {scoring_result['format_issues']}",
                "severity": "recommended",
                "evidence": "format_issues",
                "rubric": "General Resume Formatting Best Practices",
                "priority": 2,
                "category": "structure"
            })
        if resume_meta.get("length") and ((resume_meta["length"] > 2 and job_level == "executive") or (resume_meta["length"] > 1 and job_level != "executive")):
            structure_checks.append({
                "message": "Resume length may exceed recommended limit.",
                "severity": "optional",
                "evidence": "length",
                "rubric": "Industry Resume Length Guidelines",
                "priority": 1,
                "category": "structure"
            })
        feedback_items.extend(structure_checks)

        # Targeting & Relevance
        targeting_checks = []
        if scoring_result.get("gap_map"):
            for gap in scoring_result["gap_map"]:
                targeting_checks.append({
                    "message": gap,
                    "severity": "critical" if "KO failed" in gap else "recommended",
                    "evidence": "gap_map",
                    "rubric": "KO/Targeting Rubric",
                    "priority": 3 if "KO failed" in gap else 2,
                    "category": "targeting"
                })
        if job_desc.get("keywords"):
            missing_keywords = [k for k in job_desc["keywords"] if k.lower() not in resume_meta.get("keywords", "").lower()]
            if missing_keywords:
                targeting_checks.append({
                    "message": f"Missing keywords: {', '.join(missing_keywords)}",
                    "severity": "recommended",
                    "evidence": "keywords",
                    "rubric": "JD Keyword Targeting",
                    "priority": 2,
                    "category": "targeting"
                })
        feedback_items.extend(targeting_checks)

        # Achievements & Evidence
        achievement_checks = []
        for bullet in scoring_result.get("bullets", []):
            if bullet.get("achievements", 0) == 0:
                achievement_checks.append({
                    "message": f"Add quantifiable results to: '{bullet['bullet']}'",
                    "severity": "recommended",
                    "evidence": bullet['bullet'],
                    "rubric": "Achievement/Impact Rubric",
                    "priority": 2,
                    "category": "achievement"
                })
            if bullet.get("impact", 0) == 0:
                achievement_checks.append({
                    "message": f"Add impact/result terms to: '{bullet['bullet']}'",
                    "severity": "optional",
                    "evidence": bullet['bullet'],
                    "rubric": "Achievement/Impact Rubric",
                    "priority": 1,
                    "category": "achievement"
                })
        feedback_items.extend(achievement_checks)

        # Skills & Credentials
        skills_checks = []
        missing_skills = [s for s in job_desc.get("skills", []) if s.lower() not in resume_meta.get("skills", "").lower()]
        if missing_skills:
            skills_checks.append({
                "message": f"Missing skills: {', '.join(missing_skills)}",
                "severity": "critical" if job_level in ["senior", "executive"] else "recommended",
                "evidence": "skills",
                "rubric": "Skills Alignment Rubric",
                "priority": 3 if job_level in ["senior", "executive"] else 2,
                "category": "skills"
            })
        missing_certs = [c for c in job_desc.get("certifications", []) if c.lower() not in resume_meta.get("certifications", "").lower()]
        if missing_certs:
            skills_checks.append({
                "message": f"Missing certifications: {', '.join(missing_certs)}",
                "severity": "recommended",
                "evidence": "certifications",
                "rubric": "Certifications Rubric",
                "priority": 2,
                "category": "skills"
            })
        feedback_items.extend(skills_checks)

        # LLM-driven feedback (optional, context-aware)
        if self.llm_provider:
            llm_input = {
                "job_desc": job_desc,
                "resume_meta": resume_meta,
                "scoring_result": scoring_result,
                "context": context or {}
            }
            try:
                llm_feedback = self.llm_provider.get_feedback(llm_input)
                feedback_items.append({
                    "message": llm_feedback,
                    "severity": "recommended",
                    "evidence": "llm",
                    "rubric": f"LLM ({self.llm_provider.__class__.__name__}) Suggestions",
                    "priority": 2,
                    "category": "llm"
                })
            except Exception as e:
                from error_handler.handler import handle_error
                handle_error(e, context={'component': 'resume_feedback_generator', 'method': 'generate_feedback', 'llm_input': llm_input})

        # Analytics: aggregate feedback for reporting
        analytics = {
            "common_gaps": [f["message"] for f in feedback_items if f["severity"] == "critical"],
            "improvement_trends": [f["message"] for f in feedback_items if f["severity"] == "recommended"],
            "feedback_impact": {
                "critical": len([f for f in feedback_items if f["severity"] == "critical"]),
                "recommended": len([f for f in feedback_items if f["severity"] == "recommended"]),
                "optional": len([f for f in feedback_items if f["severity"] == "optional"])
            }
        }
        feedback_items.append({
            "message": f"Analytics summary: {analytics}",
            "severity": "optional",
            "evidence": "analytics",
            "rubric": "Feedback Analytics",
            "priority": 0,
            "category": "analytics"
        })
        return feedback_items

# Example usage:
# generator = ResumeFeedbackGenerator()
# feedback = generator.generate_feedback(job_desc, resume_meta, scoring_result)
