from error_handler.handler import handle_error
"""
Orchestrator: Integrates HeuristicScorer and MLScorer for resume scoring
Returns combined results and rationales
"""
from enrichment.heuristic_scorer import HeuristicScorer
from enrichment.ml_scorer import MLScorer
from llm_provider.base import LLMProvider
import importlib

class ResumeScoringOrchestrator:
    def __init__(self, job_desc=None, ml_model=None, llm_config=None, resume_path=None, jd_text=None):
        # Parse resume if path provided
        if resume_path:
            from enrichment.resume_parser import ResumeParser
            resume_struct = ResumeParser().parse(resume_path)
            # Canonicalize resume entities
            from enrichment.entity_canonicalizer import EntityCanonicalizer
            canonicalizer = EntityCanonicalizer()
            resume_struct["sections"] = canonicalizer.canonicalize(resume_struct["sections"])
            # Timeline analysis for resume
            from enrichment.timeline_analyzer import TimelineAnalyzer
            analyzer = TimelineAnalyzer()
            timeline = resume_struct["sections"].get("timeline", [])
            roles = analyzer.extract_roles(timeline)
            resume_struct["recency_scores"] = analyzer.compute_recency(roles)
            resume_struct["time_in_title"] = analyzer.time_in_title(roles)
            self.resume_struct = resume_struct
        else:
            self.resume_struct = None
        # Parse JD if raw text provided
        if jd_text:
            from enrichment.jd_parser import JDParser
            job_desc = JDParser().parse(jd_text)
            # Canonicalize JD entities
            from enrichment.entity_canonicalizer import EntityCanonicalizer
            canonicalizer = EntityCanonicalizer()
            job_desc = canonicalizer.canonicalize(job_desc)
            # Timeline analysis for JD
            from enrichment.timeline_analyzer import TimelineAnalyzer
            analyzer = TimelineAnalyzer()
            timeline = job_desc.get("timeline", [])
            roles = analyzer.extract_roles(timeline)
            job_desc["recency_scores"] = analyzer.compute_recency(roles)
            job_desc["time_in_title"] = analyzer.time_in_title(roles)
        # Taxonomy mapping for skills/titles
        if job_desc:
            from enrichment.taxonomy_mapper import TaxonomyMapper
            taxonomy_mapper = TaxonomyMapper()
            job_desc["keywords"] = taxonomy_mapper.map_skills(job_desc.get("keywords", []))
            job_desc["responsibilities"] = taxonomy_mapper.map_titles(job_desc.get("responsibilities", []))
            job_desc["skills"] = taxonomy_mapper.map_skills(job_desc.get("skills", []))
            job_desc["must_haves"] = taxonomy_mapper.map_skills(job_desc.get("must_haves", []))
        self.heuristic = HeuristicScorer(job_desc)
        self.ml = MLScorer(model=ml_model)
        self.llm = self._init_llm(llm_config)
        # BM25/TF-IDF matcher setup
        try:
            from bm25_tfidf.bm25_tfidf_matcher import BM25TFIDFMatcher
            corpus = list(job_desc.get("keywords", [])) + list(job_desc.get("responsibilities", [])) + list(job_desc.get("skills", []))
            self.bm25_matcher = BM25TFIDFMatcher(corpus) if corpus else None
        except Exception:
            self.bm25_matcher = None

    def _init_llm(self, llm_config):
        """Initialize LLM provider adapter based on config dict."""
        if not llm_config or not llm_config.get("provider"):
            return None
        provider_name = llm_config["provider"].lower()
        api_key = llm_config.get("api_key")
        # Map provider name to module/class
        provider_map = {
            "openai": ("src.llm_provider.openai_provider", "OpenAIProvider"),
            "ollama": ("src.llm_provider.ollama_provider", "OllamaProvider"),
            "anthropic": ("src.llm_provider.anthropic_provider", "AnthropicProvider"),
            "gemini": ("src.llm_provider.gemini_provider", "GeminiProvider"),
        }
        if provider_name not in provider_map:
            return None
        module_name, class_name = provider_map[provider_name]
        try:
            module = importlib.import_module(module_name)
            provider_cls = getattr(module, class_name)
            return provider_cls(api_key=api_key)
        except Exception as e:
            print(f"LLM provider load error: {e}")
            return None

    def score_resume(self, bullets=None, resume_data=None, llm_prompt=None, context=None):
        try:
            # Use parsed resume bullets if not provided
            if bullets is None and self.resume_struct:
                bullets = self.resume_struct["sections"].get("experience", [])
            if resume_data is None and self.resume_struct:
                resume_data = {
                    "education": self.resume_struct["sections"].get("education", ""),
                    "certifications": self.resume_struct["sections"].get("certifications", ""),
                    "years_experience": self._extract_years_experience(self.resume_struct["raw_text"])
                }
            heuristic_result = self.heuristic.score_resume(bullets, resume_data, context=context)
            ml_result = self.ml.score_resume(resume_data)
            llm_result = None
            resp_sem_sims = [b.get("resp_sem_sim", 0.0) for b in heuristic_result.get("bullets", [])]
            skill_sem_sims = [b.get("skill_sem_sim", 0.0) for b in heuristic_result.get("bullets", [])]
            avg_resp_sem_sim = round(sum(resp_sem_sims) / max(1, len(resp_sem_sims)), 3)
            avg_skill_sem_sim = round(sum(skill_sem_sims) / max(1, len(skill_sem_sims)), 3)
            bm25_scores = []
            if self.bm25_matcher and bullets:
                for bullet in bullets:
                    try:
                        bm25_scores.append(self.bm25_matcher.score(bullet))
                    except Exception:
                        bm25_scores.append(None)
            import numpy as np
            def _agg_bm25(scores, key):
                vals = [s[key] for s in scores if s and key in s]
                return round(float(np.mean(vals)), 4) if vals else None
            bm25_tfidf_agg = {
                "tfidf_max": _agg_bm25(bm25_scores, "tfidf_max"),
                "tfidf_mean": _agg_bm25(bm25_scores, "tfidf_mean"),
                "bm25_max": _agg_bm25(bm25_scores, "bm25_max"),
                "bm25_mean": _agg_bm25(bm25_scores, "bm25_mean")
            } if bm25_scores else None
            if self.llm and llm_prompt:
                llm_result = self.llm.get_signals(llm_prompt)

            # Feedback generator integration
            from enrichment.resume_feedback_generator import ResumeFeedbackGenerator
            feedback_generator = ResumeFeedbackGenerator(llm_provider=self.llm)
            feedback = feedback_generator.generate_feedback(
                job_desc=self.heuristic.job_desc,
                resume_meta=resume_data,
                scoring_result=heuristic_result,
                context=context
            )
            return {
                "heuristic": heuristic_result,
                "ml": ml_result,
                "llm": llm_result,
                "bm25_tfidf": bm25_tfidf_agg,
                "aggregate": self._aggregate_results(heuristic_result, ml_result, llm_result, avg_resp_sem_sim, avg_skill_sem_sim, bm25_tfidf_agg),
                "feedback": feedback
            }
        except Exception as e:
            handle_error(e, context={'component': 'enrichment', 'method': 'score_resume'})
            return None
        # BM25/TF-IDF aggregate scores
        bm25_scores = []
        if self.bm25_matcher and bullets:
            for bullet in bullets:
                try:
                    bm25_scores.append(self.bm25_matcher.score(bullet))
                except Exception:
                    bm25_scores.append(None)
        # Aggregate BM25/TF-IDF scores
        def _agg_bm25(scores, key):
            vals = [s[key] for s in scores if s and key in s]
            return round(float(np.mean(vals)), 4) if vals else None
        import numpy as np
        bm25_tfidf_agg = {
            "tfidf_max": _agg_bm25(bm25_scores, "tfidf_max"),
            "tfidf_mean": _agg_bm25(bm25_scores, "tfidf_mean"),
            "bm25_max": _agg_bm25(bm25_scores, "bm25_max"),
            "bm25_mean": _agg_bm25(bm25_scores, "bm25_mean")
        } if bm25_scores else None
        if self.llm and llm_prompt:
            llm_result = self.llm.get_signals(llm_prompt)
        return {
            "heuristic": heuristic_result,
            "ml": ml_result,
            "llm": llm_result,
            "bm25_tfidf": bm25_tfidf_agg,
            "aggregate": self._aggregate_results(heuristic_result, ml_result, llm_result, avg_resp_sem_sim, avg_skill_sem_sim, bm25_tfidf_agg)
        }

    def _extract_years_experience(self, text):
        import re
        match = re.search(r"(\d+)\+? years?", text, re.I)
        if match:
            return int(match.group(1))
        return 0

    def _aggregate_results(self, heuristic_result, ml_result, llm_result=None, avg_resp_sem_sim=None, avg_skill_sem_sim=None, bm25_tfidf_agg=None):
        # Aggregate: combine likelihood, categories, rationales, semantic similarity, and BM25/TF-IDF
        likelihood = ml_result.get("likelihood_to_pass", 0.0)
        category = heuristic_result.get("category", "Unknown")
        rationale = f"Heuristic: {category}. ML: {ml_result.get('rationale', '')}"
        if llm_result:
            rationale += f" LLM: {llm_result.get('response', llm_result)}"
        rationale += f" | Avg Resp Semantic Sim: {avg_resp_sem_sim} | Avg Skill Semantic Sim: {avg_skill_sem_sim}"
        if bm25_tfidf_agg:
            rationale += f" | BM25/TFIDF: {bm25_tfidf_agg}"
        return {
            "likelihood_to_pass": likelihood,
            "heuristic_category": category,
            "avg_resp_sem_sim": avg_resp_sem_sim,
            "avg_skill_sem_sim": avg_skill_sem_sim,
            "bm25_tfidf": bm25_tfidf_agg,
            "rationale": rationale
        }

# Example usage:
# orchestrator = ResumeScoringOrchestrator(job_desc)
# result = orchestrator.score_resume(bullets, resume_data)
