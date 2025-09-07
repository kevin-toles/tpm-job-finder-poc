"""
HeuristicScorer: Deterministic resume-to-job fit scoring for Senior TPM roles
Objective scoring, informed by recruiter/hiring manager psychology
"""
from typing import List, Dict, Any, Optional
import re

import json
import os

class HeuristicScorer:
    DEFAULT_WEIGHTS = {
        "responsibilities": 20,
        "keywords": 15,
        "skills": 15,
        "achievements": 10,
        "impact": 10,
        "education": 10,
        "certifications": 10,
        "experience": 10,
        "project_impact": 10,
    }
    CATEGORIES = [
        (95, "Strong"),
        (85, "High"),
        (70, "Average"),
        (50, "Weak"),
        (30, "Unlikely"),
        (0, "Negligible"),
    ]

    def __init__(self, job_desc: Dict[str, Any], weights: Optional[Dict[str, int]] = None, config_path: Optional[str] = None):
        self.job_desc = job_desc
        self.keywords = set(job_desc.get("keywords", []))
        self.responsibilities = set(job_desc.get("responsibilities", []))
        self.skills = set(job_desc.get("skills", []))
        self.must_haves = set(job_desc.get("must_haves", []))
        self.education = set(job_desc.get("education", []))
        self.certifications = set(job_desc.get("certifications", []))
        self.required_experience = job_desc.get("years_experience", 0)
        self.project_impact_terms = set(job_desc.get("project_impact", []))
        self.impact_terms = {"improved", "increased", "reduced", "saved", "delivered", "launched", "grew", "cut", "boosted"}
        self.achievement_pattern = re.compile(r"\b(\d+|%|million|billion|k)\b", re.I)
        self.weights = self._load_weights(weights, config_path)
        self.feedback_log = []

    def _load_weights(self, weights, config_path):
        if weights:
            return weights
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        return self.DEFAULT_WEIGHTS.copy()

    def score_bullet(self, bullet: str, resume_meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        bullet_lower = bullet.lower()
        resp_matches = sum(1 for r in self.responsibilities if r.lower() in bullet_lower)
        resp_score = self._bucket_score(resp_matches, len(self.responsibilities), self.weights["responsibilities"])
        kw_matches = sum(1 for k in self.keywords if k.lower() in bullet_lower)
        kw_score = self._bucket_score(kw_matches, len(self.keywords), self.weights["keywords"])
        skill_matches = sum(1 for s in self.skills if s.lower() in bullet_lower)
        skill_score = self._bucket_score(skill_matches, len(self.skills), self.weights["skills"])
        ach_matches = len(self.achievement_pattern.findall(bullet))
        ach_score = self._bucket_score(ach_matches, 3, self.weights["achievements"])
        impact_matches = sum(1 for t in self.impact_terms if t in bullet_lower)
        impact_score = self._bucket_score(impact_matches, 2, self.weights["impact"])
        # New features
        edu_score = 0
        cert_score = 0
        exp_score = 0
        proj_score = 0
        rationale_parts = []
        if resume_meta:
            # Education
            edu_matches = sum(1 for e in self.education if e.lower() in resume_meta.get("education", "").lower())
            edu_score = self._bucket_score(edu_matches, len(self.education), self.weights["education"])
            rationale_parts.append(f"Education matches: {edu_matches}/{len(self.education)}")
            # Certifications
            cert_matches = sum(1 for c in self.certifications if c.lower() in resume_meta.get("certifications", "").lower())
            cert_score = self._bucket_score(cert_matches, len(self.certifications), self.weights["certifications"])
            rationale_parts.append(f"Certifications matches: {cert_matches}/{len(self.certifications)}")
            # Experience
            years = resume_meta.get("years_experience", 0)
            exp_score = self.weights["experience"] if years >= self.required_experience else 0
            rationale_parts.append(f"Years experience: {years} (required: {self.required_experience})")
            # Project impact
            proj_matches = sum(1 for p in self.project_impact_terms if p.lower() in bullet_lower)
            proj_score = self._bucket_score(proj_matches, len(self.project_impact_terms), self.weights["project_impact"])
            rationale_parts.append(f"Project impact matches: {proj_matches}/{len(self.project_impact_terms)}")
        total = resp_score + kw_score + skill_score + ach_score + impact_score + edu_score + cert_score + exp_score + proj_score
        category = self._categorize(total)
        rationale = self._feedback(bullet, resp_matches, kw_matches, skill_matches, ach_matches, impact_matches)
        rationale += "; " + "; ".join(rationale_parts)
        return {
            "bullet": bullet,
            "responsibilities": resp_score,
            "keywords": kw_score,
            "skills": skill_score,
            "achievements": ach_score,
            "impact": impact_score,
            "education": edu_score,
            "certifications": cert_score,
            "experience": exp_score,
            "project_impact": proj_score,
            "total": total,
            "category": category,
            "rationale": rationale
        }

    def score_resume(self, bullets: List[str], resume_meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        results = [self.score_bullet(b, resume_meta) for b in bullets]
        overall = sum(r["total"] for r in results) // max(1, len(results))
        category = self._categorize(overall)
        rationales = [r["rationale"] for r in results]
        return {
            "bullets": results,
            "overall_score": overall,
            "category": category,
            "rationales": rationales
        }

    def log_feedback(self, resume_id: str, feedback: str):
        # Stub: In production, store feedback in DB or file
        self.feedback_log.append({"resume_id": resume_id, "feedback": feedback})
        # Optionally write to file
        # with open("heuristic_feedback.log", "a") as f:
        #     f.write(json.dumps({"resume_id": resume_id, "feedback": feedback}) + "\n")

    def _bucket_score(self, matches: int, total_possible: int, max_points: int) -> int:
        # Objective: scale score by match ratio, subjective: use buckets for realism
        if total_possible == 0:
            return 0
        ratio = matches / total_possible
        if ratio >= 0.85:
            return max_points
        elif ratio >= 0.65:
            return int(max_points * 0.8)
        elif ratio >= 0.45:
            return int(max_points * 0.6)
        elif ratio >= 0.25:
            return int(max_points * 0.4)
        elif matches > 0:
            return int(max_points * 0.2)
        return 0

    def _categorize(self, score: int) -> str:
        for threshold, label in self.CATEGORIES:
            if score >= threshold:
                return label
        return "Negligible"

    def _feedback(self, bullet: str, resp_matches, kw_matches, skill_matches, ach_matches, impact_matches) -> str:
        feedback = []
        if resp_matches == 0:
            feedback.append("No direct match to job responsibilities.")
        if kw_matches < max(1, len(self.keywords)//3):
            feedback.append("Few relevant keywords found.")
        if skill_matches < max(1, len(self.skills)//3):
            feedback.append("Limited skill alignment.")
        if ach_matches == 0:
            feedback.append("No quantifiable achievements detected.")
        if impact_matches == 0:
            feedback.append("No impact/result terms found.")
        if not feedback:
            feedback.append("Strong alignment with job requirements.")
        return "; ".join(feedback)
