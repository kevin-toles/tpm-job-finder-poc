"""
HeuristicScorer: Deterministic resume-to-job fit scoring for Senior TPM roles
Objective scoring, informed by recruiter/hiring manager psychology
"""
from typing import List, Dict, Any, Optional
import re

import json
import os
from tpm_job_finder_poc.storage.secure_storage import SecureStorage

class HeuristicScorer:
    def _semantic_similarity(self, text_a: str, text_b: str) -> float:
        # Use sentence transformer embeddings for semantic similarity
        try:
            from tpm_job_finder_poc.enrichment.embeddings import EmbeddingEngine
            engine = EmbeddingEngine()
            return engine.similarity(text_a, text_b)
        except Exception as e:
            from tpm_job_finder_poc.error_handler.handler import handle_error
            handle_error(e, context={'component': 'heuristic_scorer', 'method': '_semantic_similarity', 'text_a': text_a, 'text_b': text_b})
            return 0.0
    KO_FIELDS = ["location", "education", "certifications", "years_experience"]

    def _check_kos(self, resume_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Check hard knockouts (KO) and return KO status and failed fields."""
        failed = []
        # Location KO
        if "location" in self.job_desc:
            required_loc = self.job_desc["location"].lower()
            candidate_loc = resume_meta.get("location", "").lower()
            if required_loc and required_loc not in candidate_loc:
                failed.append("location")
        # Education KO
        if self.education:
            edu_matches = any(e.lower() in resume_meta.get("education", "").lower() for e in self.education)
            if not edu_matches:
                failed.append("education")
        # Certifications KO
        if self.certifications:
            cert_matches = any(c.lower() in resume_meta.get("certifications", "").lower() for c in self.certifications)
            if not cert_matches:
                failed.append("certifications")
        # Years experience KO
        if self.required_experience:
            years = resume_meta.get("years_experience", 0)
            if years < self.required_experience:
                failed.append("years_experience")
        return {"ko_failed": bool(failed), "failed_fields": failed}
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
        from tpm_job_finder_poc.enrichment.taxonomy_mapper import TaxonomyMapper
        self.taxonomy_mapper = TaxonomyMapper()
        self.job_desc = job_desc
        # Canonicalize skills and titles using taxonomy mapper
        self.keywords = set(self.taxonomy_mapper.map_skills(job_desc.get("keywords", [])))
        self.responsibilities = set(self.taxonomy_mapper.map_titles(job_desc.get("responsibilities", [])))
        self.skills = set(self.taxonomy_mapper.map_skills(job_desc.get("skills", [])))
        self.must_haves = set(self.taxonomy_mapper.map_skills(job_desc.get("must_haves", [])))
        self.education = set(job_desc.get("education", []))
        self.certifications = set(job_desc.get("certifications", []))
        self.required_experience = job_desc.get("years_experience", 0)
        self.project_impact_terms = set(job_desc.get("project_impact", []))
        self.impact_terms = {"improved", "increased", "reduced", "saved", "delivered", "launched", "grew", "cut", "boosted"}
        self.achievement_pattern = re.compile(r"\b(\d+|%|million|billion|k)\b", re.I)
        self.weights = self._load_weights(weights, config_path)
        self.feedback_log = []
        # BM25/TF-IDF matcher setup
        try:
            from bm25_tfidf.bm25_tfidf_matcher import BM25TFIDFMatcher
            corpus = list(self.keywords | self.responsibilities | self.skills)
            self.bm25_matcher = BM25TFIDFMatcher(corpus) if corpus else None
        except Exception as e:
            from tpm_job_finder_poc.error_handler.handler import handle_error
            handle_error(e, context={'component': 'heuristic_scorer', 'method': '__init__'})
            self.bm25_matcher = None

    def _load_weights(self, weights, config_path):
        if weights:
            return weights
        if config_path and os.path.exists(config_path):
            # Use SecureStorage to load config/weights
            storage = SecureStorage()
            try:
                config_data = storage.load_metadata(config_path)
                if config_data:
                    return config_data
            except Exception as e:
                from tpm_job_finder_poc.error_handler.handler import handle_error
                handle_error(e, context={'component': 'heuristic_scorer', 'method': '_load_weights', 'config_path': config_path})
        return self.DEFAULT_WEIGHTS.copy()

    def score_bullet(self, bullet: str, resume_meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        bullet_lower = bullet.lower()
        # Classic matches
        resp_matches = sum(1 for r in self.responsibilities if r.lower() in bullet_lower)
        kw_matches = sum(1 for k in self.keywords if k.lower() in bullet_lower)
        skill_matches = sum(1 for s in self.skills if s.lower() in bullet_lower)
        # Embedding-based semantic similarity for responsibilities (sentence transformers)
        resp_sem_sim = max([self._semantic_similarity(bullet, r) for r in self.responsibilities], default=0.0) if self.responsibilities else 0.0
        resp_score = self._bucket_score(resp_matches, len(self.responsibilities), self.weights["responsibilities"])
        # Add bonus for semantic similarity above threshold
        if resp_sem_sim > 0.7:
            resp_score = max(resp_score, int(self.weights["responsibilities"] * resp_sem_sim))
        kw_score = self._bucket_score(kw_matches, len(self.keywords), self.weights["keywords"])
        # Embedding-based semantic similarity for skills (sentence transformers)
        skill_sem_sim = max([self._semantic_similarity(bullet, s) for s in self.skills], default=0.0) if self.skills else 0.0
        skill_score = self._bucket_score(skill_matches, len(self.skills), self.weights["skills"])
        if skill_sem_sim > 0.7:
            skill_score = max(skill_score, int(self.weights["skills"] * skill_sem_sim))
        ach_matches = len(self.achievement_pattern.findall(bullet))
        ach_score = self._bucket_score(ach_matches, 3, self.weights["achievements"])
        impact_matches = sum(1 for t in self.impact_terms if t in bullet_lower)
        impact_score = self._bucket_score(impact_matches, 2, self.weights["impact"])
        # BM25/TF-IDF matcher scores
        bm25_scores = None
        if self.bm25_matcher:
            try:
                bm25_scores = self.bm25_matcher.score(bullet)
            except Exception as e:
                from tpm_job_finder_poc.error_handler.handler import handle_error
                handle_error(e, context={'component': 'heuristic_scorer', 'method': 'score_bullet', 'bullet': bullet})
                bm25_scores = None
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
        # Optionally add BM25/TF-IDF scores to rationale and output
        rationale = self._feedback(bullet, resp_matches, kw_matches, skill_matches, ach_matches, impact_matches)
        rationale += f"; Embedding Resp sim: {resp_sem_sim:.2f}; Embedding Skill sim: {skill_sem_sim:.2f}; " + "; ".join(rationale_parts)
        if bm25_scores:
            rationale += f"; BM25/TFIDF: {bm25_scores}"
        category = self._categorize(total)
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
            "rationale": rationale,
            "resp_sem_sim": resp_sem_sim,
            "skill_sem_sim": skill_sem_sim,
            "bm25_tfidf": bm25_scores
        }

    def score_resume(self, bullets: List[str], resume_meta: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        results = [self.score_bullet(b, resume_meta) for b in bullets]
        overall = sum(r["total"] for r in results) // max(1, len(results))
        category = self._categorize(overall)
        rationales = [r["rationale"] for r in results]
        # KO logic
        ko_result = self._check_kos(resume_meta or {})
        ko_failed = ko_result["ko_failed"]
        failed_fields = ko_result["failed_fields"]
        # Evidence map: which bullet matched which JD signal
        evidence_map = {}
        for idx, bullet_result in enumerate(results):
            evidence_map[idx] = {
                "bullet": bullet_result["bullet"],
                "matches": {
                    "responsibilities": bullet_result["responsibilities"],
                    "keywords": bullet_result["keywords"],
                    "skills": bullet_result["skills"],
                    "education": bullet_result["education"],
                    "certifications": bullet_result["certifications"],
                    "experience": bullet_result["experience"],
                    "project_impact": bullet_result["project_impact"]
                }
            }
        # Gap map: missing/weak signals
        gap_map = []
        if ko_failed:
            gap_map.extend([f"KO failed: {field}" for field in failed_fields])
        # Check for weak signals in sub-scores
        for key in ["responsibilities", "keywords", "skills", "education", "certifications", "experience", "project_impact"]:
            total_possible = getattr(self, key, None)
            if isinstance(total_possible, set):
                total_possible = len(total_possible)
            elif key == "experience":
                total_possible = self.required_experience
            score_sum = sum(b[key] for b in results)
            if total_possible and score_sum == 0:
                gap_map.append(f"No match for {key}")
        # PSL mapping
        psl = self._map_psl(overall, ko_failed, context)
        return {
            "bullets": results,
            "overall_score": overall,
            "category": category,
            "rationales": rationales,
            "ko_failed": ko_failed,
            "failed_kos": failed_fields,
            "evidence_map": evidence_map,
            "gap_map": gap_map,
            "psl": psl
        }
    def _map_psl(self, fit_score: int, ko_failed: bool, context: Optional[Dict[str, Any]]) -> float:
        """Map FitScore and KO status to Phone-Screen Likelihood (PSL)."""
        # Base probabilities by channel/archetype
        base = 0.20  # Default mid-market portal
        if context:
            channel = context.get("channel", "portal")
            archetype = context.get("archetype", "mid-market")
            if channel == "referral":
                base = 0.55 if archetype == "mid-market" else 0.45
            elif channel == "easy_apply":
                base = 0.10 if archetype == "mid-market" else 0.06
            elif channel == "portal":
                base = 0.20 if archetype == "mid-market" else 0.12
        # KO gate
        ko_gate = 0 if ko_failed else 1
        # Fit calibration (logistic curve)
        sigma = 12
        m = 68
        import math
        fit_factor = 1 / (1 + math.exp(-(fit_score - m) / sigma))
        return round(base * ko_gate * fit_factor, 3)

    def log_feedback(self, resume_id: str, feedback: str):
        # Store feedback in memory
        self.feedback_log.append({"resume_id": resume_id, "feedback": feedback})
        # Use SecureStorage for audit logging
        try:
            storage = SecureStorage()
            storage.log_event("heuristic_feedback", {"resume_id": resume_id, "feedback": feedback})
        except Exception as e:
            from tpm_job_finder_poc.error_handler.handler import handle_error
            handle_error(e, context={'component': 'heuristic_scorer', 'method': 'log_feedback', 'resume_id': resume_id})

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
