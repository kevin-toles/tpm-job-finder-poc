"""
Embeddings: Utility for semantic similarity between resume bullets and JD sections
Uses SentenceTransformers (e.g., all-MiniLM-L6-v2)
"""
from typing import List

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError as e:
    from error_handler.handler import handle_error
    handle_error(e, context={'component': 'embeddings', 'import': 'sentence_transformers'})
    SentenceTransformer = None
    util = None

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformer:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                from error_handler.handler import handle_error
                handle_error(e, context={'component': 'embeddings', 'method': '__init__', 'model_name': model_name})
                self.model = None
        else:
            self.model = None

    def get_embeddings(self, texts: List[str]):
        if not self.model:
            raise ImportError("sentence-transformers not installed")
        try:
            return self.model.encode(texts, convert_to_tensor=True)
        except Exception as e:
            from error_handler.handler import handle_error
            handle_error(e, context={'component': 'embeddings', 'method': 'get_embeddings', 'texts': texts})
            return None

    def similarity(self, text_a: str, text_b: str) -> float:
        if not self.model:
            raise ImportError("sentence-transformers not installed")
        try:
            emb_a = self.model.encode([text_a], convert_to_tensor=True)
            emb_b = self.model.encode([text_b], convert_to_tensor=True)
            return float(util.pytorch_cos_sim(emb_a, emb_b)[0][0])
        except Exception as e:
            from error_handler.handler import handle_error
            handle_error(e, context={'component': 'embeddings', 'method': 'similarity', 'text_a': text_a, 'text_b': text_b})
            return 0.0

# Example usage:
# engine = EmbeddingEngine()
# sim = engine.similarity("Led agile teams", "lead projects")
